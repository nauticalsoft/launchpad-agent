# LaunchPad Agent

Automated **free-tier** product listing of **NHY-QR Digital Menu/Catalogue** (Nautical)
across the 67 sites in `launchpad/sites.csv`. One real account per site, one real
product. Human-in-the-loop via Telegram for the steps automation can't do (CAPTCHAs,
Google sign-in).

## Pipeline stages (per site)
1. **triage** — classify: hands-off / paid-only / manual (signup method, CAPTCHA, free listing, submit URL).
2. **signup** — create the account (unique password, stored locally, never in chat).
3. **submit** — fill the listing form from `product_kit.yaml`.
4. **verify** — read the confirmation email via the Gmail API (`+alias` matches the site).
5. **handoff** — pause on CAPTCHA / Google sign-in, resume from your phone.

## Layout
- `launchpad/product_kit.yaml` — single source of truth for every form field.
- `launchpad/sites.csv` — the worklist (from the master sheet).
- `launchpad/config.py` — loads the kit + sites.
- `launchpad/state.py` — per-site status store (SQLite by default; Postgres via `DATABASE_URL`).
- `launchpad/runner.py` — CLI: `init-db`, `status`, `next`, `triage-load`.

## Run
```bash
python -m launchpad.runner init-db
python -m launchpad.runner status
python -m launchpad.runner next --stage signup
```

## Boundaries
- One account per site for one product. No fake accounts.
- Free listings only — paid/featured are logged for a later decision, never bought.
- No automated upvoting / review-seeding / engagement farming.

Secrets (passwords, Gmail OAuth, nautical login) are stored locally / in env, never
committed and never sent through chat.
