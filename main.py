"""HTML/CSS interface with all scene and camera code written in Python/VPython."""
from __future__ import annotations

import argparse
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
from queue import Empty, Full, Queue
import socket
import threading
from urllib.parse import parse_qs, urlsplit
import webbrowser

from house import build_house

STATIC = Path(__file__).resolve().parent / "static"
ACTIONS = {"overview", "living", "kitchen", "bedroom", "terrace", "zoom-in", "zoom-out", "roof", "light"}


class HouseHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, commands, state, scene_url, **kwargs):
        self.commands, self.state, self.scene_url = commands, state, scene_url
        super().__init__(*args, directory=str(STATIC), **kwargs)

    def respond(self, data, content_type):
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        path = urlsplit(self.path).path
        if path in {"/", "/index.html"}:
            html = (STATIC / "index.html").read_text(encoding="utf-8")
            self.respond(html.replace("__SCENE_URL__", self.scene_url).encode(), "text/html; charset=utf-8")
        elif path == "/api/state":
            self.respond(json.dumps(self.state["value"]).encode(), "application/json; charset=utf-8")
        elif path in {"/style.css", "/scene.css", "/favicon.svg"}:
            super().do_GET()
        else:
            self.send_error(404)

    def do_POST(self):
        if urlsplit(self.path).path != "/command":
            self.send_error(404)
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if not 0 < length <= 1024:
                raise ValueError
            action = parse_qs(self.rfile.read(length).decode("utf-8")).get("action", [""])[0]
            if action not in ACTIONS:
                raise ValueError
        except (ValueError, UnicodeError):
            self.send_error(400, "Unknown camera command")
            return
        # Keep early clicks until VPython has finished building the scene.
        try:
            self.commands.put_nowait(action)
        except Full:
            self.send_error(503, "Too many pending controls; try again in a moment")
            return
        # An HTML form can submit to the hidden response frame without reloading
        # the VPython view. No project JavaScript is needed.
        self.send_response(204)
        self.end_headers()


def free_port():
    with socket.socket() as connection:
        connection.bind(("127.0.0.1", 0))
        return connection.getsockname()[1]


def main():
    parser = argparse.ArgumentParser(description="Explore an HTML/CSS dream house powered directly by Python VPython.")
    parser.add_argument("--port", type=int, default=8765, help="HTML/CSS interface port")
    parser.add_argument("--scene-port", type=int, help="VPython port; automatically chosen by default")
    parser.add_argument("--no-browser", action="store_true")
    parser.add_argument("--export", type=Path, metavar="FILE", help="Export the model as JSON and exit")
    args = parser.parse_args()
    model = build_house()
    if args.export:
        args.export.write_text(json.dumps(model, indent=2), encoding="utf-8")
        print(f"Exported {len(model['objects'])} objects to {args.export}")
        return

    commands = Queue(maxsize=64)
    state = {"value": {"ready": False, "message": "Waiting for the VPython view"}}
    scene_port = args.scene_port if args.scene_port is not None else free_port()
    scene_url = f"http://127.0.0.1:{scene_port}/"
    handler = partial(HouseHandler, commands=commands, state=state, scene_url=scene_url)
    try:
        server = ThreadingHTTPServer(("127.0.0.1", args.port), handler)
    except OSError as error:
        raise SystemExit(f"Cannot use interface port {args.port}: {error}\nTry: python main.py --port 8770") from error
    if scene_port == server.server_port:
        server.server_close()
        raise SystemExit("The interface and VPython scene need different ports.")
    with socket.socket() as probe:
        try:
            probe.bind(("127.0.0.1", scene_port))
        except OSError as error:
            server.server_close()
            raise SystemExit(f"Cannot use VPython port {scene_port}: {error}") from error
    url = f"http://127.0.0.1:{server.server_port}"
    threading.Thread(target=server.serve_forever, daemon=True).start()
    os.environ["VPYTHON_HTTP_PORT"] = str(scene_port)
    os.environ["VPYTHON_NO_LAUNCH_BROWSER"] = "1"
    print(f"\n  {model['name']}\n  Python + VPython for 3D; HTML + CSS for the page\n  Open {url}\n  Right-drag to orbit; scroll to zoom; Shift-drag to pan.\n  Keep this terminal running. Ctrl+C stops the application.\n", flush=True)
    if not args.no_browser:
        threading.Timer(.8, lambda: webbrowser.open(url)).start()
    try:
        from viewer import HouseViewer
        viewer = HouseViewer(model, url)
        state["value"] = viewer.snapshot()
        while True:
            viewer.vp.rate(30)
            for _ in range(20):
                try:
                    viewer.command(commands.get_nowait())
                except Empty:
                    break
            state["value"] = viewer.snapshot()
    except ImportError as error:
        raise SystemExit("Install VPython: python -m pip install -r requirements.txt") from error
    except KeyboardInterrupt:
        print("\nHouse viewer stopped.")
    finally:
        server.shutdown()
        server.server_close()


if __name__ == "__main__":
    main()
