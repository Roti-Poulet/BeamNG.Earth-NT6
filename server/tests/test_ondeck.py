"""A building on a pier or bridge deck over water stands on the deck, not on the seabed under it (the Sunshine Skyway
fishing pier's bait shop, 2026-10-27); one over the deck's lanes is left out; one on dry land under a viaduct stays."""
import os
import sys
import unittest

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import buildings  # noqa: E402

DECK = (np.array([[0.0, 0.0], [100.0, 0.0]]), np.array([5.0, 5.0]), 4.0)      # a pier's 4 m lane, 5 m up


def box(cx, cy, hx=3.0, hy=3.0):
    return np.array([[cx - hx, cy - hy], [cx + hx, cy - hy], [cx + hx, cy + hy], [cx - hx, cy + hy]])


class OnDeckTest(unittest.TestCase):
    def test_beside_the_lanes_stands_on_the_deck(self):
        got = buildings.on_deck(box(50.0, 4.5, 1.5, 1.5), [DECK], -3.0)        # 3..6 m off the centre line
        self.assertEqual(got, (False, 5.0))

    def test_over_the_lanes_left_out(self):
        got = buildings.on_deck(box(50.0, 0.0), [DECK], -3.0)
        self.assertTrue(got[0])

    def test_dry_land_under_a_viaduct_stays(self):
        self.assertIsNone(buildings.on_deck(box(50.0, 4.5, 1.5, 1.5), [DECK], 2.0))

    def test_off_the_deck_or_deck_on_the_ground(self):
        self.assertIsNone(buildings.on_deck(box(50.0, 30.0), [DECK], -3.0))
        low = (DECK[0], np.array([-2.0, -2.0]), 4.0)
        self.assertIsNone(buildings.on_deck(box(50.0, 4.5, 1.5, 1.5), [low], -3.0))

    def test_old_two_tuple_decks_ignored(self):
        self.assertIsNone(buildings.on_deck(box(50.0, 4.5, 1.5, 1.5), [DECK[:2]], -3.0))


if __name__ == "__main__":
    unittest.main()
