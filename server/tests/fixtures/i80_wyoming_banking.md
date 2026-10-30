# I-80 banking replay inputs

Location: 41.41135, -105.83960, Wyoming. Captured on 2026-10-28 from existing local input caches;
no solved road/revisit/plan cache is used by this fixture or its tests.

`i80_wyoming_banking.npz` contains both real motorway carriageway polylines from Overture release
2026-09-23.1, mapdata v2 roads.6, cached cell 14/3374/6116. The reported point itself is in cell
14/3375/6117; these full features span multiple cells. IDs:

* `9299f3ec-adca-483a-ba31-485fa458b837`
* `9de188ec-c521-4d65-b268-f203e7ade93f`

The archive includes the joined road specifications and the input cell's provenance JSON.
Road geometry attribution: OpenStreetMap contributors and Overture Maps Foundation, ODbL-1.0;
see the project's CREDITS.md. Original vertices are preserved, including sparse long chords and
short geometry irregularities. They are not replaced with a fitted circular curve.

`dem_height` is a 301 x 301 float32 raster sampled every 8 m in the location's ENU frame over
[-1200, 1200] m on both axes. Values are raw geodetic elevations returned by `dem.Dem.sample`
at zoom 16 from read-only decoded v2/g1 input tiles, before road grading or banking. The test
bilinearly interpolates this captured raster and fails outside its bounds. It approximates the
local DEM at 8 m resolution; it does not claim to preserve every sub-8 m DEM detail. This keeps
real hills while isolating banking on the exact road geometry, and is adequate for the
bank-on/bank-off comparison using identical terrain inputs.

Terrain source: the project's Mapterhorn/fallback/ground-filter DEM pipeline (server/dem.py,
SOURCES.md and CREDITS.md). All tests are offline. Recreate from the same available input caches:

```text
python tools/capture_banking_fixture.py [cache-directory]
```

The capture tool does not download data or modify the input cache. Missing inputs fail explicitly.
