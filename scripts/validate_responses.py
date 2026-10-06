#!/usr/bin/env python3
"""Check collected data in ``responses/`` and report per-participant status.

Run this before analysis. It verifies that the two CSVs agree, that every
completed viewing looks sane, and that each participant watched the demos.

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
    all_viewings = read_csv(pdir / "viewings.csv")
    all_boundaries = read_csv(pdir / "boundaries.csv")

    # Practice rows share the files but are not data: they must not count
    # toward progress, and the main-viewing checks do not apply to them.
    viewings = [v for v in all_viewings if v.get("role", "main") == "main"]
    boundaries = [b for b in all_boundaries if b.get("role", "main") == "main"]
    practice = [v for v in all_viewings if v.get("role") == "practice"]

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
        # Marks are stored in press order, and dragging legitimately produces
        # out-of-order timestamps, so that is not an error. Near-duplicates
        # are: they usually mean the same boundary was marked twice.
        if any(t < 0 for t in times):
            problems.append(f"{pdir.name}: {key} has a negative timestamp")
        ordered = sorted(times)
        dupes = sum(1 for a, b in zip(ordered, ordered[1:]) if b - a < 0.5)
        if dupes:
            problems.append(
                f"{pdir.name}: {key} has {dupes} pair(s) of marks under 0.5 s "
                "apart - likely double-marked"
            )

    demo_views = [d for d in session.get("demos", [])
                  if d.get("status") == "completed"]
    if not session.get("demos_completed") and done:
        problems.append(f"{pdir.name}: annotated without finishing the demos")

    summary = {
        "participant_id": session["participant_id"],
        "done": done,
        "total": total,
        "complete": done >= total,
        "demo_views": len(demo_views),
        "practice_attempts": len(session.get("practice", [])),
        "boundaries": len(boundaries),
        "pauses": sum(int(v.get("pause_count") or 0) for v in viewings),
        "seeks": sum(int(v.get("seek_count") or 0) for v in viewings),
        "practice_rows": len(practice),
        "practice_marks": sum(int(v.get("n_presses") or 0) for v in practice),
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
          f"{'seeks':>7}{'demos':>8}{'prac.runs':>11}{'prac.marks':>12}")
    print("-" * 82)
    for s in summaries:
        flag = "" if s["complete"] else "  <- incomplete"
        print(f"{s['participant_id']:<16}{s['done']}/{s['total']:>8}"
              f"{s['boundaries']:>8}{s['pauses']:>8}{s['seeks']:>7}"
              f"{s['demo_views']:>8}"
              f"{s['practice_rows']:>11}{s['practice_marks']:>12}{flag}")

    print(f"\n{len(all_problems)} issue(s) found.")
    for p in all_problems:
        print(f"  ! {p}")

    return 1 if all_problems else 0


if __name__ == "__main__":
    sys.exit(main())
