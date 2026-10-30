"""Checks for the architectural model, independent of a browser or GPU."""
import json
import math
import unittest

from house import build_house


class HouseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.model = build_house()

    def test_scene_can_be_serialized_without_invalid_numbers(self):
        json.dumps(self.model, allow_nan=False)
        for obj in self.model["objects"]:
            self.assertIn(obj["material"], self.model["materials"])
            self.assertTrue(all(v > 0 and math.isfinite(v) for v in obj["size"]))

    def test_generation_is_reproducible(self):
        self.assertEqual(self.model, build_house())

    def test_walkthrough_does_not_pass_through_opaque_geometry_at_eye_level(self):
        route = self.model["route"]
        for a, b in zip(route, route[1:]):
            for sample in range(41):
                t = sample / 40
                p = [x + (y - x) * t for x, y in zip(a["pos"], b["pos"])]
                for obj in self.model["objects"]:
                    if obj["kind"] != "box" or obj.get("opacity", 1) < .5 or obj.get("rotation"):
                        continue
                    if all(abs(p[i] - obj["pos"][i]) < obj["size"][i] / 2 + .035 for i in range(3)):
                        self.fail(f"Route intersects {obj['material']} {obj['group']} at {p}: {obj}")

    def test_room_stops_land_in_their_named_room(self):
        for stop in self.model["stops"]:
            t = stop["progress"] * (len(self.model["route"]) - 1)
            nearest = min(round(t), len(self.model["route"]) - 1)
            self.assertEqual(self.model["route"][nearest]["room"], stop["id"])


if __name__ == "__main__":
    unittest.main()
