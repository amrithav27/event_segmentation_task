#!/usr/bin/env python3
"""Stage Ego4D Moment Queries clips into ``static/videos/`` for the Streamlit app.

Reads ``stimuli/videos.csv`` and, for every row, produces
``static/videos/<video_id>.mp4`` from the local Ego4D download:

* moments clips -- from ``<EGO4D_ROOT>/v2/clip_256ss/<clip_uid>.mp4``
* longer stimuli and the practice clip -- from
  ``<EGO4D_ROOT>/v2/video_540ss/<source_video_uid>.mp4``, since no moments clip
  exceeds 480 s

Every output is normalised to the same form: H.264, 256 px tall, no audio
track, and ``-movflags +faststart`` so the browser can start playing before the
whole file has downloaded.

Usage::

    python scripts/prepare_stimuli.py                 # default ~/ego4d_data
    python scripts/prepare_stimuli.py --ego4d-root /path/to/ego4d_data
    python scripts/prepare_stimuli.py --force         # re-stage existing files
"""

from __future__ import annotations

import argparse
import csv
import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MANIFEST = ROOT / "stimuli" / "videos.csv"
OUT_DIR = ROOT / "static" / "videos"

# The practice clip is cut from this offset in the source video.
PRACTICE_START_SEC = 120.0


def require_ffmpeg() -> None:
    for tool in ("ffmpeg", "ffprobe"):
        if shutil.which(tool) is None:
            sys.exit(f"error: {tool} not found on PATH. Install ffmpeg and retry.")


def probe_duration(path: Path) -> float:
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "csv=p=0", str(path)],
        capture_output=True, text=True, check=True,
    )
    return float(out.stdout.strip())


def run_ffmpeg(args: list[str]) -> None:
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", *args], check=True)


#: Every stimulus is presented at this height, so a 540p full video does not
#: look sharper than the 256p moments clips and bias attention.
TARGET_HEIGHT = 256


def stage_downscaled(src: Path, dst: Path, start: float | None = None,
                     duration: float | None = None) -> None:
    """Re-encode a full 540p video down to the common stimulus height.

    Also used to cut the practice clip. Audio is dropped outright: the study
    is run muted, and shipping silent files removes any chance of a
    participant hearing something the others did not.
    """
    args = []
    if start is not None:
        args += ["-ss", str(start)]
    args += ["-i", str(src)]
    if duration is not None:
        args += ["-t", str(duration)]
    args += ["-vf", f"scale=-2:{TARGET_HEIGHT}", "-c:v", "libx264",
             "-preset", "veryfast", "-crf", "23", "-an",
             "-movflags", "+faststart", str(dst)]
    run_ffmpeg(args)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ego4d-root", type=Path, default=Path.home() / "ego4d_data")
    parser.add_argument("--force", action="store_true",
                        help="re-stage videos that are already present")
    args = parser.parse_args()

    require_ffmpeg()
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    clip_dir = args.ego4d_root / "v2" / "clip_256ss"
    video_dir = args.ego4d_root / "v2" / "video_540ss"

    staged, skipped, missing = [], [], []

    with MANIFEST.open(newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))

    for row in rows:
        video_id = row["video_id"]
        dst = OUT_DIR / f"{video_id}.mp4"

        if dst.exists() and not args.force:
            skipped.append(video_id)
            continue

        # `source` says where the file comes from: an 8-minute Ego4D moments
        # clip, a full Ego4D video (the only way to get a stimulus longer than
        # 480 s -- see "Why no clip is longer than 8 minutes"), or `local`, a
        # path relative to this project for a file we already have on disk.
        if row["source"] == "clip_256ss":
            src = clip_dir / f"{row['clip_uid']}.mp4"
        elif row["source"] == "local":
            src = (ROOT / row["source_video_uid"]).resolve()
        else:
            src = video_dir / f"{row['source_video_uid']}.mp4"

        if not src.exists():
            missing.append((video_id, src))
            continue

        # Everything is re-encoded, including clips that are already 256p and
        # would stream-copy faster. Ego4D ships them as VP9, sometimes with an
        # audio track; a stream copy would leave the stimulus set mixed between
        # VP9 and H.264, and VP9-in-MP4 is not reliably playable outside
        # Chrome and Firefox. Uniform H.264, silent, is worth the CPU.
        # A `local` practice clip is already exactly the clip we want, so it
        # is only downscaled. An Ego4D source has to be cut down to length
        # first.
        if row["role"] == "practice" and row["source"] != "local":
            stage_downscaled(src, dst, start=PRACTICE_START_SEC,
                             duration=float(row["duration_sec"]))
        else:
            stage_downscaled(src, dst)

        staged.append(video_id)

    # Record what the app can actually show, so app.py never guesses.
    index = []
    for row in rows:
        path = OUT_DIR / f"{row['video_id']}.mp4"
        if not path.exists():
            continue
        index.append({
            "video_id": row["video_id"],
            "role": row["role"],
            "domain": row["domain"],
            "clip_uid": row["clip_uid"],
            "filename": path.name,
            "duration_sec": round(probe_duration(path), 3),
        })
    (ROOT / "stimuli" / "staged.json").write_text(
        json.dumps(index, indent=2) + "\n", encoding="utf-8"
    )

    print(f"staged:  {', '.join(staged) or '-'}")
    print(f"skipped: {', '.join(skipped) or '-'}  (already present; use --force)")
    for video_id, src in missing:
        print(f"MISSING: {video_id}  expected source {src}", file=sys.stderr)
    if missing:
        print("\nFetch the missing clips with scripts/fetch_stimuli.sh, then re-run.",
              file=sys.stderr)
    print(f"\nwrote {ROOT / 'stimuli' / 'staged.json'} ({len(index)} videos)")
    return 1 if missing else 0


if __name__ == "__main__":
    raise SystemExit(main())
