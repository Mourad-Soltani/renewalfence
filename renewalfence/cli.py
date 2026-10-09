"""Command line. Signature: Mourad.Soltani"""

from __future__ import annotations

import argparse
import json
from datetime import date
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from renewalfence import __version__
from renewalfence.core import load_agreements, write_outputs


def health_payload() -> dict:
    return {"status": "ok", "service": "renewalfence", "version": __version__, "signature": "Mourad.Soltani"}


class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):  # noqa: N802
        if self.path.split("?", 1)[0] != "/health":
            body = b'{"error":"not found"}'
            self.send_response(404)
        else:
            body = json.dumps(health_payload()).encode()
            self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt, *args):
        return


def serve(port: int) -> None:
    server = ThreadingHTTPServer(("127.0.0.1", port), HealthHandler)
    print(json.dumps({"listening": port, "signature": "Mourad.Soltani"}))
    server.serve_forever()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="renewalfence")
    sub = parser.add_subparsers(dest="command", required=True)

    report = sub.add_parser("report")
    report.add_argument("csv")
    report.add_argument("--out", default="out")
    report.add_argument("--as-of", default=date.today().isoformat())
    report.add_argument("--lead-days", type=int, default=21)

    health = sub.add_parser("health")
    serve_cmd = sub.add_parser("serve")
    serve_cmd.add_argument("--port", type=int, default=8765)

    args = parser.parse_args(argv)
    if args.command == "health":
        print(json.dumps(health_payload()))
        return 0
    if args.command == "serve":
        serve(args.port)
        return 0
    as_of = date.fromisoformat(args.as_of)
    rows = load_agreements(Path(args.csv), as_of, args.lead_days)
    summary = write_outputs(rows, Path(args.out), as_of)
    print(json.dumps({"wrote": args.out, "count": summary["count"], "by_status": summary["by_status"]}))
    return 0
