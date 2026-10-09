"""Core notice-window math. Signature: Mourad.Soltani"""

from __future__ import annotations

import csv
import json
from dataclasses import asdict, dataclass
from datetime import date, datetime, timedelta
from pathlib import Path


REQUIRED = [
    "client",
    "agreement",
    "renewal_date",
    "notice_days",
    "auto_renew",
    "monthly_value",
    "owner_email",
]


@dataclass
class Agreement:
    client: str
    agreement: str
    renewal_date: str
    notice_days: int
    auto_renew: bool
    monthly_value: float
    owner_email: str
    notice_deadline: str
    days_to_notice: int
    status: str


def parse_date(value: str) -> date:
    return datetime.strptime(value.strip(), "%Y-%m-%d").date()


def classify(renewal: date, notice_deadline: date, auto_renew: bool, as_of: date, lead_days: int) -> str:
    if as_of > renewal:
        return "lapsed"
    if auto_renew and as_of > notice_deadline:
        return "overdue"
    if (notice_deadline - as_of).days <= lead_days:
        return "open"
    return "safe"


def load_agreements(path: Path, as_of: date, lead_days: int) -> list[Agreement]:
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        missing = [name for name in REQUIRED if name not in (reader.fieldnames or [])]
        if missing:
            raise ValueError(f"missing columns: {', '.join(missing)}")
        rows: list[Agreement] = []
        for raw in reader:
            if not (raw.get("client") or "").strip():
                continue
            renewal = parse_date(raw["renewal_date"])
            notice_days = int(raw["notice_days"])
            if notice_days < 0:
                raise ValueError("notice_days must be >= 0")
            deadline = renewal - timedelta(days=notice_days)
            auto = raw["auto_renew"].strip().lower() in {"yes", "true", "1", "y"}
            rows.append(
                Agreement(
                    client=raw["client"].strip(),
                    agreement=raw["agreement"].strip(),
                    renewal_date=renewal.isoformat(),
                    notice_days=notice_days,
                    auto_renew=auto,
                    monthly_value=float(raw["monthly_value"]),
                    owner_email=raw["owner_email"].strip(),
                    notice_deadline=deadline.isoformat(),
                    days_to_notice=(deadline - as_of).days,
                    status=classify(renewal, deadline, auto, as_of, lead_days),
                )
            )
    return rows


def to_markdown(rows: list[Agreement], as_of: date) -> str:
    lines = [
        "# RenewalFence notice brief",
        "",
        "Signature: Mourad.Soltani",
        "",
        f"As of {as_of.isoformat()}. Calendar-day notice windows. Not legal advice.",
        "",
        "| Client | Agreement | Notice deadline | Renewal | Status | Monthly |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        lines.append(
            f"| {row.client} | {row.agreement} | {row.notice_deadline} | {row.renewal_date} | {row.status} | {row.monthly_value:.2f} |"
        )
    exposed = sum(row.monthly_value for row in rows if row.status in {"overdue", "open"})
    lines.extend(["", f"Monthly value inside an open or overdue window: {exposed:.2f}", ""])
    return "\n".join(lines)


def _ics_stamp(day: date) -> str:
    return day.strftime("%Y%m%d")


def to_ics(rows: list[Agreement]) -> str:
    chunks = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//Mourad.Soltani//RenewalFence//EN",
        "CALSCALE:GREGORIAN",
    ]
    for index, row in enumerate(rows, start=1):
        notice = parse_date(row.notice_deadline)
        renewal = parse_date(row.renewal_date)
        chunks.extend(
            [
                "BEGIN:VEVENT",
                f"UID:notice-{index}@renewalfence.local",
                f"DTSTAMP:{_ics_stamp(date.today())}T000000Z",
                f"DTSTART;VALUE=DATE:{_ics_stamp(notice)}",
                f"SUMMARY:Notice deadline — {row.client}",
                f"DESCRIPTION:Last calendar day to give notice on {row.agreement}. Status {row.status}.",
                "END:VEVENT",
                "BEGIN:VEVENT",
                f"UID:renewal-{index}@renewalfence.local",
                f"DTSTAMP:{_ics_stamp(date.today())}T000000Z",
                f"DTSTART;VALUE=DATE:{_ics_stamp(renewal)}",
                f"SUMMARY:Renewal — {row.client}",
                f"DESCRIPTION:{row.agreement} renews. Auto-renew={'yes' if row.auto_renew else 'no'}.",
                "END:VEVENT",
            ]
        )
    chunks.append("END:VCALENDAR")
    return "\n".join(chunks) + "\n"


def write_outputs(rows: list[Agreement], out_dir: Path, as_of: date) -> dict:
    out_dir.mkdir(parents=True, exist_ok=True)
    report = to_markdown(rows, as_of)
    ics = to_ics(rows)
    summary = {
        "signature": "Mourad.Soltani",
        "as_of": as_of.isoformat(),
        "count": len(rows),
        "by_status": {
            status: sum(1 for row in rows if row.status == status)
            for status in ("overdue", "open", "safe", "lapsed")
        },
        "agreements": [asdict(row) for row in rows],
    }
    (out_dir / "brief.md").write_text(report, encoding="utf-8")
    (out_dir / "notice.ics").write_text(ics, encoding="utf-8")
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return summary
