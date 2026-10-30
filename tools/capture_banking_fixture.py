"""Capture the I-80 curve replay from existing input caches; never fetch or modify caches."""
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "server"))
import dem
import geodesy
import mapgeom
import roads

LAT, LON = 41.41135, -105.83960
IDS = ("9299f3ec-adca-483a-ba31-485fa458b837", "9de188ec-c521-4d65-b268-f203e7ade93f")


def main():
    cache = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.home() / ".cache/beamng-earth"
    source = cache / "mapdata/v2/overture/2026-09-23.1/roads.6/14/3374/6116.npz"
    with np.load(source, allow_pickle=False) as archive:
        f = mapgeom.Features.from_arrays("roads", {k: archive[k] for k in archive.files}, "")
        provenance = str(archive["provenance"])
    specs = roads.road_specs(f)
    data = {"origin": np.array([LAT, LON]), "road_ids": np.array(IDS), "provenance": np.array(provenance)}
    for k, fid in enumerate(IDS):
        i = list(f.ids).index(fid)
        data[f"road{k}"] = roads.ground_parts(f, i)[0]
        data[f"spec{k}"] = np.array(json.dumps(specs[i]._asdict(), default=lambda v: v.item()))

    # Use Dem.sample's actual bilinear sampler, with read-only decoded tiles.
    # Bypass its constructor/loaders so no executor, download or cache write occurs.
    sampler = dem.Dem.__new__(dem.Dem)

    def tiles(keys, progress=None):
        return {key: np.load(cache / "dem/decoded/v2/g1" / str(key[0]) / str(key[1]) / f"{key[2]}.npy",
                             mmap_mode="r", allow_pickle=False) for key in keys}

    sampler.tiles = tiles
    frame = geodesy.EnuFrame(LAT, LON, 0.)
    axis = np.arange(-1200., 1201., 8.)
    x, y = np.meshgrid(axis, axis)
    la, lo, _ = frame.enu_to_geodetic(x, y, 0.)
    data["dem_x"], data["dem_y"] = axis, axis
    data["dem_height"] = sampler.sample(la, lo, 16).astype(np.float32)
    output = ROOT / "server/tests/fixtures/i80_wyoming_banking.npz"
    np.savez_compressed(output, **data)
    print(f"Captured {len(IDS)} real road polylines and {x.size} raw DEM samples: {output}")


if __name__ == "__main__":
    main()
