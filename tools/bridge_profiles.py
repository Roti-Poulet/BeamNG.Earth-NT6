"""Bridge deck profiles without the game: for 24 named bridges (Portland / Vancouver WA and US landmarks), the
deck heights the server builds with --bridge-profile legacy and curve, from the cached (or fetched) map data, DEM
and sea, scored against published heights. Writes <out>/<case>.json, <out>/<case>_profile.png, <out>/summary.json.

    python tools/bridge_profiles.py --out bridge_profiles [--only fremont,marquam]
"""
import argparse
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "server"))
import dem as demmod  # noqa: E402
import geodesy  # noqa: E402
import mapcells  # noqa: E402
import mapdata as mapdatamod  # noqa: E402
import roads  # noqa: E402


# key: (title, lat, lon, name words (any), reference) reference: deck_m = road surface over the water (or the
# road under), src: where that number is from; art: the structure a reference names
CASES = {
    # Portland / Vancouver (references: deck over the water = clearance from Wikipedia + the structure under the road)
    "interstate": ("Interstate Bridge (I-5, Columbia)", 45.6175, -122.6757, ["interstate bridge"],
                   dict(deck_m=24, src="72 ft (21.9 m) under the hump span, +2 m",
                        art="movable")),
    "fremont": ("Fremont Bridge (I-405)", 45.5383, -122.6835, ["fremont"],
                dict(deck_m=57, src="clearance 175 ft (53 m) + structure", art="arch")),
    "marquam": ("Marquam Bridge (I-5)", 45.5065, -122.6693, ["marquam"],
                dict(deck_m=43, src="clearance 130 ft (40 m) + structure", art="beam")),
    "glennjackson": ("Glenn L. Jackson Bridge (I-205)", 45.5925, -122.5475, ["glenn", "jackson"],
                     dict(deck_m=47, src="clearance 144 ft (43.9 m) + structure", art="beam")),
    "hawthorne": ("Hawthorne Bridge", 45.5133, -122.6716, ["hawthorne"],
                  dict(deck_m=17, src="49 ft (15 m) closed + 2 m", art="movable")),
    "morrison": ("Morrison Bridge", 45.5176, -122.6697, ["morrison"],
                 dict(deck_m=23, src="69 ft (21 m) + 2 m", art="movable")),
    "burnside": ("Burnside Bridge", 45.5230, -122.6678, ["burnside"],
                 dict(deck_m=22, src="64 ft (20 m) closed + 2 m", art="movable")),
    "steel": ("Steel Bridge", 45.5277, -122.6697, ["steel"],
              dict(deck_m=24, src="upper deck 72 ft (22 m) + 2 m", art="movable")),
    "broadway": ("Broadway Bridge", 45.5322, -122.6738, ["broadway"],
                 dict(deck_m=29, src="90 ft (27 m) closed + 2 m", art="movable")),
    "sellwood": ("Sellwood Bridge", 45.4645, -122.6630, ["sellwood"],
                 dict(deck_m=25, src="75 ft (23 m) + 2 m", art="arch")),
    "stjohns": ("St. Johns Bridge", 45.5848, -122.7647, ["st. johns", "st johns", "saint johns"],
                dict(deck_m=63, src="Wikipedia: clearance 205 ft (62 m)", art="suspension")),
    # overpasses (references: 5 m headroom + slab: 6 m over the road under)
    "i205_division": ("SE Division over I-205 SB ramp + MAX", 45.5047, -122.5652, ["division"],
                      dict(clear_m=6.0, src="rule: 5 m headroom + slab", art="beam")),
    "sw6th_i405": ("SW 6th Ave over I-405", 45.5086, -122.6831, ["6th", "5th"],
                   dict(clear_m=6.0, src="rule: 5 m headroom + slab", art="beam")),
    "taylor_i405": ("SW Taylor St over I-405", 45.5163, -122.6880, ["taylor"],
                    dict(clear_m=6.0, src="rule: 5 m headroom + slab", art="beam")),
    "vancouver_99": ("Vancouver WA: I-5 overpass at NE 78th St (Hwy 99 corridor)", 45.6786, -122.6646, ["99", "interstate 5", "i-5", "highway"],
                     dict(clear_m=6.0, src="rule: 5 m headroom + slab", art="beam")),
    # landmarks (published clearances: Wikipedia)
    "calcasieu": ("I-10 Calcasieu River Bridge, Lake Charles LA", 30.2370, -93.2428, ["calcasieu", "interstate 10", "i-10"],
                  dict(deck_m=43, src="Wikipedia: clearance 135 ft (41 m) + ~2 m", art="truss")),
    "skyway": ("Sunshine Skyway, Tampa Bay FL", 27.6235, -82.6553, ["skyway"],
               dict(deck_m=58, src="Wikipedia: clearance 180 ft (55 m) + ~3 m", art="cable-stayed")),
    "vincentthomas": ("Vincent Thomas Bridge, San Pedro CA", 33.7493, -118.2720, ["vincent thomas"],
                      dict(deck_m=58, src="Wikipedia: clearance 185 ft (56 m) + ~2 m", art="suspension")),
    "lbgateway": ("Long Beach International Gateway CA", 33.7648, -118.2213, ["gateway", "desmond"],
                  dict(deck_m=65, src="Wikipedia: clearance 205 ft (62 m) + ~3 m", art="cable-stayed")),
    "goldengate": ("Golden Gate Bridge, San Francisco", 37.8199, -122.4783, ["golden gate"],
                   dict(deck_m=69, src="Wikipedia: clearance 220 ft (67 m) + ~2 m", art="suspension")),
    "baybridge": ("SF-Oakland Bay Bridge (west span)", 37.7920, -122.3780, ["bay bridge", "interstate 80", "i-80"],
                  dict(deck_m=60, src="Wikipedia: west span clearance ~191 ft (58 m) + ~2 m", art="suspension")),
    "coronado": ("San Diego-Coronado Bridge", 32.6890, -117.1535, ["coronado"],
                 dict(deck_m=63, src="Wikipedia: clearance 200 ft (61 m) + ~2 m", art="beam")),
    "crescentcity": ("Crescent City Connection, New Orleans", 29.9383, -90.0570, ["crescent city", "westbank", "mississippi river bridge"],
                     dict(deck_m=48, src="Wikipedia: clearance ~150 ft (46 m) + ~2 m", art="truss")),
    "smithfield": ("Smithfield Street Bridge, Pittsburgh (lenticular)", 40.4352, -80.0015, ["smithfield"],
                   dict(deck_m=None, src="no published clearance found offline; NBI if matched", art="truss")),
}


BOX = {"vancouver_99": 400.0, "lbgateway": 400.0, "crescentcity": 300.0}     # m around the point searched


def cell_fn_of(md):
    return lambda key: md.cell(key, layers=("roads",), kind="demand").layers.get("roads")


def run_case(key, md, dem, cache, mode):
    title, lat, lon, words, ref = CASES[key]
    os.environ["BNE_BRIDGE_PROFILE"] = mode
    if mode == "curve":
        os.environ["BNE_CACHE_DIR"] = cache
    else:
        os.environ.pop("BNE_CACHE_DIR", None)
    frame = geodesy.EnuFrame(lat, lon, 0.0)
    zoom = min(demmod.zoom_for(lat, 2.5), demmod.MAX_ZOOM)

    global _SEA
    if "_SEA" not in globals():
        import seacarve
        _SEA = seacarve.SeaCarver(md, cache)

    def elev(la, lo):
        return _SEA.carve(la, lo, dem.sample(la, lo, zoom))
    bp = roads.BridgeProfiles(frame, cell_fn_of(md), elev)
    bp.wet = _SEA.depth
    bp.infra_fn = lambda key: md.cell(key, layers=("infrastructure",), kind="demand").layers.get("infrastructure")
    la0, lo0, la1, lo1 = lat - 0.004, lon - 0.006, lat + 0.004, lon + 0.006
    cells = [md.cell(k, layers=("roads",), kind="demand").layers.get("roads")
             for k in mapcells.cells_for_bbox(la0, lo0, la1, lo1)]
    names = {}
    for f in cells:
        if f is None:
            continue
        for i in range(len(f)):
            names[str(f.ids[i])] = (str(f.attrs["name"][i]) if "name" in f.attrs else "",
                                    str(f.attrs["class"][i]) if "class" in f.attrs else "")
    r = BOX.get(key, 80.0)
    parts = bp.parts(cells, (-r, -r, r, r))
    for k, v in bp.done.items():                # parts of the chains beyond these cells
        if k[0] not in names:
            names[k[0]] = ("", v[0].cls)
    return parts, names, bp, frame


def pick(parts, names, words, over_water=False, ground=None):
    """The part to plot: name-matched near the point first, then (a water crossing) the one standing
    highest over the lowest ground under it, else the major road nearest the point."""
    rank = {"motorway": 0, "trunk": 1, "primary": 2, "secondary": 3, "tertiary": 4}
    best = None
    for fid, spec, xy, z, lon in parts:
        if not np.isfinite(z).all():
            continue
        nm, cls = names.get(fid, ("", ""))
        hit = any(w in nm.lower() for w in words)
        d = float(np.min(np.hypot(xy[:, 0], xy[:, 1])))
        L = float(np.sum(np.hypot(*np.diff(xy, axis=0).T)))
        if over_water:
            lo = float(np.min(ground(np.asarray(xy, np.float64)[:, :2]))) if ground is not None else 0.0
            score = (0 if hit else 1, -round(float(np.max(z)) - lo), d)
        else:
            score = (0 if hit else 1, rank.get(cls, 9), round(d / 40.0), -L)
        if best is None or score < best[0]:
            best = (score, (fid, spec, xy, z, lon), nm, cls)
    return best


def metrics(xy, z, g):
    s = np.r_[0.0, np.cumsum(np.hypot(*np.diff(xy, axis=0).T))]
    keep = np.r_[0, 1 + np.flatnonzero(np.diff(s) >= 1.0)]     # points under 1 m apart (a part's last stub) skipped
    if keep[-1] != len(s) - 1:
        keep[-1] = len(s) - 1
    ds = np.maximum(np.diff(s[keep]), 1e-6)
    gr = np.diff(z[keep]) / ds
    kink = np.abs(np.diff(gr)) if len(gr) > 1 else np.zeros(1)
    over = z - g
    flat = 0.0                              # longest stretch within 0.3 m of the lower abutment's height
    base = min(z[0], z[-1])
    run = 0.0
    for k in range(1, len(z)):
        if abs(z[k] - base) < 0.3 and abs(z[k - 1] - base) < 0.3:
            run += s[k] - s[k - 1]
            flat = max(flat, run)
        else:
            run = 0.0
    return dict(length_m=round(float(s[-1]), 1), crest_m=round(float(z.max()), 2),
                max_over_ground_m=round(float(over.max()), 2), min_ground_m=round(float(g.min()), 2),
                deck_over_lowest_ground_m=round(float(z.max() - g.min()), 2),
                max_grade_pct=round(float(np.max(np.abs(gr)) * 100), 2),
                max_kink_pct=round(float(np.max(kink) * 100), 2), flat_run_m=round(flat, 1)), s


def plot(path, title, s, g, z_old, z_new, ref_line=None):
    from PIL import Image, ImageDraw
    W, H, m = 1100, 420, 50
    allz = np.r_[g, z_old, z_new] if ref_line is None else np.r_[g, z_old, z_new, [ref_line]]
    zlo, zhi = float(allz.min()) - 2, float(allz.max()) + 4
    L = max(float(s[-1]), 1.0)
    im = Image.new("RGB", (W, H), (250, 250, 248))
    d = ImageDraw.Draw(im)

    def P(si, zi):
        return (m + (W - 2 * m) * si / L, H - m - (H - 2 * m) * (zi - zlo) / max(zhi - zlo, 1e-6))
    d.polygon([P(0, zlo)] + [P(a, b) for a, b in zip(s, g)] + [P(L, zlo)], fill=(205, 196, 176))
    if ref_line is not None:
        d.line([P(0, ref_line), P(L, ref_line)], fill=(120, 120, 120), width=1)
        d.text(P(0, ref_line), " reference deck", fill=(90, 90, 90))
    d.line([P(a, b) for a, b in zip(s, z_old)], fill=(200, 60, 40), width=3)
    d.line([P(a, b) for a, b in zip(s, z_new)], fill=(30, 90, 200), width=3)
    d.text((m, 10), title, fill=(0, 0, 0))
    d.text((m, 26), "red: before (legacy)   blue: after (curve)   tan: ground/water   "
                    f"length {L:.0f} m, heights {zlo:.0f}..{zhi:.0f} m (vertical exaggerated)", fill=(60, 60, 60))
    im.save(path)


KINK_MAX_PCT = 2.0      # grade change between deck points, at most


def verdict(r, tag):
    """True / False / None (no reference): a water bridge within max(5 m, 15 %) of its reference deck height, an
    overpass at least its clearance - 0.5 m over the lowest ground under it; either without a grade change over
    KINK_MAX_PCT between deck points."""
    if "error" in r:
        return None
    ref, m = r["reference"], r[tag]
    if m is None:
        return None
    smooth = m["max_kink_pct"] <= KINK_MAX_PCT
    if ref.get("deck_m"):
        return smooth and abs(r[f"deck_over_water_{tag}_m"] - ref["deck_m"]) <= max(5.0, 0.15 * ref["deck_m"])
    if ref.get("clear_m"):
        return smooth and m["deck_over_lowest_ground_m"] >= ref["clear_m"] - 0.5
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--cache-dir", default=os.path.join(os.path.expanduser("~"), ".cache", "beamng-earth"))
    ap.add_argument("--only", default="")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    md = mapdatamod.MapData(a.cache_dir)
    dem = demmod.Dem(os.path.join(a.cache_dir, "dem"))
    keys = [k for k in CASES if not a.only or k in a.only.split(",")]
    summary = {}
    for key in keys:
        title, lat, lon, words, ref = CASES[key]
        try:
            old_parts, names, old_bp, _ = run_case(key, md, dem, a.cache_dir, "legacy")
            new_parts, _, bp, frame = run_case(key, md, dem, a.cache_dir, "curve")
        except Exception as e:
            summary[key] = {"title": title, "error": f"{type(e).__name__}: {e}"}
            print(key, "ERROR", e, flush=True)
            continue
        # every part of every chain solved (a chain reaches past the search box: the main span of a long
        # crossing can lie outside it)
        every = [(k[0], v[0], v[1], v[2], v[3]) for k, v in bp.done.items()]
        got = pick(every, names, words, over_water=bool(ref.get("deck_m")), ground=bp._ground)
        if got is None:
            summary[key] = {"title": title, "error": "no bridge part found near the point"}
            print(key, "no bridge", flush=True)
            continue
        _, (fid, spec, xy, z_new, _), nm, cls = got
        z_old = next((z for f, _, x, z, _ in old_parts if f == fid and len(x) == len(xy) and np.allclose(x, xy)), None)
        if z_old is None:
            z_old = next((v[2] for k, v in old_bp.done.items() if k[0] == fid and len(v[1]) == len(xy)
                          and np.allclose(v[1], xy)), None)
        la, lo, _ = frame.enu_to_geodetic(xy[:, 0], xy[:, 1], 0.0)
        g = np.asarray(dem.sample(la, lo, min(demmod.zoom_for(lat, 2.5), demmod.MAX_ZOOM)), np.float64)
        g = frame.geodetic_to_enu(la, lo, g)[2]
        sea = frame.geodetic_to_enu(la, lo, np.zeros(len(la)))[2]
        water = max(float(g.min()), float(sea.max()))
        m_new, s = metrics(xy, z_new, g)
        m_old = metrics(xy, z_old, g)[0] if z_old is not None else None
        rec = {"title": title, "fid": fid, "name": nm, "class": cls, "water_or_low_m": round(water, 2),
               "lat": [round(float(v), 6) for v in la], "lon": [round(float(v), 6) for v in lo],
               "before": m_old, "after": m_new, "reference": ref,
               "deck_over_water_before_m": round(float(z_old.max()) - water, 1) if z_old is not None else None,
               "deck_over_water_after_m": round(float(z_new.max()) - water, 1)}
        summary[key] = rec
        with open(os.path.join(a.out, key + ".json"), "w", encoding="utf-8") as f:
            json.dump(dict(rec, s=[round(float(v), 1) for v in s], ground=[round(float(v), 2) for v in g],
                           z_before=None if z_old is None else [round(float(v), 2) for v in z_old],
                           z_after=[round(float(v), 2) for v in z_new]), f, indent=1)
        plot(os.path.join(a.out, key + "_profile.png"), f"{title}  [{nm or '?'} / {cls}]", s, g,
             z_old if z_old is not None else z_new, z_new,
             None if not ref.get("deck_m") else water + ref["deck_m"])
        print(key, nm, cls, "before", rec["deck_over_water_before_m"], "after", rec["deck_over_water_after_m"],
              flush=True)
    with open(os.path.join(a.out, "summary.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=1)
    for tag in ("before", "after"):
        got = [verdict(r, tag) for r in summary.values()]
        print(f"{tag}: {got.count(True)} pass, {got.count(False)} fail, {got.count(None)} without a reference")
    md.close()


if __name__ == "__main__":
    main()
