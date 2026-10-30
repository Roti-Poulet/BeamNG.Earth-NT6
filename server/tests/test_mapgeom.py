"""mapgeom.py: the map features' geometry helpers."""
import sys
import unittest
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import mapgeom  # noqa: E402
class DropHugeTest(unittest.TestCase):
    """GitHub #413: an OpenStreetMap "building" of 15.8 km2 roofed a whole city."""

    def test_city_sized_footprint_collapsed(self):
        def sq(x0, y0, s):
            k = 1 / 111320.0
            return np.array([[x0, y0], [x0 + s * k, y0], [x0 + s * k, y0 + s * k], [x0, y0 + s * k], [x0, y0]])
        ll = np.concatenate([sq(0, 0, 3000), sq(0.1, 0.1, 20)])
        f = mapgeom.Features("buildings", np.array(["a", "b"]), np.array([3, 3], np.uint8), np.array([0, 1, 2]),
                             np.array([0, 1, 2]), np.array([0, 5, 10]), ll)
        g = mapgeom.drop_huge(f, 2.0e6)
        self.assertEqual(float(np.ptp(g.lonlat[0:5], 0).max()), 0.0)     # (no area: every reader leaves it out)
        self.assertTrue((np.ptp(g.lonlat[5:10], 0) > 0).all())
        self.assertGreater(float(np.ptp(f.lonlat[0:5], 0).max()), 0.0)  # (f itself unchanged)
        self.assertIs(mapgeom.drop_huge(g, 2.0e6), g)


if __name__ == "__main__":
    unittest.main()
