# Banking pulses at the Wyoming I-80 curve

## Root cause and version comparison

The curve at 41.41135, -105.83960 is represented by two sparse motorway polylines. Their median vertex spacings
are 113.77 m and 88.78 m. Sampling those polylines every 2 m adds points on their straight chords; it does not
recover the continuous curvature of the real highway.

Banking was introduced in [c6c29a5](https://github.com/TecnaGamer/BeamNG.Earth/commit/c6c29a5361a3d6ea9e764b23c86a3624c73372b3),
whose parent is [2f10e75](https://github.com/TecnaGamer/BeamNG.Earth/commit/2f10e753397eb9ef4468e63bf9df3bd1e9dbab14).
The parent `_plan` has the same longitudinal median/Gaussian smoothing and core-width construction but no banking.
The new native kernel estimates signed curvature from a circle through points only 12 m either side, converts it
to cross slope `e = 0.08 * min(1, r_min / R)`, suppresses values below 1%, and averages over an 18 m box window.
Here `r_min = v² / (127 * (0.08 + f))`; motorway design speed is 110 km/h, `f = 0.10`. The stored value is slope
(metres/metre), not an angle; the roll angle is `atan(e)`. Eight percent is about 4.57 degrees.

On the real sparse inputs, the 12 m stencil sees zero curvature within each long chord and excessive curvature
at its corners. Small map irregularities can even reverse its sign. The result is repeated zero-to-8% bank pulses,
not one gradual superelevation through the highway curve. At 70 mph, 89–114 m between vertices means about
2.8–3.6 seconds between such events. This matches the reported cadence. The reporter confirmed the correction
in-game at the supplied location; the quantitative measurements below come from the offline replay.

## Targeted correction

Only banking behavior changes in `server/grading.py`:

* Measure curvature over 100 m either side (a 200 m baseline), spanning the local source chords instead of treating
  their individual corners as tight turns.
* Use 100 m runoff and a separate 12 m Gaussian on the bank profile to remove sample-entry/exit steps from the
  discrete box average. This filters cross slope, not road elevation.
* Fade banking to level over 100 m at bridge abutments and unjoined ends, preserving exact zero at the endpoint.
* Request geometry context for the curvature stencil, half-runoff, and Gaussian support (188 m with these settings).
  Separate that extra geometry from the existing longitudinal DEM context, so bridge approach/underpass inputs
  and elevation smoothing remain unchanged.

Banking remains enabled, retains its design-speed rule and 8% cap, and remains directional. Natural hills and
the bridge-height/clearance solvers are preserved. Joined geometry supplies context before banking is trimmed
to each segment, avoiding artificial endpoint transitions.
The existing native kernels provide the calculation and filtering; no native rebuild is needed.

## Reproduction results

The offline replay uses the actual two source polylines plus captured local raw DEM elevations. It rebuilds
grading and geometry, bypassing generated plan/revisit caches. See the [fixture provenance](../server/tests/fixtures/i80_wyoming_banking.md).

| Measurement within 650 m of the location | Original bank settings | Corrected |
|---|---:|---:|
| Maximum absolute bank | 8% | about 3.24% |
| Maximum change in cross slope | 0.445 percentage points/m | 0.0347 percentage points/m |
| Maximum bank-induced longitudinal grade at plan carriageway edge | 2.58% | 0.201% |
| Centerline elevation change from the pre-banking `_plan` | — | exactly 0 in both replayed profiles |

The prior-commit `_plan` was extracted from the parent source and executed against the same sampled inputs;
both current centerline arrays match it exactly. A bank-disabled diagnostic control likewise has identical
XY and longitudinal heights. The correction therefore removes cross-slope artifacts without flattening hills.

The original banking parameters fail four of the new replay checks: bank rate/direction, lane-edge vertical rate,
wheel-track collision pulses, and gradual bridge banking fade. All six new checks pass after correction.

## Segments, tiles, rendering and collision

* Adjacent fragments of the real curve are replayed with neighboring context. Their endpoint XY, elevations,
  bank and lane-edge heights are checked. Bank agreement tolerance is 0.0002 m/m (0.02 percentage points), and
  edge-height agreement is within 3 mm; independent sampling phases need not produce bit-identical floats.
* The bank arrays are interpolated by the same `grade_points` kernel used for terrain, render draping and
  remote collision patches. Ordinary road ribbons are render-only; TerrainBlock heights carry local collision.
  There is no separate rendered-road banking formula to diverge from the collision surface.
* Independently built render tiles at x=0 are compared at shared vertices and against quantized terrain heights.
  Only vertices referenced by rendered triangles count; the builder also retains unused pre-drape vertices.
* Both wheel tracks are checked against a bank-disabled control after height quantization. Collision-only CDAE
  vertices are serialized/read back and checked against the generated geometry, with upward-facing triangles.
* Existing terrain-follow overlap tests verify decoded collision samples remain identical across block moves.
  Ideal-arc seam checks also pass. No tile-lattice or terrain quantization change was needed.
* Banking fades to exact zero at bridge abutments. The Otto bridge geographic replay and existing underpass,
  approach and clearance tests pass with the original Otto fixture, without adding or changing its DEM samples.

## Validation and route testing

All 339 tests passed across 20 suites:

```text
test_i80_banking test_road_seams test_smooth_road_collision test_grading test_roads
test_roadmesh test_heightmap test_terrainpatch test_chunkcache test_plancache test_gradesep
test_approaches test_bridge_clearance test_otto_bridge test_underpass_profiles
test_sidewalk_collision test_surface test_dem test_bridgetypes test_tunnels
```

Run via `python tools/run_tests.py <module names> --par 4 --timeout 300`.
Restart the local server before checking this curve in-game. Source hashes invalidate the existing revisit
cache in a new process. The reporter confirmed this correction in-game. Streetlight generation is outside
the scope of this change.
