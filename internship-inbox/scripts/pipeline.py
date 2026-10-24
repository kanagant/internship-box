#!/usr/bin/env python3
"""Exact date math for the Internship Inbox Skill.

Cubbie reads Gmail, Canvas and Calendar and writes what it found to JSON files, with every time in
ISO 8601 including the UTC offset (2026-10-27T14:00:00-07:00). This script cannot call Cubbie. It keeps no
saved state: the student's tracker lives in their own Google Sheet. --sample uses assets/sample_data.json.

Commands:
  triage    --rows FILE --now ISO        what needs attention: overdue, due soon, or gone quiet
  conflicts --targets FILE --busy FILE --now ISO [--buffer-hours N]
                                         coursework or events that clash with interviews and deadlines
  Add --sample to either command to use the bundled sample instead of files.

Exit codes: 0 ok, 2 bad arguments, unreadable file, or a time without a UTC offset.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

SAMPLE = Path(__file__).resolve().parent.parent / "assets" / "sample_data.json"
SOON_HOURS = 72
QUIET_DAYS = 14
CLOSED = {"rejected", "withdrawn", "offer accepted", "declined"}


def fail(message: str, code: int = 2):
    print(message, file=sys.stderr)
    sys.exit(code)


def parse_dt(text, label: str) -> datetime:
    try:
        value = datetime.fromisoformat(str(text).replace("Z", "+00:00"))
    except ValueError:
        fail(f"{label}: {text!r} is not an ISO 8601 time", 2)
    if value.tzinfo is None:
        fail(f"{label}: {text!r} has no UTC offset; include it, for example -07:00", 2)
    return value


def load(path: str):
    try:
        return json.loads(Path(path).read_text())
    except (OSError, ValueError) as exc:
        fail(f"Could not read {path}: {type(exc).__name__}", 2)


def need_list(data, label: str) -> list:
    if not isinstance(data, list) or not all(isinstance(x, dict) for x in data):
        fail(f"{label} must be a JSON list of objects", 2)
    return data


def hours_between(later: datetime, earlier: datetime) -> float:
    return round((later - earlier).total_seconds() / 3600, 1)


def cmd_triage(args) -> None:
    if args.sample:
        data = load(str(SAMPLE))
        rows, now = data["rows"], parse_dt(data["now"], "sample now")
    else:
        if not (args.rows and args.now):
            fail("Give --rows FILE and --now ISO, or --sample", 2)
        rows, now = need_list(load(args.rows), "rows"), parse_dt(args.now, "--now")
    out = []
    for row in rows:
        stage = str(row.get("stage", "")).strip().lower()
        if stage in CLOSED:
            continue
        label = f"{row.get('company')!r}"
        next_at = row.get("next_at")
        if next_at:
            left = hours_between(parse_dt(next_at, f"next_at of {label}"), now)
            if left < 0:
                out.append({**row, "flag": "overdue", "hours_left": left})
            elif left <= SOON_HOURS:
                out.append({**row, "flag": "due_soon", "hours_left": left})
            continue
        last = row.get("last_email")
        try:
            quiet = (now.date() - date.fromisoformat(last)).days if last else None
        except ValueError:
            fail(f"last_email of {label} must be YYYY-MM-DD", 2)
        if quiet is not None and quiet >= QUIET_DAYS and stage in {"applied", "unclear", ""}:
            out.append({**row, "flag": "quiet", "days_quiet": quiet})
    order = {"overdue": 0, "due_soon": 1, "quiet": 2}
    out.sort(key=lambda r: (order[r["flag"]], r.get("hours_left", 0) if r["flag"] != "quiet" else -r["days_quiet"]))
    print(json.dumps(out, indent=1, ensure_ascii=False)[:7500])


def cmd_conflicts(args) -> None:
    if args.sample:
        data = load(str(SAMPLE))
        targets, busy, now = data["targets"], data["busy"], parse_dt(data["now"], "sample now")
    else:
        if not (args.targets and args.busy and args.now):
            fail("Give --targets FILE, --busy FILE and --now ISO, or --sample", 2)
        targets = need_list(load(args.targets), "targets")
        busy = need_list(load(args.busy), "busy")
        now = parse_dt(args.now, "--now")
    buffer = timedelta(hours=args.buffer_hours)
    results = []
    for target in targets:
        label = f"{target.get('company')!r}"
        at = parse_dt(target.get("at"), f"at of {label}")
        if at < now:
            continue
        kind = target.get("kind")
        if kind == "interview":
            start, end = at, at + timedelta(minutes=int(target.get("duration_min") or 60))
            window_start, window_end = start - buffer, end + buffer
        elif kind == "assessment_deadline":
            # Work crowding the last 24 hours makes a deadline hard to hit.
            window_start, window_end = at - timedelta(hours=24), at
        else:
            fail(f"kind of {label} must be interview or assessment_deadline", 2)
        clashes = []
        for item in busy:
            item_at = parse_dt(item.get("at"), f"at of {item.get('title')!r}")
            item_end = parse_dt(item["end"], f"end of {item.get('title')!r}") if item.get("end") else item_at
            if item_at <= window_end and item_end >= window_start:
                clashes.append({"title": item.get("title"), "kind": item.get("kind"), "at": item["at"],
                                "hours_from_target": hours_between(item_at, at)})
        if clashes:
            clashes.sort(key=lambda c: abs(c["hours_from_target"]))
            results.append({"company": target.get("company"), "kind": kind, "at": target["at"], "clashes": clashes})
    print(json.dumps(results, indent=1, ensure_ascii=False)[:7500])


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="cmd", required=True)
    p_triage = sub.add_parser("triage")
    p_triage.add_argument("--rows")
    p_triage.add_argument("--now")
    p_triage.add_argument("--sample", action="store_true")
    p_triage.set_defaults(func=cmd_triage)
    p_conf = sub.add_parser("conflicts")
    p_conf.add_argument("--targets")
    p_conf.add_argument("--busy")
    p_conf.add_argument("--now")
    p_conf.add_argument("--buffer-hours", type=float, default=3.0)
    p_conf.add_argument("--sample", action="store_true")
    p_conf.set_defaults(func=cmd_conflicts)
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
