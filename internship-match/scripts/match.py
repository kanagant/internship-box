#!/usr/bin/env python3
"""Filter and rank internship postings for one student, and remember what was already shown.

Cubbie reads the postings and the student's profile and writes them to JSON files. This script cannot call
Cubbie. It applies the same eligibility rules every time, scores skill overlap, and reports why a posting was
dropped. Saved state (ids already shown) lives under HOME (~/.config/internship-match/seen.json), which survives
restarts and Skill updates. --sample uses assets/sample_data.json and never reads or writes saved state.

Commands:
  rank --profile FILE --postings FILE --today YYYY-MM-DD [--limit N]
  rank --sample
  mark --ids ID1,ID2          record these ids as shown

Profile fields: majors (list), year (freshman|sophomore|junior|senior|graduate), grad_term (YYYY-MM, optional),
skills (list), gpa (optional), needs_sponsorship (true|false|null), locations (optional list).
Posting fields: company, title, url, location, deadline (YYYY-MM-DD or null), start (YYYY-MM, optional), source,
verified_open (true|false|null), class_years (list|null), majors (list|null), gpa_min (number|null),
sponsorship (true|false|null), requires_enrolled (true|false|null), required_skills, preferred_skills.

Exit codes: 0 ok, 2 bad arguments or unreadable file, 3 saved state unreadable or unwritable.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import date
from pathlib import Path

SAMPLE = Path(__file__).resolve().parent.parent / "assets" / "sample_data.json"
YEARS = ["freshman", "sophomore", "junior", "senior", "graduate"]


def state_file() -> Path:
    return Path.home() / ".config" / "internship-match" / "seen.json"


def fail(message: str, code: int = 2):
    print(message, file=sys.stderr)
    sys.exit(code)


def load(path) -> object:
    try:
        return json.loads(Path(path).read_text())
    except (OSError, ValueError) as exc:
        fail(f"Could not read {path}: {type(exc).__name__}", 2)


def norm(items) -> list:
    return [str(x).strip().lower() for x in (items or []) if str(x).strip()]


def posting_id(p: dict) -> str:
    raw = "|".join(str(p.get(k, "")).strip().lower() for k in ("company", "title", "url"))
    return hashlib.sha1(raw.encode()).hexdigest()[:10]


def load_seen() -> set:
    path = state_file()
    if not path.exists():
        return set()
    try:
        return set(json.loads(path.read_text()))
    except (OSError, ValueError):
        fail("Saved state is unreadable; repeats are possible", 3)


def save_seen(ids: set) -> None:
    path = state_file()
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(sorted(ids)))
    except OSError:
        fail("Could not save state; repeats are possible", 3)


def parse_day(text, label: str) -> date:
    try:
        return date.fromisoformat(text)
    except (TypeError, ValueError):
        fail(f"{label} must be YYYY-MM-DD, got {text!r}", 2)


def check(profile: dict, p: dict, today: date):
    """Return (drop_reason or None, confirm list)."""
    confirm = []
    if p.get("verified_open") is False:
        return "closed", confirm
    if p.get("verified_open") is None:
        confirm.append("couldn't confirm it is still open")
    if p.get("deadline"):
        if parse_day(p["deadline"], f"deadline of {p.get('company')!r}") < today:
            return "deadline passed", confirm
    else:
        confirm.append("no deadline listed (may be rolling)")

    years = norm(p.get("class_years"))
    year = str(profile.get("year", "")).strip().lower()
    if years:
        if year not in YEARS:
            confirm.append("tell me your class year to check eligibility")
        elif year not in years:
            return "class year", confirm

    majors = norm(p.get("majors"))
    if majors and not ({"any", "all"} & set(majors)):
        mine = norm(profile.get("majors"))
        if mine and not any(m in w or w in m for m in mine for w in majors):
            return "major", confirm

    gpa_min = p.get("gpa_min")
    if isinstance(gpa_min, (int, float)):
        gpa = profile.get("gpa")
        if isinstance(gpa, (int, float)):
            if gpa < gpa_min:
                return "gpa", confirm
        else:
            confirm.append(f"confirm your GPA meets {gpa_min}")

    if p.get("sponsorship") is False:
        if profile.get("needs_sponsorship") is True:
            return "work authorization", confirm
        if profile.get("needs_sponsorship") is None:
            confirm.append("confirm work authorization: this posting does not sponsor")

    if p.get("requires_enrolled") is True and p.get("start") and profile.get("grad_term"):
        if str(profile["grad_term"]) < str(p["start"]):
            return "graduates before start", confirm
    elif p.get("requires_enrolled") is None:
        confirm.append("confirm whether you must still be enrolled at the start")
    return None, confirm


def score(profile: dict, p: dict):
    mine = set(norm(profile.get("skills")))
    required, preferred = norm(p.get("required_skills")), norm(p.get("preferred_skills"))
    matched = [s for s in required + preferred if s in mine]
    missing = [s for s in required if s not in mine]
    base = (len([s for s in required if s in mine]) / len(required)) if required else 0.5
    bonus = 0.2 * (len([s for s in preferred if s in mine]) / len(preferred)) if preferred else 0.0
    places = norm(profile.get("locations"))
    loc = str(p.get("location", "")).lower()
    place_bonus = 0.1 if places and any(x in loc for x in places) else 0.0
    return round(min(1.0, base + bonus + place_bonus), 2), matched, missing


def cmd_rank(args) -> None:
    if args.sample:
        data = load(SAMPLE)
        profile, postings, today, seen = data["profile"], data["postings"], parse_day(data["today"], "sample today"), set()
    else:
        if not (args.profile and args.postings and args.today):
            fail("Give --profile, --postings and --today, or --sample", 2)
        profile, postings = load(args.profile), load(args.postings)
        today, seen = parse_day(args.today, "--today"), load_seen()
    if not isinstance(profile, dict) or not isinstance(postings, list):
        fail("profile must be an object and postings a list", 2)
    results, dropped = [], {}
    for p in postings:
        if not isinstance(p, dict):
            fail("every posting must be an object", 2)
        pid = posting_id(p)
        if pid in seen:
            dropped["already shown"] = dropped.get("already shown", 0) + 1
            continue
        reason, confirm = check(profile, p, today)
        if reason:
            dropped[reason] = dropped.get(reason, 0) + 1
            continue
        s, matched, missing = score(profile, p)
        results.append({"id": pid, "company": p.get("company"), "title": p.get("title"), "url": p.get("url"),
                        "location": p.get("location"), "deadline": p.get("deadline"), "source": p.get("source"),
                        "score": s, "matched_skills": matched, "missing_skills": missing, "confirm": confirm})
    results.sort(key=lambda r: (-r["score"], r["deadline"] is None, r["deadline"] or ""))
    print(json.dumps({"results": results[: args.limit], "dropped": dropped, "total_considered": len(postings)},
                     indent=1, ensure_ascii=False))


def cmd_mark(args) -> None:
    ids = {i.strip() for i in args.ids.split(",") if i.strip()}
    if not ids:
        fail("Give at least one id with --ids", 2)
    save_seen(load_seen() | ids)
    print(f"Recorded {len(ids)} id(s) as shown")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="cmd", required=True)
    p_rank = sub.add_parser("rank")
    p_rank.add_argument("--profile")
    p_rank.add_argument("--postings")
    p_rank.add_argument("--today")
    p_rank.add_argument("--limit", type=int, default=10)
    p_rank.add_argument("--sample", action="store_true")
    p_rank.set_defaults(func=cmd_rank)
    p_mark = sub.add_parser("mark")
    p_mark.add_argument("--ids", required=True)
    p_mark.set_defaults(func=cmd_mark)
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
