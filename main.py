"""Run Caybin Dream House, a Python-designed modern house: python main.py.

The entire architectural model is built in house.py. This small local server
supplies that model and VPython's bundled WebGL engine to the browser viewer.
No internet connection, JavaScript build step, or cloud service is needed.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import threading
from urllib.parse import urlsplit
import webbrowser

from house import build_house

ROOT = Path(__file__).resolve().parent
STATIC = ROOT / "static"


def vpython_assets() -> Path:
    spec = importlib.util.find_spec("vpython")
    if spec is None or spec.origin is None:
        raise SystemExit("Install the 3D engine first: python -m pip install -r requirements.txt")
    return Path(spec.origin).parent / "vpython_libraries"


class HouseHandler(SimpleHTTPRequestHandler):
    """Serve an explicit asset directory and a read-only Python scene endpoint."""

    def __init__(self, *args, model: bytes, vendor: Path, **kwargs):
        self.model = model
        self.vendor = vendor
        super().__init__(*args, directory=str(STATIC), **kwargs)

    def do_GET(self):
        path = urlsplit(self.path).path
        if path == "/api/house":
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(self.model)))
            self.end_headers()
            self.wfile.write(self.model)
            return
        if path.startswith("/vendor/"):
            name = path.removeprefix("/vendor/")
            if name not in {"glow.min.js", "jquery.min.js", "jquery-ui.custom.min.js", "Roboto-Medium.ttf"}:
                self.send_error(404)
                return
            asset = self.vendor.parent / "vpython_data" / name if name.endswith(".ttf") else self.vendor / name
            data = asset.read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", "font/ttf" if name.endswith(".ttf") else "text/javascript; charset=utf-8")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)
            return
        if path not in {"/", "/index.html", "/style.css", "/viewer.js", "/favicon.svg"}:
            self.send_error(404)
            return
        super().do_GET()


def main():
    parser = argparse.ArgumentParser(description="Explore Caybin Dream House, a Python-designed modern house.")
    parser.add_argument("--port", type=int, default=8765, help="Local port (default: 8765)")
    parser.add_argument("--no-browser", action="store_true", help="Do not open a browser automatically")
    parser.add_argument("--export", type=Path, metavar="FILE", help="Export the Python model as JSON and exit")
    args = parser.parse_args()
    model = build_house()
    if args.export:
        args.export.write_text(json.dumps(model, indent=2), encoding="utf-8")
        print(f"Exported {len(model['objects'])} objects to {args.export}")
        return
    handler = partial(HouseHandler, model=json.dumps(model).encode(), vendor=vpython_assets())
    try:
        server = ThreadingHTTPServer(("127.0.0.1", args.port), handler)
    except OSError as error:
        raise SystemExit(f"Cannot use port {args.port}: {error}\nTry: python main.py --port 8766") from error
    url = f"http://127.0.0.1:{server.server_port}"
    print(f"\n  {model['name']}\n  {len(model['objects'])} Python-built objects\n  Open {url}\n  Press Ctrl+C to stop.\n", flush=True)
    if not args.no_browser:
        threading.Timer(0.6, lambda: webbrowser.open(url)).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nHouse viewer stopped.")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
