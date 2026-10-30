# Caybin Dream House

A scrollable 3D dream house designed in Python: two modern volumes in concrete,
oak screens, floor-to-ceiling glazing, a pool, and a shaded terrace. Walk through
a furnished living room and kitchen, then climb the stairs to the bedroom.

## Run

Requires Python 3.10 or newer and a browser with WebGL 2 enabled (current Chrome,
Edge, or Firefox).

```powershell
python -m pip install -r requirements.txt
python main.py
```

The browser opens automatically at **http://127.0.0.1:8765**. Keep Python running
while exploring; press **Ctrl+C** in the terminal to stop it. After installation,
the viewer works offline: its 3D engine comes from the local VPython package.

If the port is occupied:

```powershell
python main.py --port 8766
```

## Explore

| Control | Action |
| --- | --- |
| Scroll down over the 3D view | Enter the house and follow the walkthrough |
| Scroll up | Retrace the route |
| Enter the house | Move to the entrance |
| Room names | Go to a room along the tour |
| Drag | Orbit outside; look around inside |
| W / A / S / D | Leave the tour and walk freely |
| Shift + W / A / S / D | Walk faster |
| Up / Down arrows | Move backward / forward along the tour |
| R | Hide or restore the roof |
| L | Switch daylight / golden hour |
| Escape or Reset view | Return to the exterior |

On a touch screen, use the **slider** to move through the house and **drag** to
look around. Pinching also advances or reverses the tour.

Free walking has simple wall collision checks. Use the guided route to climb
the staircase. It is a concept visualization, not a construction-ready CAD model.

## Change the design in Python

- **`house.py`** builds every wall, window, roof, stair, piece of furniture,
  plant, and pool element. Coordinates and dimensions are in metres; `y` is up.
- **`MATERIALS`** controls the colors. Edit `architecture()`, `living_room()`,
  `kitchen()`, `bedroom()`, or `terrace()` to change individual spaces.
- **`build_house()`** includes the walkthrough waypoints and room stops.
- **`main.py`** runs a local, read-only HTTP server and supplies the scene.
- **`static/viewer.js`** is a small display and camera adapter for VPython's
  bundled GlowScript engine; it contains no house construction code.
- **`static/style.css`** styles the viewer controls.

Restart `main.py` and reload the browser after editing the Python model.

Export the generated scene without starting the viewer:

```powershell
python main.py --export house.json
```

## Check the model

```powershell
python -m unittest discover -s tests -v
```

The checks validate scene serialization, deterministic generation, room stops,
and clearance of the guided camera route through the solid geometry.

## Rendering

The architecture is created in Python and displayed by the same GlowScript
WebGL engine bundled with [VPython](https://vpython.org/). Browser JavaScript
handles smooth camera movement and the interface. No Node.js installation or
JavaScript build command is needed to run the house.
