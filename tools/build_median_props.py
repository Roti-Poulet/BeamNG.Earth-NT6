"""build_median_props.py: the median cable barrier (mod/.../art/shapes/beamngEarth/bne_cable_barrier.dae and
median_props.materials.json): the stock maps have none (2026-10-28; server medians.py puts it in grass medians).

    python3 tools/build_median_props.py

One 3 m module along X (-1.5 .. 1.5, the guard rails' module length: trees.lua's rows place it like Italy's rail), Z
up from the ground at its origin: a galvanised I-section post at its middle (sunk 0.3 m, a white reflector band near
its top) and four steel ropes the module's length (high-tension cable barriers: four ropes 0.48-0.96 m up, posts
about every 3 m). Two levels of detail (the far one the posts and ropes as single quads) and a collision box the
ropes' height.
"""
import json
import os
import uuid

from build_rail_crossing_props import OUT, Mesh, write_dae

ROPES = (0.48, 0.64, 0.80, 0.96)    # m up
ROPE_R = 0.011                       # m: a 3/4 in rope
POST_H = 1.05
POST_SINK = 0.3
HALF_L = 1.5
COLOURS = {
    "bne_cable_steel": ((0.58, 0.59, 0.60), 0.85, 0.5),      # galvanised
    "bne_cable_reflector": ((0.92, 0.92, 0.90), 0.0, 0.3),   # its white reflective band
}


def module(detail=True):
    m = Mesh(6)
    if detail:
        # an I-section post: two flanges and a web
        m.box("bne_cable_steel", (0.0, 0.0, (POST_H - POST_SINK) / 2), (0.004, 0.035, (POST_H + POST_SINK) / 2))
        for x in (-0.03, 0.03):
            m.box("bne_cable_steel", (x, 0.0, (POST_H - POST_SINK) / 2), (0.004, 0.04, (POST_H + POST_SINK) / 2))
        m.box("bne_cable_reflector", (0.0, 0.0, POST_H - 0.12), (0.036, 0.042, 0.05))
        for z in ROPES:     # ropes as square tubes (four faces, ends left open: the next module goes on)
            for a, b in (((-1, -1), (-1, 1)), ((-1, 1), (1, 1)), ((1, 1), (1, -1)), ((1, -1), (-1, -1))):
                y0, z0 = a[0] * ROPE_R, z + a[1] * ROPE_R
                y1, z1 = b[0] * ROPE_R, z + b[1] * ROPE_R
                m.face("bne_cable_steel", [(-HALF_L, y0, z0), (HALF_L, y0, z0), (HALF_L, y1, z1), (-HALF_L, y1, z1)])
                m.face("bne_cable_steel", [(-HALF_L, y1, z1), (HALF_L, y1, z1), (HALF_L, y0, z0), (-HALF_L, y0, z0)])
    else:
        # far: the post a slab, each rope a thin vertical strip seen from either side
        m.box("bne_cable_steel", (0.0, 0.0, (POST_H - POST_SINK) / 2), (0.03, 0.035, (POST_H + POST_SINK) / 2))
        for z in ROPES:
            for side in (1, -1):
                pts = [(-HALF_L, 0.0, z - 0.015), (HALF_L, 0.0, z - 0.015), (HALF_L, 0.0, z + 0.015),
                       (-HALF_L, 0.0, z + 0.015)]
                m.face("bne_cable_steel", pts if side > 0 else list(reversed(pts)))
    return m


def collision():
    """What a car hits: a box the ropes' length and height."""
    m = Mesh(4)
    m.box("bne_cable_steel", (0.0, 0.0, (ROPES[-1] + 0.05) / 2), (HALF_L, 0.05, (ROPES[-1] + 0.05) / 2))
    return m


def materials():
    out = {}
    pid = lambda n: str(uuid.uuid5(uuid.NAMESPACE_URL, "beamng-earth/" + n))
    for k, (col, met, rough) in COLOURS.items():
        out[k] = {"name": k, "mapTo": k, "class": "Material", "version": 1.5, "persistentId": pid(k),
                  "Stages": [{"baseColorFactor": [*col, 1.0], "metallicFactor": met, "roughnessFactor": rough},
                             {}, {}, {}]}
    with open(os.path.join(OUT, "median_props.materials.json"), "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=2)


def main():
    materials()
    path = os.path.join(OUT, "bne_cable_barrier.dae")
    lods = [(48, module(True)), (6, module(False))]
    write_dae(path, "bne_cable_barrier", lods, collision())
    print(path, os.path.getsize(path), "bytes", sum(len(t) for t in lods[0][1].tri.values()), "triangles")


if __name__ == "__main__":
    main()
