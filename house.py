"""A warm modern house modeled in Python and displayed with VPython's engine.

Coordinates are in metres: x = east/west, y = up, z = front/back.
viewer.py creates native VPython objects and uses VPython's camera controls.
"""

from __future__ import annotations

from math import cos, sin, pi
import random


# All adjoining surfaces share these finished levels (metres).
GROUND_LEVEL = .28
GROUND_CEILING = 4.02
UPPER_LEVEL = 4.44
UPPER_CEILING = 7.62
STAIR_OPENING = (7.05, 8.95, -3.95, 4.2)  # west, east, rear, front


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
              opacity=1, emissive=False, axis=None, role=None):
        item = dict(kind=kind, pos=list(pos), size=list(size), material=material, group=group)
        if rotation:
            item["rotation"] = rotation
        if opacity != 1:
            item["opacity"] = opacity
        if emissive:
            item["emissive"] = True
        if axis is not None:
            item["axis"] = list(axis)
        if role is not None:
            item["role"] = role
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
            self.box(x, y, z, .035, h, w, "glass", opacity=.17, group=group, role="glazing")
            for dz in (-w / 2, w / 2):
                self.box(x, y, z + dz, .085, h, .075, "frame", group=group, role="frame")
            for dy in (-h / 2, h / 2):
                self.box(x, y + dy, z, .085, .075, w, "frame", group=group, role="frame")
        else:
            if not doorway:
                self.box(x, y, z, w, h, .035, "glass", opacity=.17, group=group, role="glazing")
            for dx in (-w / 2, w / 2):
                self.box(x + dx, y, z, .075, h, .085, "frame", group=group, role="frame")
            for dy in (-h / 2, h / 2):
                self.box(x, y + dy, z, w, .075, .085, "frame", group=group, role="frame")

    def plant(self, x, z, scale=1, y=GROUND_LEVEL, pot=True):
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
        self.ellipsoid(x + .6, -.147, z + .4, 4, .004, 3.1, "shadow", group="landscape")
        self.cylinder(x, -.15, z, .12, height * .7 + .05, "wood_dark", group="landscape")
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
    for x0, x1, z0, z1 in [(-17, -11.2, -15, 19), (-2.4, 17, -15, 19),
                           (-11.2, -2.4, -15, 8.1), (-11.2, -2.4, 14.5, 19)]:
        m.box((x0 + x1) / 2, -.30, (z0 + z1) / 2,
              x1 - x0, .3, z1 - z0, "grass", group="landscape")
    # Four continuous patio slabs leave a genuine opening for the pool.
    for x0, x1, z0, z1 in [(-11.5, -11.2, -8.5, 18.5),
                           (-2.4, 11.5, -8.5, 18.5),
                           (-11.2, -2.4, -8.5, 8.1),
                           (-11.2, -2.4, 14.5, 18.5)]:
        m.box((x0 + x1) / 2, .06, (z0 + z1) / 2,
              x1 - x0, .20, z1 - z0, "stone", group="landscape")
    # Recessed basin, vertical pool walls, and a continuous stone coping.
    m.box(-6.8, -1.1, 11.3, 8.8, .16, 6.4, "pool", group="landscape")
    for x in (-11.08, -2.52):
        m.box(x, -.43, 11.3, .24, 1.34, 6.4, "pool", group="landscape")
        m.box(x, .21, 11.3, .24, .14, 6.4, "white", group="landscape")
    for z in (8.22, 14.38):
        m.box(-6.8, -.43, z, 8.32, 1.34, .24, "pool", group="landscape")
        m.box(-6.8, .21, z, 8.32, .14, .24, "white", group="landscape")
    m.box(-6.8, .12, 11.3, 8.32, .025, 5.92, "water", opacity=.83, group="water")
    for i in range(10):
        m.box(1.1, .22, 8.1 + i * .77, 2.0, .12, .59, "concrete", group="landscape")
    # Timber pool deck, lounge beds, side table.
    m.box(-6.9, .22, 6.9, 8.8, .12, 1.6, "wood", group="landscape")
    for i in range(38):
        m.box(-11.2 + i * .23, .281, 6.9, .012, .002, 1.6, "wood_dark", group="landscape")
    for x in (-9.4, -7.4):
        for dx in (-.4, .4):
            for dz in (-.8, .8):
                m.box(x + dx, .21, 15.4 + dz, .08, .10, .08, "wood_dark", group="landscape")
        m.box(x, .38, 15.4, 1.1, .25, 2.25, "wood", group="landscape")
        m.box(x, .54, 15.4, .98, .13, 2.14, "linen", group="landscape")
        m.box(x, .69, 14.64, .98, .17, .58, "cushion", rotation=-.2, group="landscape")
    m.cylinder(-8.4, .16, 16.5, .30, .42, "stone", group="landscape")
    for x, z, h in [(-14, -6, 5), (-14, 5, 5.5), (13, -5, 5.8),
                     (14, 9, 5), (-13, 16, 4.2), (8, -11, 5), (-5, -11, 4.5)]:
        m.tree(x, z, h)
    for x, z in [(-11, -5), (-11, 0), (11, 2), (11, 5), (10.5, 13), (5.5, 15.5)]:
        m.plant(x, z, scale=1.1, y=.16, pot=False)
    # Long low planted boundary.
    for z in (-7,):
        m.box(0, .25, z, 20, .65, .9, "concrete", group="landscape")
        for i in range(28):
            m.ellipsoid(-9.4 + i * .7, .74, z, .9, .65, .8, "leaf", group="landscape")


def architecture(m):
    # A flush floor and continuous rear wall anchor the two interlocking volumes.
    m.box(0, .04, 0, 18.8, .40, 12.8, "concrete", role="foundation")
    m.box(0, .26, 0, 18.24, .04, 12.24, "floor", role="floor")
    low_y = (GROUND_LEVEL + GROUND_CEILING) / 2
    low_h = GROUND_CEILING - GROUND_LEVEL
    m.box(0, low_y, -6, 18.24, low_h, .24, "plaster", role="wall")
    m.box(-9, low_y, -2.2, .24, low_h, 7.6, "plaster", role="wall")
    m.glazing(-9, low_y, 3.8, 4.4, low_h, side=True)
    # Shared bay endpoints close the old facade and corner gaps.
    for left in (-9, -6.5, -4):
        m.glazing(left + 1.25, low_y, 6, 2.5, low_h)
    m.glazing(0, low_y, 6, 3.0, low_h, doorway=True)
    # An open oak entrance leaf and glazed transom distinguish the doorway
    # from an accidental missing facade panel. Keep the camera path clear.
    m.box(-1.4, GROUND_LEVEL + 1.5, 5.3, 1.4, 3, .10, "wood", rotation=pi / 2)
    m.box(-1.325, 1.6, 5.45, .035, .38, .035, "brass")
    transom_bottom = GROUND_LEVEL + 3
    m.box(0, (transom_bottom + GROUND_CEILING) / 2, 6,
          3, GROUND_CEILING - transom_bottom, .035, "glass", opacity=.17, role="glazing")
    m.box(0, transom_bottom, 6, 3, .075, .085, "frame", role="frame")
    m.box(0, .20, 6.25, 3.1, .16, .65, "concrete", role="threshold")
    m.box(1.65, low_y, 6, .30, low_h, .24, "wood", role="wall")
    m.box(5.4, low_y, 6, 7.2, low_h, .24, "wood_dark", role="wall")
    m.slats(1.85, low_y, 6.19, 48, .15, low_h, depth=.16, width=.075)
    m.glazing(9, low_y, 0, 12, low_h, side=True)
    for z, depth in ((-2.5, 7), (5, 2)):
        m.box(1.1, low_y, z, .24, low_h, depth, "plaster", role="wall")

    # Lower roof joins the upper floor without a daylight slit at the soffit.
    m.box(-4.28, 4.09, .1, 10.64, .14, 13.4, "wood", group="roof", role="roof")
    m.box(-4.28, 4.28, .1, 10.64, .24, 13.4, "plaster", group="roof", role="roof")
    m.box(-4.28, 4.42, .1, 10.64, .04, 13.4, "stone", group="roof", role="roof")

    # The only floor opening is the stairwell. A solid east strip closes the
    # former gap between the stairs and exterior wall.
    sx0, sx1, sz0, sz1 = STAIR_OPENING
    for x0, x1, z0, z1 in [(1.04, sx0, -6.36, 6.55),
                           (sx0, 9.47, -6.36, sz0),
                           (sx0, 9.47, sz1, 6.55),
                           (sx1, 9.47, sz0, sz1)]:
        x, z = (x0 + x1) / 2, (z0 + z1) / 2
        m.box(x, 4.21, z, x1 - x0, .38, z1 - z0, "plaster", group="upper", role="floor")
        m.box(x, 4.42, z, x1 - x0, .04, z1 - z0, "wood_light", group="upper", role="floor")
    high_y = (UPPER_LEVEL + UPPER_CEILING) / 2
    high_h = UPPER_CEILING - UPPER_LEVEL
    for x in (1.15, 9.35):
        m.box(x, high_y, -1.325, .22, high_h, 9.85, "plaster", group="upper", role="wall")
    m.box(5.255, high_y, -6.25, 8.43, high_h, .22, "plaster", group="upper", role="wall")
    bay_width = (9.35 - 1.15) / 3
    for i in range(3):
        m.glazing(1.15 + (i + .5) * bay_width, high_y, 3.6, bay_width, high_h, group="upper")
    m.slats(7.1, high_y, 3.9, 14, .17, high_h, depth=.24, width=.075, group="upper")
    m.box(5.255, 7.70, .075, 9.23, .16, 13.65, "wood", group="roof", role="roof")
    m.box(5.255, 7.88, .075, 9.23, .20, 13.65, "plaster", group="roof", role="roof")

    # A three-sided balcony guard closes both previously unguarded ends.
    rail_y, rail_h = UPPER_LEVEL + .56, 1.12
    m.box(5.25, rail_y, 6.48, 8.2, rail_h, .045, "glass", opacity=.20, group="upper", role="guard")
    m.box(5.25, UPPER_LEVEL + 1.13, 6.48, 8.28, .055, .065, "frame", group="upper", role="guard")
    for x in (1.15, 9.35):
        m.box(x, rail_y, 5.04, .045, rail_h, 2.88, "glass", opacity=.20, group="upper", role="guard")
        m.box(x, UPPER_LEVEL + 1.13, 5.04, .065, .055, 2.94, "frame", group="upper", role="guard")
        for z in (3.6, 6.48):
            m.box(x, rail_y, z, .055, rail_h, .055, "frame", group="upper", role="guard")
    m.box(5.25, rail_y, 6.48, .055, rail_h, .055, "frame", group="upper", role="guard")

    # Closed risers meet one another and the upper landing exactly.
    rise = (UPPER_LEVEL - GROUND_LEVEL) / 20
    run = (sz1 - sz0) / 20
    for i in range(20):
        top = GROUND_LEVEL + (i + 1) * rise
        z = sz1 - (i + .5) * run
        height = top - GROUND_LEVEL
        m.box(7.9, GROUND_LEVEL + height / 2, z, 1.65, height, run + .002, "wood", role="stair")
        m.box(8.80, top + .5, z, .035, 1, .035, "frame", role="guard")
    start = (8.80, GROUND_LEVEL + rise + 1, sz1 - run / 2)
    axis = (0, 19 * rise, -19 * run)
    m.shape("cylinder", start, (.05, (sum(v * v for v in axis)) ** .5, .05), "frame", axis=axis, role="guard")
    # Stairwell guard on the bedroom side; keep the rear landing open.
    m.box(7.02, UPPER_LEVEL + 1.05, .125, .05, .05, 7.8, "frame", group="upper", role="guard")
    for z in (-3.7, -1.1, 1.5, 3.95):
        m.box(7.02, UPPER_LEVEL + .52, z, .04, 1.04, .04, "frame", group="upper", role="guard")


def living_room(m):
    # Sunken-looking lounge, pale boucle sectional, low oak coffee table.
    m.box(-5.35, .30, 2.1, 5.8, .04, 4.25, "rug")
    m.box(-6.3, .54, 2.3, 3.6, .39, 1.1, "wood_dark")
    for x in (-7.7, -4.9):
        for z in (1.95, 2.65):
            m.box(x, .32, z, .12, .08, .12, "wood_dark")
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
    m.cylinder(-4.9, .55, .35, .16, .23, "stone")
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
        m.box(x, .785, -2.8, .10, 1.01, 1.35, "white")
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
    floor = UPPER_LEVEL
    m.box(4.3, floor + .03, -.4, 4.9, .04, 5.9, "rug")
    m.box(4.3, floor + .32, -.7, 2.8, .5, 3.9, "wood_dark")
    m.box(4.3, floor + .08, -.7, 2.4, .16, 3.5, "wood_dark")
    m.box(4.3, floor + .63, -.7, 2.75, .32, 3.85, "linen")
    m.box(4.3, floor + .88, -2.55, 3.0, 1.25, .16, "wood")
    m.box(4.3, floor + .83, .05, 2.78, .10, 2.15, "cushion")
    for x in (3.65, 4.95):
        m.box(x, floor + .9, -1.85, 1.04, .22, .72, "white")
    for x in (2.25, 6.35):
        m.box(x, floor + .45, -2.0, .75, .7, .65, "wood")
        m.box(x, floor + .08, -2.0, .55, .16, .45, "wood_dark")
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
    m.box(5.4, .22, 9.5, 5.8, .12, 4.4, "wood", group="landscape")
    for i in range(26):
        m.box(2.6 + i * .225, .281, 9.5, .012, .002, 4.4, "wood_dark", group="landscape")
    m.box(5.5, .85, 10, 2.6, .12, 1.3, "wood")
    for dx in (-.9, .9):
        m.box(5.5 + dx, .54, 10, .1, .52, .8, "wood_dark")
    for x in (4.7, 6.2):
        m.chair(x, GROUND_LEVEL, 8.9, 0, True)
        m.chair(x, GROUND_LEVEL, 11.1, pi, True)
    # Open steel pergola with timber rafters.
    for x in (2.5, 8.3):
        for z in (7.4, 11.8):
            m.box(x, 1.78, z, .09, 3, .09, "frame", group="pergola")
    for x in (2.5, 8.3):
        m.box(x, 3.35, 9.6, .12, .16, 4.7, "frame", group="pergola")
    for i in range(12):
        m.box(5.4, 3.4, 7.4 + i * .4, 6.1, .16, .07, "wood", group="pergola")
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
        "overview": {"pos": [26, 17, 33], "target": [0, 2.4, 3.2]},
        # An obstacle-free centreline, including a stair climb. Each point has
        # eye and look-at coordinates for the Python room camera presets.
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
