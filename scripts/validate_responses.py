#!/usr/bin/env python3
"""Check collected data in ``responses/`` and report per-participant status.

Run this before analysis. It verifies that the two CSVs agree, that every
completed viewing looks sane, and that the realised randomisation is balanced.

Usage::

    python scripts/validate_responses.py
    python scripts/validate_responses.py --responses /path/to/responses
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def read_csv(path: Path) -> list[dict]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def check_participant(pdir: Path) -> tuple[list[str], dict]:
    """Return ``(problems, summary)`` for one participant directory."""
    problems: list[str] = []
    session_path = pdir / "session.json"

    if not session_path.exists():
        return [f"{pdir.name}: no session.json"], {}

    session = json.loads(session_path.read_text(encoding="utf-8"))
    viewings = read_csv(pdir / "viewings.csv")
    boundaries = read_csv(pdir / "boundaries.csv")

    total = len(session["schedule"])
    done = len(viewings)

    # Every boundary must belong to a viewing that was actually recorded.
    viewing_keys = {(v["video_id"], v["granularity"]) for v in viewings}
    orphans = {(b["video_id"], b["granularity"]) for b in boundaries} - viewing_keys
    if orphans:
        problems.append(f"{pdir.name}: boundaries with no matching viewing: {orphans}")

    # Press counts in viewings.csv must match the rows in boundaries.csv.
    counted: Counter = Counter()
    for b in boundaries:
        counted[(b["video_id"], b["granularity"])] += 1
    for v in viewings:
        key = (v["video_id"], v["granularity"])
        if counted[key] != int(v["n_presses"]):
            problems.append(
                f"{pdir.name}: {key} says n_presses={v['n_presses']} but "
                f"boundaries.csv has {counted[key]} rows"
            )

    # Nobody should be able to view the same video+granularity twice.
    dupes = [k for k, n in Counter(
        (v["video_id"], v["granularity"]) for v in viewings).items() if n > 1]
    if dupes:
        problems.append(f"{pdir.name}: duplicate viewings {dupes}")

    for v in viewings:
        if int(v["n_presses"]) == 0:
            problems.append(f"{pdir.name}: {v['video_id']}/{v['granularity']} "
                            "has ZERO boundaries")
        if int(v["blur_events"] or 0) > 0:
            problems.append(f"{pdir.name}: {v['video_id']}/{v['granularity']} "
                            f"had {v['blur_events']} tab switch(es)")
        # With playback controls the wall clock no longer tracks the video
        # clock -- pausing legitimately stretches it. What matters instead is
        # whether the participant actually reached the end.
        try:
            reached = float(v.get("max_time_reached_sec") or 0)
            dur = float(v["video_duration_sec"])
            if dur and reached / dur < 0.95:
                problems.append(
                    f"{pdir.name}: {v['video_id']}/{v['granularity']} only "
                    f"reached {reached:.0f}s of {dur:.0f}s "
                    f"({100 * reached / dur:.0f}%) - skipped ahead?"
                )
        except (ValueError, KeyError, TypeError):
            pass

    # Boundaries must be inside the video and monotonically ordered.
    by_viewing: dict[tuple, list[float]] = defaultdict(list)
    for b in boundaries:
        by_viewing[(b["video_id"], b["granularity"])].append(float(b["boundary_sec"]))
    for key, times in by_viewing.items():
        # Marks are stored in press order, and rewinding legitimately produces
        # out-of-order timestamps, so that is not an error. Near-duplicates
        # are: they usually mean the same boundary was marked twice after a
        # rewind.
        if any(t < 0 for t in times):
            problems.append(f"{pdir.name}: {key} has a negative timestamp")
        ordered = sorted(times)
        dupes = sum(1 for a, b in zip(ordered, ordered[1:]) if b - a < 0.5)
        if dupes:
            problems.append(
                f"{pdir.name}: {key} has {dupes} pair(s) of marks under 0.5 s "
                "apart - likely double-marked after a rewind"
            )

    # Coarse should not out-number fine on the same video.
    per_video: dict[str, dict[str, int]] = defaultdict(dict)
    for v in viewings:
        per_video[v["video_id"]][v["granularity"]] = int(v["n_presses"])
    inverted = [vid for vid, g in per_video.items()
                if "coarse" in g and "fine" in g and g["coarse"] > g["fine"]]
    if inverted:
        problems.append(
            f"{pdir.name}: more COARSE than FINE boundaries on {inverted} "
            "(possible instruction misunderstanding)"
        )

    first_granularity = {
        s["video_id"]: s["granularity"]
        for s in session["schedule"] if s["viewing_in_block"] == 1
    }
    summary = {
        "participant_id": session["participant_id"],
        "done": done,
        "total": total,
        "complete": done >= total,
        "comprehension_attempts": (session.get("comprehension") or {}).get("attempts"),
        "practice_attempts": len(session.get("practice", [])),
        "boundaries": len(boundaries),
        "pauses": sum(int(v.get("pause_count") or 0) for v in viewings),
        "seeks": sum(int(v.get("seek_count") or 0) for v in viewings),
        "first_granularity": first_granularity,
    }
    return problems, summary


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--responses", type=Path, default=ROOT / "responses")
    args = parser.parse_args()

    pdirs = sorted(p for p in args.responses.iterdir()
                   if p.is_dir() and (p / "session.json").exists())
    if not pdirs:
        print(f"No participant data in {args.responses}")
        return 0

    all_problems: list[str] = []
    summaries = []
    for pdir in pdirs:
        problems, summary = check_participant(pdir)
        all_problems += problems
        if summary:
            summaries.append(summary)

    print(f"{'participant':<16}{'progress':>10}{'marks':>8}{'pauses':>8}"
          f"{'seeks':>7}{'compr.':>8}{'practice':>10}")
    print("-" * 70)
    for s in summaries:
        flag = "" if s["complete"] else "  <- incomplete"
        print(f"{s['participant_id']:<16}{s['done']}/{s['total']:>8}"
              f"{s['boundaries']:>8}{s['pauses']:>8}{s['seeks']:>7}"
              f"{str(s['comprehension_attempts']):>8}"
              f"{s['practice_attempts']:>10}{flag}")

    # Realised counterbalancing: which granularity each video was first seen at.
    balance: dict[str, Counter] = defaultdict(Counter)
    for s in summaries:
        for video_id, granularity in s["first_granularity"].items():
            balance[video_id][granularity] += 1
    print("\nFirst-viewing granularity per video (want roughly 50/50):")
    for video_id in sorted(balance):
        c = balance[video_id]
        print(f"  {video_id}: coarse={c['coarse']}  fine={c['fine']}")

    print(f"\n{len(all_problems)} issue(s) found.")
    for p in all_problems:
        print(f"  ! {p}")

    return 1 if all_problems else 0


if __name__ == "__main__":
    sys.exit(main())
