"""Minimal web entrypoint so the agent can run as a Railway service.

Serves health + status; the actual site work runs via cron/CLI. No web UI.
"""

from __future__ import annotations

import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from launchpad import state


class Handler(BaseHTTPRequestHandler):
    def _json(self, code: int, payload: dict) -> None:
        body = json.dumps(payload).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):  # noqa: N802
        if self.path == "/health":
            return self._json(200, {"status": "ok"})
        if self.path in ("/status", "/api/v1/status"):
            return self._json(200, {"sites": state.all_sites()})
        self._json(404, {"error": "not found"})

    def log_message(self, *args):  # quiet
        pass


def main() -> None:
    port = int(os.environ.get("PORT", "8000"))
    ThreadingHTTPServer(("0.0.0.0", port), Handler).serve_forever()


if __name__ == "__main__":
    main()
