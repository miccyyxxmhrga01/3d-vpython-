"""Regressions for facade gaps, floor openings, and disconnected stairs."""
import unittest

from house import (
    GROUND_CEILING, GROUND_LEVEL, STAIR_OPENING,
    UPPER_CEILING, UPPER_LEVEL, build_house,
)


def contains(shape, point):
    return all(abs(point[i] - shape["pos"][i]) <= shape["size"][i] / 2 + 1e-7 for i in range(3))


class GeometryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.objects = build_house()["objects"]
        cls.envelope = [obj for obj in cls.objects if obj.get("role") in {"wall", "glazing", "frame"}]

    def assert_sealed(self, point):
        self.assertTrue(any(contains(obj, point) for obj in self.envelope), f"Unintended facade gap at {point}")

    def test_ground_floor_envelope_is_closed_except_the_entrance(self):
        for height in (GROUND_LEVEL + .01, 1.8, GROUND_CEILING - .01):
            for i in range(181):
                x = -9 + i * .1
                self.assert_sealed((x, height, -6))
                if abs(x) > 1.48:
                    self.assert_sealed((x, height, 6))
            for i in range(121):
                z = -6 + i * .1
                for x in (-9, 9):
                    self.assert_sealed((x, height, z))

    def test_upper_walls_and_windows_reach_every_corner_and_soffit(self):
        for height in (UPPER_LEVEL + .01, 6, UPPER_CEILING - .01):
            for i in range(83):
                x = 1.15 + i * .1
                for z in (-6.25, 3.6):
                    self.assert_sealed((x, height, z))
            for i in range(100):
                z = -6.25 + i * (9.85 / 99)
                for x in (1.15, 9.35):
                    self.assert_sealed((x, height, z))

    def test_upper_floor_has_no_holes_outside_the_stairwell(self):
        floors = [obj for obj in self.objects if obj.get("role") == "floor"]
        x0, x1, z0, z1 = STAIR_OPENING
        for ix in range(42):
            x = 1.15 + ix * .2
            for iz in range(64):
                z = -6.2 + iz * .2
                if x0 < x < x1 and z0 < z < z1:
                    continue
                point = (x, UPPER_LEVEL - .001, z)
                self.assertTrue(any(contains(obj, point) for obj in floors), f"Unintended floor gap at {point}")

    def test_stairwell_is_open_and_east_wall_has_a_supported_floor(self):
        floors = [obj for obj in self.objects if obj.get("role") == "floor"]
        self.assertFalse(any(contains(obj, (7.9, UPPER_LEVEL - .001, 0)) for obj in floors))
        self.assertTrue(any(contains(obj, (9.2, UPPER_LEVEL - .001, 0)) for obj in floors))

    def test_stair_risers_are_continuous_and_meet_the_upper_landing(self):
        stairs = [obj for obj in self.objects if obj.get("role") == "stair"]
        self.assertEqual(len(stairs), 20)
        previous = None
        for step in stairs:
            self.assertAlmostEqual(step["pos"][1] - step["size"][1] / 2, GROUND_LEVEL)
            if previous:
                front = step["pos"][2] + step["size"][2] / 2
                rear_previous = previous["pos"][2] - previous["size"][2] / 2
                self.assertGreaterEqual(front, rear_previous - 1e-7)
            previous = step
        self.assertAlmostEqual(stairs[-1]["pos"][1] + stairs[-1]["size"][1] / 2, UPPER_LEVEL)
        self.assertAlmostEqual(stairs[-1]["pos"][2] - stairs[-1]["size"][2] / 2, STAIR_OPENING[2], delta=.002)

    def test_pool_basin_is_not_filled_by_the_patios_or_lawn(self):
        point = (-6.8, -.15, 11.3)
        landscape = [obj for obj in self.objects if obj["kind"] == "box" and obj["material"] in {"grass", "stone"}]
        self.assertFalse(any(contains(obj, point) for obj in landscape))


if __name__ == "__main__":
    unittest.main()
