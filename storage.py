"""Stimulus loading, per-participant schedules, and on-disk result files.

Layout, one directory per participant::

    responses/<participant_id>/
        session.json     schedule, comprehension + practice records
        viewings.csv     one row per completed viewing
        boundaries.csv   one row per boundary mark

A *viewing* is the atomic unit of progress: it is written only once the video
has played to the end, so an interrupted viewing is simply redone and never
lands half-recorded. Resuming is therefore just "how many rows are in
viewings.csv".
"""

from __future__ import annotations

import csv
import hashlib
import io
import json
import random
import re
import zipfile
from dataclasses import dataclass
from datetime import datetime, timezone

import config

#: 2.x records playback-control fields and uses ENTER to mark, so its
#: viewings.csv is not column-compatible with 1.x output.
APP_VERSION = "2.0.0"

VIEWING_FIELDS = [
    "participant_id", "block_index", "video_id", "granularity",
    "viewing_in_block", "n_presses", "video_duration_sec", "elapsed_sec",
    "blur_events", "pause_count", "seek_count", "max_time_reached_sec",
    "completed_utc",
]

BOUNDARY_FIELDS = [
    "participant_id", "block_index", "video_id", "granularity",
    "viewing_in_block", "press_index", "boundary_sec", "wall_clock_sec",
]

VALID_PID = re.compile(r"^[A-Za-z0-9_-]{2,32}$")


# --------------------------------------------------------------- stimuli ----

@dataclass(frozen=True)
class Stimulus:
    video_id: str
    role: str
    domain: str
    clip_uid: str
    filename: str
    duration_sec: float

    @property
    def url(self) -> str:
        return f"/{config.VIDEO_URL_PREFIX}/{self.filename}"


def load_stimuli() -> tuple[list[Stimulus], Stimulus | None]:
    """Return ``(main_videos, practice_video)`` for the files actually on disk.

    Driven by ``stimuli/videos.csv``, which is committed, so a participant who
    was simply handed the ``static/videos/`` folder needs nothing installed
    beyond Streamlit. ``stimuli/staged.json`` is an optional refinement written
    by ``prepare_stimuli.py``: when present its ffprobe-measured durations
    override the declared ones.
    """
    manifest = config.STIMULI_DIR / "videos.csv"
    if not manifest.exists():
        raise FileNotFoundError(f"{manifest} not found - the checkout is incomplete.")

    measured: dict[str, float] = {}
    staged = config.STIMULI_DIR / "staged.json"
    if staged.exists():
        try:
            measured = {e["video_id"]: e["duration_sec"]
                        for e in json.loads(staged.read_text(encoding="utf-8"))}
        except (json.JSONDecodeError, KeyError, TypeError):
            measured = {}  # a stale or hand-edited file must not break the app

    video_dir = config.ROOT / "static" / "videos"
    entries: list[Stimulus] = []
    with manifest.open(newline="", encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            filename = f"{row['video_id']}.mp4"
            if not (video_dir / filename).exists():
                continue
            entries.append(Stimulus(
                video_id=row["video_id"],
                role=row["role"],
                domain=row["domain"],
                clip_uid=row["clip_uid"],
                filename=filename,
                duration_sec=measured.get(row["video_id"],
                                          float(row["duration_sec"])),
            ))

    main = sorted((e for e in entries if e.role == "main"), key=lambda e: e.video_id)
    practice = next((e for e in entries if e.role == "practice"), None)
    return main, practice


# -------------------------------------------------------------- schedule ----


def build_schedule(participant_id: str, main: list[Stimulus]) -> list[dict]:
    """Randomise video order, and granularity order within each video.

    Seeded by participant ID so the same person always gets the same schedule,
    which keeps a resumed session identical to the original one even before the
    saved copy is consulted.
    """
    seed = int(hashlib.sha256(participant_id.encode()).hexdigest()[:16], 16)
    rng = random.Random(seed)

    videos = [s.video_id for s in main]
    rng.shuffle(videos)

    schedule = []
    for block_index, video_id in enumerate(videos, start=1):
        order = list(config.GRANULARITIES)
        rng.shuffle(order)
        for viewing_in_block, granularity in enumerate(order, start=1):
            schedule.append({
                "block_index": block_index,
                "video_id": video_id,
                "granularity": granularity,
                "viewing_in_block": viewing_in_block,
            })
    return schedule


# ----------------------------------------------------------------- store ----


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


class Store:
    """Reads and writes one participant's files."""

    def __init__(self, participant_id: str):
        if not VALID_PID.match(participant_id):
            raise ValueError(
                "Participant ID must be 2-32 characters, letters/digits/-/_ only."
            )
        self.participant_id = participant_id
        self.dir = config.RESPONSES_DIR / participant_id
        self.session_path = self.dir / "session.json"
        self.viewings_path = self.dir / "viewings.csv"
        self.boundaries_path = self.dir / "boundaries.csv"

    # -- session ------------------------------------------------------------

    def exists(self) -> bool:
        return self.session_path.exists()

    def load_session(self) -> dict:
        return json.loads(self.session_path.read_text(encoding="utf-8"))

    def save_session(self, session: dict) -> None:
        self.dir.mkdir(parents=True, exist_ok=True)
        self.session_path.write_text(
            json.dumps(session, indent=2) + "\n", encoding="utf-8"
        )

    def create_session(self, main: list[Stimulus]) -> dict:
        session = {
            "participant_id": self.participant_id,
            "app_version": APP_VERSION,
            "created_utc": utc_now(),
            "n_main_videos": len(main),
            "schedule": build_schedule(self.participant_id, main),
            "comprehension": None,
            "practice": [],
        }
        self.save_session(session)
        self._ensure_headers()
        return session

    def open_or_create(self, main: list[Stimulus]) -> tuple[dict, bool]:
        """Return ``(session, resumed)``."""
        if self.exists():
            self._ensure_headers()
            return self.load_session(), True
        return self.create_session(main), False

    # -- results ------------------------------------------------------------

    def _ensure_headers(self) -> None:
        self.dir.mkdir(parents=True, exist_ok=True)
        for path, fields in ((self.viewings_path, VIEWING_FIELDS),
                             (self.boundaries_path, BOUNDARY_FIELDS)):
            if not path.exists():
                with path.open("w", newline="", encoding="utf-8") as fh:
                    csv.writer(fh).writerow(fields)

    def completed_viewings(self) -> list[dict]:
        if not self.viewings_path.exists():
            return []
        with self.viewings_path.open(newline="", encoding="utf-8") as fh:
            return list(csv.DictReader(fh))

    def n_completed(self) -> int:
        return len(self.completed_viewings())

    def record_viewing(self, step: dict, result: dict) -> None:
        """Append one finished viewing and all of its boundary marks.

        Written together and only on completion, so the two CSVs can never
        disagree about which viewings exist.

        Marks are stored in the order the participant pressed them. Because
        seeking is allowed, that is *not* necessarily increasing time order --
        sort by ``boundary_sec`` before analysing.
        """
        self._ensure_headers()
        presses = result.get("presses") or []

        with self.boundaries_path.open("a", newline="", encoding="utf-8") as fh:
            writer = csv.writer(fh)
            for i, press in enumerate(presses, start=1):
                writer.writerow([
                    self.participant_id, step["block_index"], step["video_id"],
                    step["granularity"], step["viewing_in_block"], i,
                    press["t_video"], press["t_wall"],
                ])

        with self.viewings_path.open("a", newline="", encoding="utf-8") as fh:
            csv.writer(fh).writerow([
                self.participant_id, step["block_index"], step["video_id"],
                step["granularity"], step["viewing_in_block"], len(presses),
                result.get("video_duration_sec", ""), result.get("elapsed_sec", ""),
                result.get("blur_events", 0), result.get("pause_count", 0),
                result.get("seek_count", 0), result.get("max_time_reached_sec", ""),
                utc_now(),
            ])

    # -- export -------------------------------------------------------------

    def read_csv_bytes(self, which: str) -> bytes:
        path = {"viewings": self.viewings_path,
                "boundaries": self.boundaries_path}[which]
        return path.read_bytes() if path.exists() else b""

    def bundle_zip(self) -> bytes:
        """All three files in one archive, for the participant to send back."""
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
            for path in (self.session_path, self.viewings_path, self.boundaries_path):
                if path.exists():
                    zf.write(path, arcname=f"{self.participant_id}/{path.name}")
        return buf.getvalue()
