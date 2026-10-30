"""build_lane_tags.py PLANET OUT_DIR: OpenStreetMap's lane-level road tags (turn:lanes, change:lanes, placement,
lanes:forward / backward, overtaking, ...) as small gzip JSON shards the server reads per area (server/lanetags.py),
for the road markings (the user, 2026-10-28: "look at how some maps get detailed lane by lane data"; research:
docs/research/2026-10-28-road-markings-standards.md §5). OSM US's Layercake highways file, which osmtags.py reads, has
`lanes` but none of these.

    python3 tools/build_lane_tags.py planet-latest.osm.pbf out/
    python3 tools/build_lane_tags.py https://.../planet-YYMMDD.osm.pbf out/     (streamed twice by curl: no disk)

Shards: <OUT_DIR>/<x>/<y>.json.gz per z7 tile (build_rail_tags.SHARD_ZOOM), {"ways": {way id: tags}} (highway ways
with any of LANE_KEYS; their tags in TAGS), and <OUT_DIR>/manifest.json. A way is placed by its first, middle and last
nodes (enough for a way: they are short), so the second pass looks up three nodes a way instead of all of them.
Data: (c) OpenStreetMap contributors, ODbL 1.0.
"""
import argparse
import os
import sys
import time

import numpy as np
import osmium

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_rail_tags as rail  # noqa: E402

LANE_KEYS = ("turn:lanes", "turn:lanes:forward", "turn:lanes:backward", "turn:lanes:both_ways",
             "change:lanes", "change:lanes:forward", "change:lanes:backward",
             "placement", "placement:forward", "placement:backward",
             "lanes:forward", "lanes:backward", "lanes:both_ways",
             "overtaking", "overtaking:forward", "overtaking:backward", "divider", "lane_markings",
             "width:lanes", "width:lanes:forward", "width:lanes:backward",
             "bus:lanes", "bus:lanes:forward", "bus:lanes:backward", "psv:lanes", "busway", "busway:left",
             "busway:right", "busway:both", "hov:lanes", "cycleway:lanes", "access:lanes")
TAGS = LANE_KEYS + ("highway", "lanes", "oneway", "junction")
# roundabout rings too, lane tags or not (roads._rings: their circulatory width; Layercake's highways file has no
# junction column)
RINGS = ("roundabout", "circular")


def first_pass(src):
    """[(id, tags dict, (first, middle, last) node refs)] of the highway ways with a lane key."""
    with rail._Source(src) as f:
        ways, t0, k = [], time.time(), 0
        fp = osmium.FileProcessor(f, osmium.osm.WAY).with_filter(osmium.filter.KeyFilter(*LANE_KEYS, "junction"))
        for o in fp:
            k += 1
            if k % 500_000 == 0:
                print(f"  pass 1: {k:,} ways, {len(ways):,} kept, {time.time() - t0:.0f} s", flush=True)
            tags = o.tags
            if "highway" not in tags or len(o.nodes) < 2:
                continue
            if tags.get("junction") not in RINGS and not any(k in tags for k in LANE_KEYS):
                continue                        # (a junction=yes / spui way without lane tags)
            refs = [n.ref for n in o.nodes]
            ways.append((o.id, {t: tags[t] for t in TAGS if t in tags},
                         np.array([refs[0], refs[len(refs) // 2], refs[-1]], np.int64)))
        return ways


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("planet", help="the planet (or an extract): a .osm.pbf path, an http(s) URL (streamed), '-'")
    ap.add_argument("out")
    ap.add_argument("--second-pass", help="the planet again for the second pass (a path, or '-' stdin: streaming)")
    a = ap.parse_args()
    t0 = time.time()
    ways = first_pass(a.planet)
    print(f"pass 1: {len(ways):,} ways, {time.time() - t0:.0f} s", flush=True)
    ids = np.unique(np.concatenate([r for _i, _t, r in ways])) if ways else np.zeros(0, np.int64)
    nid, nlon, nlat = rail.second_pass(a.second_pass or a.planet, ids)
    print(f"pass 2: {len(nid):,} node places, {time.time() - t0:.0f} s", flush=True)
    rail.write(a.out, ways, [], nid, nlon, nlat)
    print(f"done in {time.time() - t0:.0f} s")


if __name__ == "__main__":
    sys.exit(main())
