"""Bridge structures without the game: for named bridges, the decks and the steel the server builds around them
(roads.BridgeProfiles + bridgetypes), from the cached map data, DEM and sea, drawn as flat-shaded pictures (PIL
only: a side elevation and a three-quarter view). Writes <out>/<case>_look.png and <out>/look.json (per bridge: the
structures chosen, their source and span, the beam count, the time the structure took).

    python tools/bridge_look.py --out bridge_look [--only fremont,smithfield]
"""
import argparse
import json
import math
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "server"))
import bridge_profiles as bpf  # noqa: E402
import bridgetypes  # noqa: E402
import dem as demmod  # noqa: E402
import mapdata as mapdatamod  # noqa: E402

# key: (title, lat, lon, name words, half size of the picture's box m)
LOOK = {
    "fremont": ("Fremont Bridge", 45.5383, -122.6835, ["fremont"], 450),
    "steel": ("Steel Bridge", 45.5277, -122.6697, ["steel"], 250),
    "broadway": ("Broadway Bridge", 45.5322, -122.6738, ["broadway"], 300),
    "burnside": ("Burnside Bridge", 45.5230, -122.6678, ["burnside"], 250),
    "morrison": ("Morrison Bridge", 45.5176, -122.6697, ["morrison"], 300),
    "hawthorne": ("Hawthorne Bridge", 45.5133, -122.6716, ["hawthorne"], 280),
    "fortpitt": ("Fort Pitt Bridge", 40.4392, -80.0086, ["fort pitt bridge", "interstate 376", "i-376", "parkway"], 300),
    "smithfield": ("Smithfield Street Bridge", 40.4352, -80.0015, ["smithfield"], 250),
    "stjohns": ("St. Johns Bridge", 45.5848, -122.7647, ["st. johns", "st johns", "saint johns"], 650),
}
TYPE_NAMES = {9: "deck truss", 10: "through truss", 11: "deck arch", 12: "through arch", 13: "suspension",
              14: "cable-stayed", 15: "lift", 16: "bascule", 17: "swing", 111: "arch (over or under)", 2: "girder"}
PAINT_RGB = {k: v for k, v in bridgetypes.PAINTS.items()}


def box_quads(p, q, w, h):
    """The 4 long faces of a beam from p to q, w wide (across, horizontal) and h deep."""
    p, q = np.asarray(p, float), np.asarray(q, float)
    d = q - p
    L = float(np.linalg.norm(d)) or 1e-9
    d /= L
    up = np.array([0.0, 0.0, 1.0])
    a = np.cross(d, up)
    if np.linalg.norm(a) < 1e-6:
        a = np.array([1.0, 0.0, 0.0])
    a /= np.linalg.norm(a)
    b = np.cross(a, d)
    c = [(-1, -1), (1, -1), (1, 1), (-1, 1)]
    out = []
    for i in range(4):
        (u0, v0), (u1, v1) = c[i], c[(i + 1) % 4]
        o0 = a * u0 * w / 2 + b * v0 * h / 2
        o1 = a * u1 * w / 2 + b * v1 * h / 2
        out.append([p + o0, p + o1, q + o1, q + o0])
    return out


def deck_quads(xy, z, width):
    xy, z = np.asarray(xy, float), np.asarray(z, float)
    t = np.gradient(xy, axis=0)
    t /= np.maximum(np.hypot(*t.T), 1e-9)[:, None]
    n = np.c_[-t[:, 1], t[:, 0]] * width / 2
    L, R = xy + n, xy - n
    out = []
    for i in range(len(xy) - 1):
        top = [np.r_[L[i], z[i]], np.r_[R[i], z[i]], np.r_[R[i + 1], z[i + 1]], np.r_[L[i + 1], z[i + 1]]]
        out.append(top)
        for E in (L, R):            # the slab's sides, 1.2 m deep
            out.append([np.r_[E[i], z[i]], np.r_[E[i + 1], z[i + 1]], np.r_[E[i + 1], z[i + 1] - 1.2],
                        np.r_[E[i], z[i] - 1.2]])
    return out


def render(path, title, quads, axis, centre, size=(1500, 620)):
    """Two views side by side above each other: elevation (looking square to axis) and a 3/4 view."""
    from PIL import Image, ImageDraw
    W, H = size
    img = Image.new("RGB", (W, 2 * H), (236, 240, 244))
    dr = ImageDraw.Draw(img)
    ax = np.r_[axis / max(np.linalg.norm(axis), 1e-9), 0.0]
    side = np.cross([0, 0, 1.0], ax)
    sun = np.array([0.4, -0.5, 0.75])
    sun /= np.linalg.norm(sun)
    views = [("elevation", -side), ("three-quarter", -(side * math.cos(0.6) + ax * math.sin(0.6)) * 0.85
                                    + np.array([0, 0, 0.5]))]
    allp = np.concatenate([np.asarray(qd[0], float) for qd in quads]) if quads else np.zeros((1, 3))
    for vi, (name, look) in enumerate(views):
        look = np.asarray(look, float)
        look /= np.linalg.norm(look)
        right = np.cross(look, [0, 0, 1.0])
        right /= max(np.linalg.norm(right), 1e-9)
        upv = np.cross(right, look)
        pts = allp - centre
        u, v = pts @ right, pts @ upv
        if len(u) < 2:
            continue
        lo_u, hi_u, lo_v, hi_v = np.percentile(u, 0.5), np.percentile(u, 99.5), v.min(), v.max()
        sc = min((W - 60) / max(hi_u - lo_u, 1), (H - 80) / max(hi_v - lo_v, 1))
        ox, oy = 30 - lo_u * sc, vi * H + H - 30 + lo_v * sc

        def P(p):
            p = np.asarray(p) - centre
            return (ox + float(p @ right) * sc, oy - float(p @ upv) * sc)
        order = sorted(range(len(quads)), key=lambda i: -float((np.mean(quads[i][0], 0) - centre) @ look))
        for i in order:
            qd, col = quads[i]
            qd = np.asarray(qd, float)
            nrm = np.cross(qd[1] - qd[0], qd[3] - qd[0])
            nl = np.linalg.norm(nrm)
            sh = 0.55 + 0.45 * abs(float(nrm @ sun) / nl) if nl > 1e-9 else 0.7
            c = tuple(int(min(255, x * sh)) for x in col)
            dr.polygon([P(p) for p in qd], fill=c, outline=tuple(int(x * 0.7) for x in c))
        dr.text((12, vi * H + 8), f"{title}: {name}", fill=(20, 20, 20))
    img.save(path)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--cache-dir", default=os.path.join(os.path.expanduser("~"), ".cache", "beamng-earth"))
    ap.add_argument("--only", default="")
    ap.add_argument("--mode", default="curve")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    md = mapdatamod.MapData(a.cache_dir)
    dem = demmod.Dem(os.path.join(a.cache_dir, "dem"))
    rec = {}
    timing = []
    orig_struct = bridgetypes.chain_structures

    def spy(frame, parts, wet_fn=None, infra=()):
        got = orig_struct(frame, parts, wet_fn, infra)
        for g in got:
            spy.seen.append({k: (v if not isinstance(v, (np.ndarray, list)) else "outline") for k, v in g.items()})
        return got
    spy.seen = []
    bridgetypes.chain_structures = spy
    import roads
    orig_s = roads.BridgeProfiles._structure

    def timed(self, chain):
        t0 = time.perf_counter()
        r = orig_s(self, chain)
        timing.append((time.perf_counter() - t0, len(chain), len(r[0])))
        return r
    roads.BridgeProfiles._structure = timed
    for key, (title, lat, lon, words, half) in LOOK.items():
        if a.only and key not in a.only.split(","):
            continue
        spy.seen = []
        timing.clear()
        if key not in bpf.CASES:
            bpf.CASES[key] = (title, lat, lon, words, dict(deck_m=None, src="", art=""))
        t0 = time.perf_counter()
        parts, names, bp, frame = bpf.run_case(key, md, dem, a.cache_dir, a.mode)
        t_all = time.perf_counter() - t0
        every = [(k[0], v[0], v[1], v[2], v[3]) for k, v in bp.done.items()]
        got = bpf.pick(every, names, words, over_water=True, ground=bp._ground)
        if got is None:
            print(key, "no bridge")
            continue
        _, (fid, spec, xy, z, _), nm, cls = got
        c2 = np.zeros(2)                        # (the frame is centred on the case's point)
        axis = np.asarray(xy[-1], float) - np.asarray(xy[0], float)
        box = (c2[0] - half, c2[1] - half, c2[0] + half, c2[1] + half)
        quads = []
        gz = []
        for k, (sp, pxy, pz, _) in bp.done.items():
            pxy = np.asarray(pxy, float)
            m = (pxy[:, 0] > box[0]) & (pxy[:, 0] < box[2]) & (pxy[:, 1] > box[1]) & (pxy[:, 1] < box[3])
            if m.sum() < 2:
                continue
            idx = np.flatnonzero(m)
            sel = slice(idx[0], idx[-1] + 1)
            for qd in deck_quads(pxy[sel], np.asarray(pz, float)[sel], sp.width):
                quads.append((qd, (175, 172, 165)))
            gz.append(bp._ground(pxy[sel]))
        beams = bp.beams_in(box)
        for b in beams:
            col = PAINT_RGB.get(b[4] if len(b) > 4 else "grey", (150, 152, 150))
            for qd in box_quads(b[0], b[1], b[2], b[3]):
                quads.append((qd, col))
        for pr in bp.piers_in(box):
            x, y = pr[0], pr[1]
            ztop, zbot = pr[4], pr[5]
            if not (np.isfinite(ztop) and np.isfinite(zbot)):
                continue
            for qd in box_quads((x, y, zbot), (x, y, ztop), 2.0, 2.0):
                quads.append((qd, (140, 138, 132)))
        # water / ground line under the picked deck
        g = bp._ground(np.asarray(xy, float))
        wl = float(max(np.min(g), 0.0 if np.min(g) < 1.0 else np.min(g)))
        pts = np.asarray(xy, float)
        t = axis / max(np.linalg.norm(axis), 1e-9)
        n = np.array([-t[1], t[0]]) * 40
        quads.append(([np.r_[pts[0] - n, wl], np.r_[pts[-1] - n, wl], np.r_[pts[-1] + n, wl], np.r_[pts[0] + n, wl]],
                      (120, 150, 175)))
        centre = np.r_[c2, float(np.median(z))]
        out_png = os.path.join(a.out, f"{key}_look.png")
        render(out_png, f"{title} [{nm} / {cls}]", quads, axis, centre)
        st = [dict(type=s.get("type"), kind=TYPE_NAMES.get(s.get("type"), str(s.get("type"))), src=s.get("src"),
                   span=round(float(s.get("span") or 0), 1), paint=s.get("paint"), spans=s.get("spans"),
                   shape=s.get("shape")) for s in spy.seen]
        rec[key] = dict(title=title, picked=nm, structures=st, beams_in_view=len(beams),
                        deck_max_m=round(float(np.max(z)) - wl, 1),
                        structure_s=[round(t_[0], 3) for t_ in timing], case_s=round(t_all, 2))
        print(key, json.dumps(rec[key]), flush=True)
    with open(os.path.join(a.out, "look.json"), "w", encoding="utf-8") as f:
        json.dump(rec, f, indent=1, default=str)
    md.close()


if __name__ == "__main__":
    main()
