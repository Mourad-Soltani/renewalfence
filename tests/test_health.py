"""Health and notice-window tests. Signature: Mourad.Soltani"""

import json
import threading
import unittest
import urllib.request
from datetime import date
from pathlib import Path
from tempfile import TemporaryDirectory

from renewalfence.cli import health_payload, serve
from renewalfence.core import load_agreements, write_outputs


CSV = """client,agreement,renewal_date,notice_days,auto_renew,monthly_value,owner_email
North Studio,Brand retainer,2026-10-20,14,yes,1800,ada@north.example
South Co,Care plan,2026-11-10,14,yes,900,lee@south.example
Old Client,Archive,2026-09-01,7,no,400,old@example.com
"""


class HealthTests(unittest.TestCase):
    def test_health_payload(self):
        body = health_payload()
        self.assertEqual(body["status"], "ok")
        self.assertEqual(body["signature"], "Mourad.Soltani")
        self.assertEqual(body["service"], "renewalfence")

    def test_health_endpoint(self):
        thread = threading.Thread(target=serve, kwargs={"port": 8766}, daemon=True)
        thread.start()
        last = None
        for _ in range(20):
            try:
                with urllib.request.urlopen("http://127.0.0.1:8766/health", timeout=1) as response:
                    payload = json.loads(response.read().decode())
                self.assertEqual(response.status, 200)
                self.assertEqual(payload["status"], "ok")
                return
            except Exception as exc:  # noqa: BLE001
                last = exc
        self.fail(f"health endpoint did not come up: {last}")

    def test_report_statuses_and_ics(self):
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "retainers.csv"
            path.write_text(CSV, encoding="utf-8")
            rows = load_agreements(path, date(2026, 10, 9), 21)
            by_client = {row.client: row for row in rows}
            self.assertEqual(by_client["North Studio"].status, "overdue")
            self.assertEqual(by_client["North Studio"].notice_deadline, "2026-10-06")
            self.assertEqual(by_client["South Co"].status, "open")
            self.assertEqual(by_client["Old Client"].status, "lapsed")
            summary = write_outputs(rows, Path(tmp) / "out", date(2026, 10, 9))
            ics = (Path(tmp) / "out" / "notice.ics").read_text(encoding="utf-8")
            self.assertIn("BEGIN:VCALENDAR", ics)
            self.assertIn("Notice deadline — North Studio", ics)
            self.assertEqual(summary["signature"], "Mourad.Soltani")
            self.assertEqual(summary["by_status"]["overdue"], 1)


if __name__ == "__main__":
    unittest.main()
