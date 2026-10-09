# RenewalFence

Local micro-tool for freelancers and small studios. It reads a CSV of client agreements and fences the auto-renew notice window before a retainer renews by silence.

Signature: Mourad.Soltani

No accounts, no third-party APIs, no data leaves the machine. Ship the Markdown brief to the client and import the ICS into any calendar.

## What it does

- Computes the last day you can give notice (`renewal_date` minus `notice_days`).
- Flags rows as `overdue`, `open` (inside the lead window), `safe`, or `lapsed`.
- Writes a client-ready Markdown brief, a machine summary JSON, and an ICS with notice deadlines and renewal dates.
- Exposes `GET /health` for a local process check.

## CSV columns

`client,agreement,renewal_date,notice_days,auto_renew,monthly_value,owner_email`

Dates are `YYYY-MM-DD`. `auto_renew` is `yes` or `no`.

## Run

```bash
python3 -m renewalfence report examples/retainers.csv --out out --as-of 2026-10-09 --lead-days 21
python3 -m renewalfence serve --port 8765
curl -s localhost:8765/health
python3 -m unittest discover -s tests -v
```

## Buyer notes

See `BUYER_NOTES.md` for handoff and `OUTREACH.md` for one-to-one templates. Do not bulk-send those templates.
