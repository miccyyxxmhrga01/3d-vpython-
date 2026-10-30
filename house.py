"""A warm modern residence, modeled entirely in Python.

Coordinates are in metres: x = east/west, y = up, z = front/back.
Edit this file to change the architecture. The viewer only draws these shapes;
it contains no room or furniture construction code.
"""

from __future__ import annotations

from math import cos, sin, pi
import random


MATERIALS = {
    "plaster": "#e7e2d7", "concrete": "#bcbcb1", "stone": "#d2cabc",
    "floor": "#c4bba9", "wood": "#9a7250", "wood_light": "#b48c61",
    "wood_dark": "#77563c", "frame": "#343b35", "glass": "#b3d4ce",
    "linen": "#e6dfce", "cushion": "#b1aa92", "olive": "#63705a",
    "leaf": "#6d7c51", "leaf_light": "#87916c", "leaf_dark": "#526247",
    "soil": "#777667", "grass": "#8d9877", "water": "#79b5ad",
    "pool": "#acc8bd", "metal": "#46493e", "brass": "#aa9060",
    "light": "#ffe4ab", "book": "#b6a58e", "rug": "#d5cdbb",
    "shadow": "#a5a894", "art": "#596b5a", "white": "#f3efe5",
}


class Model:
    def __init__(self):
        self.objects = []
        self.random = random.Random(26)

    def shape(self, kind, pos, size, material, *, group="house", rotation=0,
              opacity=1, emissive=False, axis=None):
        item = dict(kind=kind, pos=list(pos), size=list(size), material=material, group=group)
        if rotation:
            item["rotation"] = rotation
        if opacity != 1:
            item["opacity"] = opacity
        if emissive:
            item["emissive"] = True
        if axis is not None:
            item["axis"] = list(axis)
        self.objects.append(item)
        return item

    def box(self, x, y, z, w, h, d, material, **kwargs):
        return self.shape("box", (x, y, z), (w, h, d), material, **kwargs)

    def ellipsoid(self, x, y, z, w, h, d, material, **kwargs):
        return self.shape("ellipsoid", (x, y, z), (w, h, d), material, **kwargs)

    def cylinder(self, x, y, z, radius, height, material, **kwargs):
        return self.shape("cylinder", (x, y, z), (radius * 2, height, radius * 2), material, **kwargs)

    def slats(self, x, y, z, count, spacing, height, depth=0.16, width=0.09, group="house"):
        for i in range(count):
            self.box(x + i * spacing, y, z, width, height, depth,
                     ("wood", "wood_light", "wood_dark")[i % 3], group=group)

    def glazing(self, x, y, z, w, h, *, side=False, group="house", doorway=False):
        # Slender, dark anodised frames. Doorways are genuinely open geometry.
        if side:
            self.box(x, y, z, .035, h, w, "glass", opacity=.17, group=group)
            for dz in (-w / 2, w / 2):
                self.box(x, y, z + dz, .085, h, .075, "frame", group=group)
            for dy in (-h / 2, h / 2):
                self.box(x, y + dy, z, .085, .075, w, "frame", group=group)
        else:
            if not doorway:
                self.box(x, y, z, w, h, .035, "glass", opacity=.17, group=group)
            for dx in (-w / 2, w / 2):
                self.box(x + dx, y, z, .075, h, .085, "frame", group=group)
            for dy in (-h / 2, h / 2):
                self.box(x, y + dy, z, w, .075, .085, "frame", group=group)

    def plant(self, x, z, scale=1, y=.25, pot=True):
        if pot:
            self.cylinder(x, y, z, .25 * scale, .43 * scale, "stone", group="plants")
            y += .38 * scale
        rng = self.random
        for i in range(7):
            a = i * 2.4
            self.ellipsoid(x + cos(a) * .21 * scale, y + (.40 + rng.random() * .22) * scale,
                           z + sin(a) * .21 * scale, .20 * scale, .85 * scale, .35 * scale,
                           "leaf" if i % 2 else "leaf_light", rotation=a, group="plants")

    def tree(self, x, z, height=5):
        self.ellipsoid(x + .6, .015, z + .4, 4, .02, 3.1, "shadow", group="landscape")
        self.cylinder(x, -.1, z, .12, height * .7, "wood_dark", group="landscape")
        rng = self.random
        for i in range(14):
            a = i * 2.4
            r = rng.uniform(.2, 1.1)
            self.ellipsoid(x + cos(a) * r, height * .7 + rng.uniform(-.5, .8),
                           z + sin(a) * r, 1.4 + rng.random(), .9 + rng.random(),
                           1.4 + rng.random(), ("leaf", "leaf_light", "leaf_dark")[i % 3],
                           group="landscape")

    def chair(self, x, y, z, rotation=0, outdoor=False):
        # Rotate the complete local furniture assembly about its centre.
        start = len(self.objects)
        self.box(x, y + .43, z, .58, .12, .58, "wood" if outdoor else "linen")
        self.box(x, y + .80, z + .25, .58, .63, .09, "wood")
        for dx in (-.22, .22):
            for dz in (-.22, .22):
                self.box(x + dx, y + .20, z + dz, .055, .42, .055, "wood_dark")
        if rotation:
            for item in self.objects[start:]:
                dx, dz = item["pos"][0] - x, item["pos"][2] - z
                item["pos"][0] = x + dx * cos(rotation) + dz * sin(rotation)
                item["pos"][2] = z - dx * sin(rotation) + dz * cos(rotation)
                item["rotation"] = rotation

    def pendant(self, x, z, y=3.8):
        self.cylinder(x, y - .65, z, .012, .6, "metal")
        self.ellipsoid(x, y - .72, z, .44, .18, .44, "brass")
        self.cylinder(x, y - .80, z, .16, .025, "light", emissive=True)


def landscape(m):
    m.box(0, -.30, 2, 40, .3, 38, "grass", group="landscape")
    # Site edge, terrace, gravel beds, and a long reflecting pool.
    m.box(0, -.10, 5, 23, .18, 27, "stone", group="landscape")
    m.box(-6.8, .015, 11.3, 9.1, .08, 6.1, "white", group="landscape")
    m.box(-6.8, .07, 11.3, 8.55, .08, 5.55, "pool", group="landscape")
    m.box(-6.8, .14, 11.3, 8.25, .02, 5.25, "water", opacity=.83, group="water")
    for i in range(10):
        m.box(1.1, .06, 8.1 + i * .77, 2.0, .11, .59, "concrete", group="landscape")
    # Timber pool deck, lounge beds, side table.
    m.box(-6.9, .16, 6.9, 8.8, .22, 1.6, "wood", group="landscape")
    for i in range(38):
        m.box(-11.2 + i * .23, .28, 6.9, .012, .008, 1.6, "wood_dark", group="landscape")
    for x in (-9.4, -7.4):
        m.box(x, .38, 15.4, 1.1, .25, 2.25, "wood", group="landscape")
        m.box(x, .54, 15.4, .98, .13, 2.14, "linen", group="landscape")
        m.box(x, .73, 14.64, .98, .17, .58, "cushion", rotation=-.2, group="landscape")
    m.cylinder(-8.4, .2, 16.5, .30, .38, "stone", group="landscape")
    for x, z, h in [(-14, -6, 5), (-14, 5, 5.5), (13, -5, 5.8),
                     (14, 9, 5), (-13, 16, 4.2), (8, -11, 5), (-5, -11, 4.5)]:
        m.tree(x, z, h)
    for x, z in [(-11, -5), (-11, 0), (11, 2), (11, 5), (10.5, 13), (5.5, 15.5)]:
        m.plant(x, z, scale=1.1, y=.1, pot=False)
    # Long low planted boundary.
    for z in (-7,):
        m.box(0, .25, z, 20, .65, .9, "concrete", group="landscape")
        for i in range(28):
            m.ellipsoid(-9.4 + i * .7, .74, z, .9, .65, .8, "leaf", group="landscape")


def architecture(m):
    # Floating ground floor and carefully recessed plinth.
    m.box(0, .05, 0, 18.8, .36, 12.8, "concrete")
    m.box(0, .245, 0, 18, .06, 12, "floor")
    m.box(0, -.03, 0, 17.7, .12, 11.7, "shadow")
    # Floor joints; their scale reads as large architectural stone slabs.
    for x in range(-8, 10, 2):
        m.box(x, .28, 0, .012, .002, 11.7, "stone")
    for z in range(-5, 7, 2):
        m.box(0, .281, z, 17.8, .002, .012, "stone")
    # Living pavilion: solid rear and west end, glazed front.
    m.box(-4.2, 2.12, -6, 9.6, 3.7, .24, "plaster")
    m.box(-9, 2.12, -2.1, .24, 3.7, 7.8, "plaster")
    m.glazing(-9, 2.12, 3.95, 3.9, 3.7, side=True)
    for x in (-7.2, -4.05):
        m.glazing(x, 2.10, 6, 3.15, 3.65)
    # Open entry portal between glass pavilion and timber-clad wing.
    m.glazing(-.1, 1.98, 6, 2.8, 3.4, doorway=True)
    m.box(-.1, 3.82, 6, 2.9, .35, .26, "plaster")
    m.box(1.65, 2.05, 6, .35, 3.6, .3, "wood")
    # Kitchen/foyer separation is partial, preserving the open-plan layout.
    m.box(1.1, 2.12, -2.45, .20, 3.7, 6.9, "plaster")
    m.box(1.1, 2.12, 5.0, .20, 3.7, 2.0, "plaster")
    m.box(5, 2.1, -6, 8, 3.7, .24, "plaster")
    m.glazing(9, 2.10, 0, 12, 3.65, side=True)
    m.box(5.4, 2.10, 6, 7.2, 3.65, .15, "wood_dark")
    m.slats(1.85, 2.1, 6.14, 48, .15, 3.65, depth=.20, width=.085)
    # Canopy and left roof: thin concrete profiles with timber soffits.
    m.box(-4, 4.08, .1, 11.4, .25, 13.6, "wood", group="roof")
    m.box(-4, 4.30, .1, 11.8, .23, 14.0, "plaster", group="roof")
    m.box(-4, 4.44, .1, 11.2, .05, 13.4, "stone", group="roof")
    # Upper volume cantilevers over the lower timber-clad wing.
    # Three slabs leave an actual stairwell instead of a solid floor above it.
    for x, z, w, d in [(4.0, -.1, 6.2, 12.7), (8.3, -5.1, 2.5, 2.7),
                       (8.3, 5.2, 2.5, 2.1)]:
        m.box(x, 4.2, z, w, .36, d, "plaster", group="upper")
        m.box(x, 4.40, z, w - .05, .05, d - .05, "wood_light", group="upper")
    m.box(1.15, 5.97, -1.5, .22, 3.1, 9.0, "plaster", group="upper")
    m.box(5.2, 5.97, -6.25, 8.4, 3.1, .22, "plaster", group="upper")
    m.box(9.35, 5.97, -1.6, .22, 3.1, 9.2, "plaster", group="upper")
    # Bedroom and balcony glazing.
    for x in (3.3, 6.1, 8.2):
        m.glazing(x, 5.90, 3.6, 2.75 if x < 7 else 1.4, 2.95, group="upper")
    m.box(5.2, 4.42, 5.0, 8.3, .06, 2.8, "wood", group="upper")
    for i in range(29):
        m.box(1.25 + i * .28, 4.46, 5, .012, .008, 2.8, "wood_dark", group="upper")
    m.box(5.2, 5.02, 6.4, 8.4, 1.15, .045, "glass", opacity=.20, group="upper")
    m.box(5.2, 5.61, 6.4, 8.4, .045, .065, "frame", group="upper")
    for x in (1.1, 5.2, 9.4):
        m.box(x, 5.02, 6.4, .045, 1.2, .06, "frame", group="upper")
    m.box(5.2, 7.63, -.1, 9.2, .24, 13.6, "wood", group="roof")
    m.box(5.2, 7.86, -.1, 9.5, .22, 13.9, "plaster", group="roof")
    # Upper right privacy fins, on the exterior side of the bedroom glazing.
    m.slats(7.35, 5.98, 3.9, 12, .17, 3.06, depth=.35, width=.075, group="upper")
    # Straight stair in the east hall; open landing at z=-3.9.
    for i in range(20):
        z = 3.9 - i * .39
        h = .28 + (i + 1) * .207
        m.box(7.9, h - .105, z, 1.65, .21, .40, "wood")
        m.box(8.78, h + .44, z, .035, .88, .035, "frame")
    m.shape("cylinder", (8.78, 1.32, 3.9), (.045, 8.6, .045), "frame", axis=(0, 4.14, -7.41))


def living_room(m):
    # Sunken-looking lounge, pale boucle sectional, low oak coffee table.
    m.box(-5.35, .30, 2.1, 5.8, .04, 4.25, "rug")
    m.box(-6.3, .54, 2.3, 3.6, .39, 1.1, "wood_dark")
    m.box(-6.3, .81, 2.3, 3.8, .36, 1.17, "linen")
    m.box(-6.3, 1.12, 2.81, 3.8, .65, .24, "linen")
    m.box(-7.98, 1, 2.3, .28, .65, 1.2, "linen")
    m.box(-4.61, 1, 2.3, .28, .65, 1.2, "linen")
    m.box(-7.5, .81, 1.3, 1.25, .36, 1.7, "linen")
    for x in (-7.3, -6.15, -5.05):
        m.box(x, 1.16, 2.64, .62, .48, .18, "olive" if x == -6.15 else "cushion", rotation=.1)
    m.box(-5.4, .49, .45, 2.15, .12, 1.2, "wood")
    m.box(-5.4, .37, .45, 1.25, .21, .65, "wood_dark")
    m.box(-5.7, .58, .5, .52, .06, .36, "book")
    m.cylinder(-4.9, .56, .35, .16, .22, "stone")
    m.plant(-8.15, 4.85, 1.25)
    # Feature wall with a long, recessed fireplace and framed artwork.
    m.box(-8.78, 1.7, -1, .20, 2.8, 3.8, "wood_dark")
    m.box(-8.65, 1.06, -1, .05, .50, 2.85, "frame")
    m.box(-8.60, .89, -1, .035, .06, 2.50, "light", emissive=True)
    m.box(-8.62, 2.35, -1, .08, 1.25, 2.25, "wood")
    m.box(-8.56, 2.35, -1, .035, 1.12, 2.12, "white")
    m.ellipsoid(-8.53, 2.4, -1, .02, .72, 1.1, "art")
    m.cylinder(-3.3, .28, 5.1, .035, 2.3, "metal")
    m.ellipsoid(-3.3, 2.5, 5.1, .7, .35, .7, "linen")
    m.cylinder(-3.3, .28, 5.1, .25, .035, "metal")
    # Dining for six, kept clear of the camera route.
    m.box(-5.9, 1.04, -3.3, 2.8, .12, 1.25, "wood")
    for dx in (-.9, .9):
        m.box(-5.9 + dx, .65, -3.3, .12, .76, .8, "wood_dark")
    for x in (-6.8, -5.85, -4.9):
        m.chair(x, .28, -4.38)
        m.chair(x, .28, -2.22, pi)
    m.pendant(-6.8, -3.3)
    m.pendant(-5.0, -3.3)
    m.cylinder(-5.9, 1.1, -3.3, .18, .26, "stone")


def kitchen(m):
    # Flat-front oak joinery and light stone waterfall island.
    for i in range(5):
        x = -3.35 + i * .8
        m.box(x, .74, -5.45, .78, .92, .95, "wood")
        m.box(x, 1.24, -5.45, .8, .08, 1.0, "white")
        m.box(x, 2.47, -5.78, .78, .95, .35, "plaster")
        m.box(x, .92, -4.963, .24, .025, .025, "brass")
    m.box(-.15, 1.75, -5.40, .9, 2.95, 1.0, "wood_dark")
    m.box(-.15, 1.61, -4.88, .68, .65, .025, "frame")
    m.box(-.15, 2.48, -4.88, .68, .55, .025, "frame")
    m.box(-2.35, 1.29, -5.45, .85, .025, .62, "frame")
    for x in (-2.57, -2.13):
        for z in (-5.62, -5.26):
            m.cylinder(x, 1.31, z, .12, .006, "metal")
    m.box(-1.6, .78, -2.8, 2.95, 1.0, 1.0, "wood_dark")
    m.box(-1.6, 1.32, -2.8, 3.1, .12, 1.35, "white")
    for x in (-3.1, -.1):
        m.box(x, .8, -2.8, .10, .98, 1.35, "white")
    m.box(-1.4, 1.386, -2.87, .65, .02, .45, "metal")
    m.cylinder(-1.4, 1.39, -3.18, .025, .35, "brass")
    m.box(-1.4, 1.73, -3.08, .05, .05, .26, "brass")
    for x in (-2.7, -1.6, -.5):
        m.cylinder(x, .28, -1.55, .025, .66, "frame")
        m.cylinder(x, .94, -1.55, .27, .1, "wood")
    m.pendant(-2.4, -2.8)
    m.pendant(-.8, -2.8)
    m.plant(.35, -.05, .8)


def bedroom(m):
    start = len(m.objects)
    floor = 4.44
    m.box(4.3, floor + .03, -.4, 4.9, .04, 5.9, "rug")
    m.box(4.3, floor + .32, -.7, 2.8, .5, 3.9, "wood_dark")
    m.box(4.3, floor + .63, -.7, 2.75, .32, 3.85, "linen")
    m.box(4.3, floor + .88, -2.55, 3.0, 1.25, .16, "wood")
    m.box(4.3, floor + .83, .05, 2.78, .10, 2.15, "cushion")
    for x in (3.65, 4.95):
        m.box(x, floor + .9, -1.85, 1.04, .22, .72, "white")
    for x in (2.25, 6.35):
        m.box(x, floor + .45, -2.0, .75, .7, .65, "wood")
        m.cylinder(x, floor + .83, -2.0, .16, .26, "stone")
        m.ellipsoid(x, floor + 1.17, -2.0, .4, .34, .4, "linen")
    # Built-in wardrobes and a quiet reading chair.
    for i in range(5):
        m.box(2.0 + i * 1.25, floor + 1.4, -5.55, 1.22, 2.8, .8, "wood")
        m.box(2.0 + i * 1.25, floor + 1.4, -5.13, .025, .4, .025, "brass")
    m.chair(7.6, floor, 1.5, -.5)
    m.cylinder(8.55, floor, 1.1, .35, .65, "stone")
    for item in m.objects[start:]:
        item["group"] = "upper"
    m.plant(8.2, 4.9, 1, floor)
    for x in (3.1, 6.3):
        start = len(m.objects)
        m.chair(x, floor, 5.2, pi, outdoor=True)
        for item in m.objects[start:]:
            item["group"] = "upper"


def terrace(m):
    m.box(5.4, .27, 9.5, 5.8, .16, 4.4, "wood", group="landscape")
    for i in range(26):
        m.box(2.6 + i * .225, .36, 9.5, .012, .008, 4.4, "wood_dark", group="landscape")
    m.box(5.5, .85, 10, 2.6, .12, 1.3, "wood")
    for dx in (-.9, .9):
        m.box(5.5 + dx, .56, 10, .1, .5, .8, "wood_dark")
    for x in (4.7, 6.2):
        m.chair(x, .35, 8.9, 0, True)
        m.chair(x, .35, 11.1, pi, True)
    # Open steel pergola with timber rafters.
    for x in (2.5, 8.3):
        for z in (7.4, 11.8):
            m.box(x, 1.8, z, .09, 3, .09, "frame", group="pergola")
    for x in (2.5, 8.3):
        m.box(x, 3.35, 9.6, .12, .16, 4.7, "frame", group="pergola")
    for i in range(16):
        m.box(5.4, 3.4, 7.4 + i * .29, 6.1, .16, .07, "wood", group="pergola")
    m.plant(8.0, 11.4, 1.1)


def build_house():
    m = Model()
    landscape(m)
    architecture(m)
    living_room(m)
    kitchen(m)
    bedroom(m)
    terrace(m)
    return {
        "name": "Caybin Dream House",
        "materials": MATERIALS,
        "objects": m.objects,
        "overview": {"pos": [25, 16, 30], "target": [0, 2.1, 2.5]},
        # An obstacle-free centreline, including a stair climb. Each point has
        # eye and look-at coordinates. The browser interpolates them on scroll.
        "route": [
            {"pos": [1.1, 1.92, 18], "target": [-.1, 1.9, 5], "room": "approach"},
            {"pos": [.1, 1.92, 9], "target": [-.1, 1.9, 1], "room": "entrance"},
            {"pos": [-.1, 1.92, 4.7], "target": [-4.7, 1.3, 1.5], "room": "entrance"},
            {"pos": [-2.5, 1.92, 3.8], "target": [-7, 1.3, .2], "room": "living"},
            {"pos": [-3.5, 1.92, .9], "target": [-6.5, 1.4, -2], "room": "living"},
            {"pos": [-3.6, 1.92, -1], "target": [-1.5, 1.3, -4], "room": "kitchen"},
            {"pos": [.3, 1.92, -.5], "target": [-1.3, 1.5, -4], "room": "kitchen"},
            {"pos": [.3, 1.92, 2.4], "target": [5, 1.8, 3], "room": "staircase"},
            {"pos": [2.4, 1.92, 2.4], "target": [7.9, 1.8, 3.9], "room": "staircase"},
            {"pos": [7.9, 1.92, 4.4], "target": [7.9, 4.6, -4], "room": "staircase"},
            {"pos": [7.9, 3.9, .5], "target": [7.9, 5.8, -4.8], "room": "staircase"},
            {"pos": [7.9, 6.1, -4.1], "target": [4.2, 5.4, -.7], "room": "bedroom"},
            {"pos": [6.5, 6.1, -4.1], "target": [4.2, 5.4, -.7], "room": "bedroom"},
            {"pos": [6.7, 6.1, 2.8], "target": [4.3, 5.3, -.7], "room": "bedroom"},
        ],
        "stops": [
            {"id": "entrance", "name": "The entrance", "detail": "A sheltered arrival", "progress": 2 / 13},
            {"id": "living", "name": "Living room", "detail": "Light, space & a slower pace", "progress": 3.4 / 13},
            {"id": "kitchen", "name": "Kitchen & dining", "detail": "Made for gathering", "progress": 5.4 / 13},
            {"id": "bedroom", "name": "The bedroom", "detail": "Your own quiet retreat", "progress": 1.0},
        ],
        "terrace": {"pos": [4.0, 1.95, 13], "target": [5.4, 1.2, 8.9]},
    }
