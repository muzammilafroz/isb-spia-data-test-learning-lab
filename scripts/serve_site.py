"""Serve dist under the same base path used by GitHub Pages."""

from __future__ import annotations

import argparse
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
BASE = "/isb-spia-data-test-learning-lab"


class PagesHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(DIST), **kwargs)

    def _strip_base(self) -> None:
        if self.path == BASE:
            self.path = "/"
        elif self.path.startswith(f"{BASE}/"):
            self.path = self.path[len(BASE):]

    def do_GET(self):
        self._strip_base()
        return super().do_GET()

    def do_HEAD(self):
        self._strip_base()
        return super().do_HEAD()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()
    server = ThreadingHTTPServer(("127.0.0.1", args.port), PagesHandler)
    print(f"Serving {DIST} at http://127.0.0.1:{args.port}{BASE}/")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
