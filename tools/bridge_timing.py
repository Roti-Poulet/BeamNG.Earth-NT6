"""Time the bridge work per case without the game: BridgeProfiles' deck solve (roads) and the structures
(bridgetypes) for every chain the case's box touches, --bridge-profile legacy vs curve, each run twice (the second,
with the map data warm, is reported). Prints JSON per case and the totals.

    python tools/bridge_timing.py [--only fremont,steel] [--look]   (--look: tools/bridge_look.py's cases)
"""
import argparse
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "server"))
import bridge_profiles as bpf  # noqa: E402
import dem as demmod  # noqa: E402
import mapdata as mapdatamod  # noqa: E402
import roads  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cache-dir", default=os.path.join(os.path.expanduser("~"), ".cache", "beamng-earth"))
    ap.add_argument("--only", default="")
    a = ap.parse_args()
    md = mapdatamod.MapData(a.cache_dir)
    dem = demmod.Dem(os.path.join(a.cache_dir, "dem"))
    acc = {"solve": 0.0, "structure": 0.0}
    o_solve, o_struct = roads.BridgeProfiles._solve, roads.BridgeProfiles._structure

    def solve(self, *x):
        t0 = time.perf_counter()
        try:
            return o_solve(self, *x)
        finally:
            acc["solve"] += time.perf_counter() - t0

    def struct(self, *x):
        t0 = time.perf_counter()
        try:
            return o_struct(self, *x)
        finally:
            acc["structure"] += time.perf_counter() - t0
    roads.BridgeProfiles._solve, roads.BridgeProfiles._structure = solve, struct
    tot = {}
    for key in [k for k in bpf.CASES if not a.only or k in a.only.split(",")]:
        row = {}
        for mode in ("legacy", "curve"):
            for rep in range(2):
                acc.update(solve=0.0, structure=0.0)
                t0 = time.perf_counter()
                bpf.run_case(key, md, dem, a.cache_dir, mode)
                wall = time.perf_counter() - t0
            row[mode] = {"wall_s": round(wall, 3), "solve_s": round(acc["solve"], 3),
                         "structure_s": round(acc["structure"], 3)}
            for k, v in row[mode].items():
                tot.setdefault(mode, {}).setdefault(k, 0.0)
                tot[mode][k] = round(tot[mode][k] + v, 3)
        print(key, json.dumps(row), flush=True)
    print("TOTAL", json.dumps(tot))
    md.close()


if __name__ == "__main__":
    main()
