"""LaunchPad CLI orchestrator.

    python -m launchpad.runner init-db
    python -m launchpad.runner status
    python -m launchpad.runner next --stage signup
    python -m launchpad.runner triage-load triage.json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from launchpad import config as cfg
from launchpad import state


def cmd_init(_args) -> None:
    state.init_db(cfg.load_sites())
    print(f"db ready: {len(cfg.load_sites())} sites")


def cmd_status(_args) -> None:
    sites = state.all_sites()
    from collections import Counter

    by_stage = Counter(s["stage"] for s in sites)
    by_status = Counter(s["status"] for s in sites)
    print("STAGE:", dict(by_stage))
    print("STATUS:", dict(by_status))
    for s in sites:
        flag = "FREE" if s["free_listing"] else ("PAID" if s.get("free_listing") is not None else "?")
        print(f"  #{s['id']:<3} {s['stage']:<8} {s['status']:<9} {s['platform'][:32]:<32} {flag} {s.get('submit_url') or ''}")


def cmd_next(args) -> None:
    sites = [s for s in state.all_sites() if s["stage"] == args.stage and s["status"] != "done"]
    if not sites:
        print(f"no sites pending at stage '{args.stage}'")
        return
    for s in sites[: (args.limit or 5)]:
        print(f"  #{s['id']:<3} {s['platform']:<30} {s['url']}")
    print(f"\n{len(sites)} pending at '{args.stage}'")


def cmd_triage_load(args) -> None:
    """Load a triage JSON array into the DB (classifies each site)."""
    data = json.loads(Path(args.file).read_text())
    count = 0
    for rec in data:
        sid = int(rec["id"])
        captcha = None if rec.get("captcha") is None else bool(rec["captcha"])
        free = None if rec.get("free_listing") is None else bool(rec["free_listing"])
        paid_only = bool(rec.get("paid_only"))
        stage = "done" if paid_only else "signup"
        state.set_stage(
            sid,
            stage,
            signup_method=rec.get("signup_method"),
            captcha=int(captcha) if captcha is not None else None,
            free_listing=int(free) if free is not None else None,
            submit_url=rec.get("submit_url"),
            notes=(rec.get("notes") or "")[:500],
            status="paid_only" if paid_only else ("pending" if free else "manual"),
        )
        state.log(sid, f"triage: {rec.get('signup_method')} captcha={captcha} free={free}")
        count += 1
    print(f"loaded {count} triage records")


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="launchpad")
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("init-db").set_defaults(fn=cmd_init)
    sub.add_parser("status").set_defaults(fn=cmd_status)
    nx = sub.add_parser("next")
    nx.add_argument("--stage", default="signup")
    nx.add_argument("--limit", type=int, default=5)
    nx.set_defaults(fn=cmd_next)
    tl = sub.add_parser("triage-load")
    tl.add_argument("file")
    tl.set_defaults(fn=cmd_triage_load)
    args = p.parse_args(argv)
    args.fn(args)
    return 0


if __name__ == "__main__":
    sys.exit(main())
