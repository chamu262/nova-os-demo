"""A tiny local web server (Python standard library only)."""
import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from .team import Team

STATIC = Path(__file__).parent / "static"


def make_handler(team: Team):
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, fmt, *args):
            pass

        def _send(self, code, body, ctype="application/json"):
            data = body if isinstance(body, bytes) else json.dumps(body).encode()
            self.send_response(code)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def do_GET(self):
            path = self.path.split("?")[0]
            if path == "/api/state":
                return self._send(200, team.snapshot())
            if path == "/api/health":
                return self._send(200, {"ok": True, "mode": team.llm.name})
            if path in ("/", "/index.html"):
                return self._send(200, (STATIC / "index.html").read_bytes(), "text/html; charset=utf-8")
            self._send(404, {"error": "not found"})

        def do_POST(self):
            try:
                length = int(self.headers.get("Content-Length", 0))
                body = json.loads(self.rfile.read(length) or b"{}")
                if self.path == "/api/chat":
                    return self._send(200, team.handle(body.get("message", "")))
                if self.path.startswith("/api/decisions/"):
                    did = int(self.path.rsplit("/", 1)[1])
                    return self._send(200, team.decide(did, bool(body.get("approve"))))
                self._send(404, {"error": "not found"})
            except KeyError:
                self._send(404, {"error": "no such decision"})
            except (ValueError, json.JSONDecodeError) as exc:
                self._send(400, {"error": str(exc)})

    return Handler


def serve(host="127.0.0.1", port=None):
    port = int(port or os.environ.get("PORT", 7878))
    team = Team()
    httpd = ThreadingHTTPServer((host, port), make_handler(team))
    print(f"Nova OS running in {team.llm.name} mode → http://{host}:{port}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
