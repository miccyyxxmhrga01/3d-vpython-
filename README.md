# Caybin Dream House

A furnished, two-storey dream house built directly with Python's VPython API.
HTML and CSS provide the page design. VPython is the only 3D library, and all
project scene and camera code is Python. There is no custom JavaScript file.

The house has continuous floor-to-ceiling glazing, an oak entrance, solid stair
risers, a three-sided balcony guard, furnished rooms, and a recessed pool.
Shared floor and ceiling levels keep adjoining walls, windows, and slabs aligned.

## Run

From your fork's checkout, use Python 3.10 or newer and a current browser with
WebGL 2 enabled:

```powershell
python -m pip install -r requirements.txt
python main.py
```

The browser opens at **http://127.0.0.1:8765**. Keep Python running while
exploring. Press Ctrl+C in its terminal to stop. Use `python main.py --port 8770`
if the default port is occupied, or add `--no-browser` to open the page yourself.
VPython's scene uses a second local port, selected automatically; optionally
set it with `--scene-port 8771`.

After installation, the house works offline. The HTML page embeds VPython's
own view, and normal HTML form submissions send button actions to Python.
VPython internally supplies its browser runtime; you do not write or maintain
its JavaScript. No Node.js or frontend build is required. Open the server
address rather than opening `static/index.html` directly.

The requirements include a Setuptools compatibility bound because this VPython
release imports [`pkg_resources`, removed in Setuptools 82](https://setuptools.pypa.io/en/stable/deprecated/pkg_resources.html).

Use one house tab per Python run. VPython's native view is a live Python session;
restart `python main.py` if the scene is disconnected or the tab is reloaded.

## Explore

| Control | Action |
| --- | --- |
| Right mouse drag or Ctrl + left drag | Orbit using VPython's native camera |
| Scroll wheel | Zoom in and out |
| Shift + mouse drag | Pan the camera |
| + / − buttons | Zoom in and out without a wheel |
| Room names | Move to the room's interior camera |
| Explore inside | Move into the living room |
| Reset view | Restore the exterior camera |
| Toggle roof | Hide or restore the roof |
| Change light | Switch daylight / golden hour |

With the 3D view focused, arrow keys orbit, + / − zoom, and Home or Escape resets.
Tab and Enter operate the HTML buttons. VPython supplies touch camera gestures.
Camera input is immediate, with no automatic motion. The scene status displays
the current room, roof visibility, and lighting.

The concept is not a construction-ready CAD model. Camera movement is free and
can pass through walls; room shortcuts provide a convenient interior starting point.

## Edit the design

- **`house.py`** defines every wall, window, piece of furniture, plant, and pool
  element. Edit its `MATERIALS` or room functions to customize the home.
- **`viewer.py`** creates VPython boxes, cylinders, ellipsoids, and lights; it
  controls room cameras, zoom buttons, roof visibility, lighting, and keyboard input.
- **`static/index.html`** and **`static/style.css`** define the HTML/CSS interface.
- **`static/scene.css`** fits VPython's native view inside the page.
- **`main.py`** serves the page, accepts HTML form commands, and runs VPython.
- **`tests/`** checks model geometry and the Python control endpoint.

`GROUND_LEVEL`, `GROUND_CEILING`, `UPPER_LEVEL`, `UPPER_CEILING`, and
`STAIR_OPENING` in `house.py` define the shared architectural boundaries. Use
those values when changing walls or floors to avoid introducing new gaps.

Restart the server after editing the Python house. Export the model or run its checks:

```powershell
python main.py --export house.json
python -m unittest discover -s tests -v
```

The 13 checks cover scene generation, facade closure, upper-floor continuity,
the intentional stair opening, stair-to-landing contact, the pool basin, camera
clearance, and form commands submitted while the scene is still loading.

Only the Python source, `static/` assets, `tests/`, this README, requirements,
and `.gitignore` are needed in a fork. Generated previews, caches, and local
assistant configuration are excluded.
