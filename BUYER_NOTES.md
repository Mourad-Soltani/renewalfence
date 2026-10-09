# Buyer notes

Signature: Mourad.Soltani

## Asset

RenewalFence is a local Python tool (stdlib only) that turns a retainer CSV into a notice-window brief and an ICS calendar. It is intentionally small: one command, three output files, one health endpoint.

## Who pays

Freelance designers, dev shops, and bookkeepers who bill monthly retainers with 14–30 day auto-renew notice clauses and currently track them in a spreadsheet.

## Suggested price

$19 one-time for the CLI, or $9/month if you wrap the same functions in a hosted upload later. Do not add a database until a buyer asks for shared team access.

## Handoff checklist

- Repo, MIT license, and example CSV are included.
- Tests cover date math, ICS shape, and `/health`.
- No Stripe, no email sender, and no external API keys are wired in.
- Outreach file is templates only. Do not import a purchased list.

## Limits

This is not legal advice. Notice-day counts are calendar days, not business days. Timezone is floating local date in the ICS.
