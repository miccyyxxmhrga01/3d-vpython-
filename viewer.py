"""Render and control the house using the Python VPython API only."""
from __future__ import annotations

from html import escape
from math import pi


class HouseViewer:
    def __init__(self, model, app_url):
        import vpython as vp

        self.vp = vp
        self.model = model
        self.groups = {}
        self.view = "overview"
        self.roof_hidden = False
        self.evening = False
        self.scene = vp.scene
        self.scene.width = 1100
        self.scene.height = 760
        self.scene.autoscale = False
        self.scene.userspin = True
        self.scene.userzoom = True
        self.scene.userpan = True
        self.scene.resizable = False
        self.scene.background = self.color("#e4e6dc")
        self.scene.ambient = vp.vec(.63, .63, .59)
        self.scene.title = f'<link rel="stylesheet" href="{escape(app_url)}/scene.css">'
        self.status = vp.wtext(pos=self.scene.title_anchor, text='<span class="scene-status">Building your dream house...</span>')
        self.scene.lights = []
        self.key_light = vp.distant_light(canvas=self.scene, direction=vp.vec(-.5, 1, .8), color=vp.vec(.57, .53, .43))
        self.fill_light = vp.distant_light(canvas=self.scene, direction=vp.vec(.8, .3, -.5), color=vp.vec(.19, .22, .20))
        for index, item in enumerate(model["objects"]):
            self.create_object(item)
            if index % 100 == 99:
                vp.rate(60)
        self.set_view("overview")
        self.scene.bind("keydown", self.on_key)

    def color(self, value):
        return self.vp.vec(*(int(value[i:i + 2], 16) / 255 for i in (1, 3, 5)))

    def create_object(self, item):
        vp = self.vp
        position = vp.vec(*item["pos"])
        options = dict(canvas=self.scene, pos=position,
                       color=self.color(self.model["materials"][item["material"]]),
                       opacity=item.get("opacity", 1), emissive=item.get("emissive", False),
                       shininess=.7 if item["material"] in {"metal", "brass", "glass", "water"} else 0)
        if item["kind"] == "cylinder":
            options["axis"] = vp.vec(*item.get("axis", (0, item["size"][1], 0)))
            options["radius"] = item["size"][0] / 2
            obj = vp.cylinder(**options)
        else:
            options["size"] = vp.vec(*item["size"])
            constructor = {"box": vp.box, "ellipsoid": vp.ellipsoid}[item["kind"]]
            obj = constructor(**options)
        if item.get("rotation"):
            obj.rotate(angle=item["rotation"], axis=vp.vec(0, 1, 0), origin=position)
        self.groups.setdefault(item["group"], []).append(obj)

    def set_view(self, view):
        if view == "overview":
            camera = self.model["overview"]
            name = "Exterior overview"
        elif view == "terrace":
            camera = self.model["terrace"]
            name = "Pool & terrace"
        else:
            stop = next(stop for stop in self.model["stops"] if stop["id"] == view)
            scaled = stop["progress"] * (len(self.model["route"]) - 1)
            index = min(int(scaled), len(self.model["route"]) - 2)
            amount = scaled - index
            a, b = self.model["route"][index:index + 2]
            camera = {key: [x + (y - x) * amount for x, y in zip(a[key], b[key])] for key in ("pos", "target")}
            name = stop["name"]
        self.view = view
        self.view_name = name
        self.scene.fov = .8 if view == "overview" else 1.15
        self.scene.up = self.vp.vec(0, 1, 0)
        self.scene.camera.pos = self.vp.vec(*camera["pos"])
        self.scene.camera.axis = self.vp.vec(*camera["target"]) - self.scene.camera.pos
        self.update_status()

    def zoom(self, factor):
        # VPython's range is also updated by its built-in scroll-wheel control.
        self.scene.range = max(.18, min(70, self.scene.range * factor))

    def update_status(self):
        roof = "Roof hidden" if self.roof_hidden else "Roof visible"
        light = "Golden hour" if self.evening else "Daylight"
        self.status.text = f'<span class="scene-status" role="status">{escape(self.view_name)} · {roof} · {light}</span>'

    def command(self, action):
        if action in {"overview", "living", "kitchen", "bedroom", "terrace"}:
            self.set_view(action)
        elif action == "zoom-in":
            self.zoom(.82)
        elif action == "zoom-out":
            self.zoom(1 / .82)
        elif action == "roof":
            self.roof_hidden = not self.roof_hidden
            for obj in self.groups.get("roof", []):
                obj.visible = not self.roof_hidden
            self.update_status()
        elif action == "light":
            self.evening = not self.evening
            self.scene.background = self.color("#d5caba" if self.evening else "#e4e6dc")
            self.scene.ambient = self.vp.vec(.44, .39, .31) if self.evening else self.vp.vec(.63, .63, .59)
            self.key_light.color = self.vp.vec(.78, .54, .32) if self.evening else self.vp.vec(.57, .53, .43)
            self.fill_light.color = self.vp.vec(.19, .20, .24) if self.evening else self.vp.vec(.19, .22, .20)
            self.update_status()

    def on_key(self, event):
        if event.key in {"+", "="}:
            self.zoom(.82)
        elif event.key == "-":
            self.zoom(1 / .82)
        elif event.key in {"home", "escape"}:
            self.set_view("overview")
        elif event.key in {"left", "right", "up", "down"}:
            horizontal = event.key in {"left", "right"}
            angle = pi / 30 * (1 if event.key in {"left", "up"} else -1)
            axis = self.vp.vec(0, 1, 0) if horizontal else self.vp.cross(self.scene.forward, self.scene.up)
            self.scene.camera.rotate(angle=angle, axis=axis, origin=self.scene.center)

    def snapshot(self):
        as_list = lambda vector: [float(vector.x), float(vector.y), float(vector.z)]
        return {"ready": True, "view": self.view, "objects": sum(map(len, self.groups.values())),
                "position": as_list(self.scene.camera.pos), "axis": as_list(self.scene.camera.axis),
                "forward": as_list(self.scene.forward), "range": float(self.scene.range),
                "roof_hidden": self.roof_hidden, "evening": self.evening}
