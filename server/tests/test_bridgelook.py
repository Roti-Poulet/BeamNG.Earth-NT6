"""Bridge look (2026-10-27): the type a movable or lens bridge gets, its spans, its towers and houses; the deck's
lift over a bank; carriageways side by side are not stacked."""
import sys
import unittest
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import bridgetypes as bt  # noqa: E402
import roadmesh  # noqa: E402
import roads  # noqa: E402


def deck(x0=-200.0, x1=200.0, z=25.0, y=0.0, w=12.0):
    xs = np.arange(x0, x1 + 1e-6, 4.0)
    return (np.c_[xs, np.full(len(xs), y)], np.full(len(xs), z), w)


FLAT = staticmethod(lambda xy: np.zeros(len(xy)))


def river(half):
    """Ground: a river |x| < half at 0 m between 12 m banks (no sea)."""
    return lambda xy: np.where(np.abs(np.asarray(xy)[:, 0]) < half, 0.0, 12.0)


class TypeTest(unittest.TestCase):
    def test_movable_record_beats_an_arch_tag(self):
        self.assertEqual(bt.resolve_type(bt.ARCH_ANY, bt.NBI_BASCULE), (bt.NBI_BASCULE, "arched"))
        self.assertEqual(bt.resolve_type(0, bt.NBI_LIFT), (bt.NBI_LIFT, None))

    def test_truss_record_tagged_arch_is_a_lens(self):
        self.assertEqual(bt.resolve_type(bt.ARCH_ANY, bt.NBI_THROUGH_TRUSS), (bt.NBI_THROUGH_TRUSS, "lens"))
        self.assertEqual(bt.resolve_type(bt.NBI_THROUGH_TRUSS, 0, {"bridge:truss": "lenticular"}),
                         (bt.NBI_THROUGH_TRUSS, "lens"))

    def test_cable_and_plain_kept(self):
        self.assertEqual(bt.resolve_type(bt.NBI_SUSPENSION, bt.NBI_THROUGH_TRUSS), (bt.NBI_SUSPENSION, None))
        self.assertEqual(bt.resolve_type(bt.NBI_THROUGH_ARCH, 0), (bt.NBI_THROUGH_ARCH, None))

    def test_stray_site_without_a_size_dropped(self):
        got = bt._drop_strays([{"type": bt.ARCH_ANY, "span": 0.0, "src": "osm"},
                               {"type": bt.NBI_THROUGH_ARCH, "span": 380.0, "src": "osm+nbi"}])
        self.assertEqual([g["span"] for g in got], [380.0])


class LensTest(unittest.TestCase):
    def test_two_lens_spans_over_305_m_of_river(self):
        info = {"type": bt.NBI_THROUGH_TRUSS, "span": 110.0, "shape": "lens"}
        g = river(152.5)
        beams = bt.truss_members([deck(-260.0, 260.0)], info, g)
        self.assertTrue(beams)
        x = np.array([p[0] for b in beams for p in b[:2]])
        self.assertLessEqual(x.max() - x.min(), 2 * 110.0 + 2 * bt.PANEL_M)     # 2 spans, not 3
        top = max(p[2] for b in beams for p in b[:2])
        self.assertGreater(top, 25.0 + bt.PORTAL_M + 0.5 * bt.LENS_RISE * 110.0)

    def test_spans_counted_on_one_axis(self):
        run = [(np.array([x, 6.0]), np.array([x, -6.0]), 20.0, 30.0, np.array([1.0, 0.0]))
               for x in np.arange(-150.0, 150.1, 14.0)]
        k, t, keep = bt._spans_of(run, 110.0, bt._span_axis([run]))
        self.assertEqual(int(k[keep].max()) + 1, 2)


class MovableTest(unittest.TestCase):
    def test_lift_span_has_two_towers_over_the_river(self):
        info = {"type": bt.NBI_LIFT, "span": 76.0, "src": "nbi"}
        beams, _ = bt.structure_members([deck()], info, river(150.0))
        z = np.array([p[2] for b in beams for p in b[:2]])
        self.assertGreater(z.max(), 25.0 + bt.LIFT_TOWER_MIN)
        tall = [b for b in beams if abs(b[1][2] - b[0][2]) > 15.0]
        xs = sorted({round(float(b[0][0])) for b in tall})
        self.assertTrue(any(abs(x + 38) < 6 for x in xs) and any(abs(x - 38) < 6 for x in xs), xs)

    def test_girder_bascule_houses_and_piers(self):
        info = {"type": bt.NBI_BASCULE, "span": 80.0, "src": "nbi"}
        beams, piers = bt.structure_members([deck()], info, river(150.0))
        self.assertTrue(beams)
        self.assertEqual(len(piers), 2)
        self.assertTrue(all(abs(abs(p[0]) - 40.0) < 6.0 for p in piers))

    def test_bascule_over_no_water_draws_nothing(self):
        info = {"type": bt.NBI_BASCULE, "span": 80.0, "src": "nbi"}
        self.assertEqual(bt.structure_members([deck(z=12.0)], info, lambda xy: np.full(len(xy), 3.0)), ([], []))


class DeckTest(unittest.TestCase):
    def test_lift_over_a_bank_is_rounded(self):
        s = np.arange(0.0, 420.1, 3.0)
        z = 22.0 + 0.0 * s
        z[-1] = 25.0
        floor = np.where(s > 410, 25.05, 11.0)                   # a bank under the deck's last 10 m
        out = roads._lift_smooth(s, z, floor)
        gr = np.diff(out) / np.diff(s)
        self.assertLess(np.abs(np.diff(gr[:-1])).max(), 0.02)
        self.assertEqual(out[-1], 25.0)
        self.assertTrue((out[1:-1] >= np.minimum(floor, 25.0 + roads.LIFT_END_GRADE * (s[-1] - s))[1:-1] - 1e-6).all())

    def test_side_by_side_carriageways_not_stacked(self):
        a = np.c_[np.arange(0.0, 400.0, 4.0), np.zeros(100)]
        b = np.c_[np.arange(0.0, 400.0, 4.0), np.full(100, 8.5)]
        self.assertEqual(roads._deck_stacks([a, b], [2.0, 1.0], [11.8, 11.8]), [])
        c = np.c_[np.arange(0.0, 400.0, 4.0), np.full(100, 1.5)]
        self.assertTrue(roads._deck_stacks([a, c], [2.0, 1.0], [11.8, 11.8]))


class ParapetTest(unittest.TestCase):
    @staticmethod
    def edges_count(T, P=None):
        """Faces per edge; with P, edges matched by position (each face has its own vertices)."""
        if P is not None:
            _, inv = np.unique(np.round(P, 6), axis=0, return_inverse=True)
            T = inv.ravel()[T]
        e = np.sort(np.concatenate([T[:, [0, 1]], T[:, [1, 2]], T[:, [2, 0]]]), 1)
        _, c = np.unique(e, axis=0, return_counts=True)
        return c

    def test_barrier_is_closed_and_faces_out(self):
        x = np.arange(0.0, 40.1, 4.0)
        edge = np.c_[x, np.full(len(x), 5.0)]
        P, T, _ = roadmesh.barrier_solid(edge, np.tile([0.0, -1.0], (len(x), 1)), np.zeros(len(x)),
                                         np.full(len(x), roadmesh.PARAPET_H))
        self.assertTrue((self.edges_count(T, P) == 2).all(), "every edge shared by exactly two faces")
        # outward: the signed volume is positive (all faces wound the same way, out)
        v = np.einsum("ij,ij->i", P[T[:, 0]], np.cross(P[T[:, 1]], P[T[:, 2]])).sum() / 6.0
        self.assertGreater(v, 0.0)
        area = roadmesh.PARAPET_W * roadmesh.PARAPET_H
        self.assertTrue(0.3 * area * 40 < v < area * 40)

    def test_parapet_on_the_deck_edge_and_ramped_at_the_abutment(self):
        x = np.arange(0.0, 60.1, 4.0)
        pts = np.c_[x, np.zeros(len(x)), 0.02 * x]                  # lands on the ground at x = 0
        chunks = [{"n": pts, "w": 10.0, "m": "asphalt", "fixed": True, "deck": True, "fid": "a",
                   "abut": roads._abutments(pts, lambda xy: np.zeros(len(xy)))}]
        got = roadmesh.deck(chunks, (0.0, 0.0, 0.0))
        P, T = got[0], got[1]
        half = max(float(c["w"]) for c in chunks if c.get("deck")) / 2
        self.assertLessEqual(np.abs(P[:, 1]).max(), half + roadmesh.PARAPET_W + 1e-6)   # nothing past the slab's edge
        top = P[np.abs(P[:, 1]) > half]                              # the parapets (and slab edge)
        near = top[top[:, 0] < 1.0]
        far = top[(top[:, 0] > 20) & (top[:, 0] < 40)]
        rise_near = (near[:, 2] - 0.02 * near[:, 0]).max()
        rise_far = (far[:, 2] - 0.02 * far[:, 0]).max()
        self.assertLess(rise_near, roadmesh.END_H + 0.2)    # ramped down at the abutment
        self.assertAlmostEqual(rise_far, roadmesh.PARAPET_H, delta=0.05)

    def test_heights(self):
        e = np.c_[np.arange(0.0, 20.1, 2.0), np.zeros(11)]
        h = roadmesh.parapet_heights(e, [(0.0, 0.0)])
        self.assertAlmostEqual(h[0], roadmesh.PARAPET_END_H)
        self.assertAlmostEqual(h[-1], roadmesh.PARAPET_H)
        self.assertTrue((np.diff(h) >= -1e-9).all())
        self.assertTrue((roadmesh.parapet_heights(e, None) == roadmesh.PARAPET_H).all())


class JerseyTest(unittest.TestCase):
    def test_dimensions(self):
        sec = roadmesh.jersey_section(roadmesh.JERSEY_H)
        xs, ys = [p[0] for p in sec], [p[1] for p in sec]
        self.assertAlmostEqual(max(ys), 0.84)
        self.assertAlmostEqual(max(xs), 0.38)                       # half of the 610 mm base, less its 115 mm outer half
        self.assertIn((0.15, 0.84), [(round(x, 3), round(y, 3)) for x, y in sec])        # 150 mm top
        self.assertIn((0.255, 0.38), [(round(x, 3), round(y, 3)) for x, y in sec])       # the 55 degree break
        self.assertIn((0.38, 0.13), [(round(x, 3), round(y, 3)) for x, y in sec])        # 130 mm toe

    def test_sloped_end_narrows_to_a_square_low_nose(self):
        x = np.arange(0.0, 20.1, 1.0)
        line = np.c_[x, np.zeros(len(x))]
        h = roadmesh.parapet_heights(line, [(0.0, 0.0), (20.0, 0.0)])
        self.assertAlmostEqual(h[0], roadmesh.END_H)
        self.assertAlmostEqual(h[10], roadmesh.JERSEY_H)
        P, T, _ = roadmesh.barrier_solid(line + [0, 5.0], np.tile([0.0, -1.0], (len(x), 1)), np.zeros(len(x)), h)
        self.assertTrue((ParapetTest.edges_count(T, P) == 2).all())
        n = len(roadmesh.JERSEY)
        nose = P[-2 * n:-n]                                       # (the first end cap's own vertices)
        self.assertAlmostEqual(nose[:, 2].max(), roadmesh.END_H)     # low, square (a full-width end face) ...
        self.assertAlmostEqual(nose[:, 1].min(), 5.0 - roadmesh.JERSEY_HALF_W)
        self.assertAlmostEqual(nose[:, 2].min(), 0.0)                # ... and on its base (grounded on the slab)

    def test_uv_world_scale_no_stretch(self):
        x = np.arange(0.0, 20.1, 1.0)
        line = np.c_[x, np.zeros(len(x))]
        P, T, UV = roadmesh.barrier_solid(line, np.tile([0.0, 1.0], (len(x), 1)), np.zeros(len(x)),
                                          roadmesh.parapet_heights(line, [(0.0, 0.0)]))
        for t in T:                                                  # uv distance / world distance on every edge
            for a, b in ((0, 1), (1, 2), (2, 0)):
                d = np.linalg.norm(P[t[a]] - P[t[b]])
                if d > 1e-6:
                    self.assertAlmostEqual(np.linalg.norm(UV[t[a]] - UV[t[b]]) / d, roadmesh.UV_M, delta=0.06)


if __name__ == "__main__":
    unittest.main()
