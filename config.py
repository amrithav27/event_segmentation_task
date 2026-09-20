"""Experiment parameters and participant-facing text.

Everything a researcher might want to tune lives here, so ``app.py`` stays
mechanism and this stays design. Instruction wording follows the PsychoPy
event-segmentation protocol in ``../pooja_experiment``.
"""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent
STIMULI_DIR = ROOT / "stimuli"
RESPONSES_DIR = ROOT / "responses"
VIDEO_URL_PREFIX = "app/static/videos"  # served by Streamlit's static file server

# ---------------------------------------------------------------- design ----

#: Number of main videos each participant annotates.
N_MAIN_VIDEOS = 3

#: Each video is viewed once per granularity, back to back.
GRANULARITIES = ("coarse", "fine")

#: Key participants press to mark a boundary. SPACE is the transport
#: play/pause toggle instead, so marking uses ENTER.
RESPONSE_KEY = "Enter"
RESPONSE_KEY_NAME = "ENTER"

#: Playback controls offered during a viewing. Setting this to False would
#: also mean reverting the player to its no-controls form.
ALLOW_PLAYBACK_CONTROLS = True

#: Videos play muted -- Ego4D audio is uninformative here and muting also keeps
#: browsers from blocking autoplay.
MUTE_VIDEO = True

# ------------------------------------------------------- practice limits ----

#: Accepted mark counts on the practice clip, as marks per minute.
#:
#: The practice clip is the one from the PsychoPy study in
#: ``../pooja_experiment``, so these reproduce the thresholds that study's code
#: hard-codes for this exact clip: coarse 1-4 and fine 5-10 (see
#: ``segmentation_exp_lab_lastrun.py``, the ``lower``/``upper`` pairs). Stated
#: as rates rather than counts so they still mean something if the clip is
#: swapped.
PRACTICE_RATE_BOUNDS = {
    "coarse": (0.5, 2.0),   # 1-4 marks on the 106 s practice clip
    "fine": (3.0, 5.5),     # 5-10 marks on the 106 s practice clip
}

#: How many times a participant may fail the practice before the app lets them
#: through anyway (prevents an unwinnable loop for an unusual but honest rater).
PRACTICE_MAX_ATTEMPTS = 3

# ---------------------------------------------------------------- text ------

WELCOME = """
### Welcome, and thank you for taking part

You will watch a series of short first-person ("head-camera") videos of
everyday activities and mark where you think one event ends and the next
begins. You control playback, so you can pause and rewind as you go.

The whole session takes about **1 hour 15 minutes**. You are not expected to do
it in one sitting: you can stop between videos and resume later with the same
Participant ID - your progress is saved automatically.
"""

TASK_OVERVIEW = f"""
### What you will do

You will see **{N_MAIN_VIDEOS} videos**, of quite different lengths - roughly 6,
8 and 18 minutes. You watch **each video twice, back to back**:

* once marking **coarse** (large) event boundaries, and
* once marking **fine** (small) event boundaries.

The order of the two viewings, and the order of the videos, is different for
every participant.

While a video plays, press the **{RESPONSE_KEY_NAME}** every time you believe a
meaningful unit of activity has ended and another has begun.

**You control playback:**

| key | does |
|---|---|
| **ENTER** | mark a boundary |
| **SPACE** | play / pause |
| **LEFT / RIGHT** | jump back / forward 5 seconds |
| **UP / DOWN** | jump forward / back 30 seconds |
| **BACKSPACE** | remove the mark you just made |

You can also click the bar under the video to jump to any point. Marks you
have made show up as ticks on that bar.

**Important:**

* Please **watch the whole video** - do not skip ahead to the end.
* The videos are **silent** - do not adjust your volume.
* Mark boundaries as you notice them. Pause or rewind if you need to check
  something, but don't agonise: we want your intuition, not a perfect answer.
"""

COARSE_INSTRUCTIONS = f"""
### Coarse segmentation

For this viewing, press the **{RESPONSE_KEY_NAME}** when you identify
**SIGNIFICANT shifts in the narrative**, or events that seem meaningful to you.

Focus on the **LARGER** shifts in what the person is doing, rather than
fixating on minor details. It is better to miss a potential boundary than to
mark too many.
"""

FINE_INSTRUCTIONS = f"""
### Fine segmentation

For this viewing, press the **{RESPONSE_KEY_NAME}** to identify the **SMALLEST
units of activity** that are natural and meaningful to you.

You should expect to press noticeably **more often** than in the coarse
viewing.
"""

INSTRUCTIONS = {"coarse": COARSE_INSTRUCTIONS, "fine": FINE_INSTRUCTIONS}

PRACTICE_INTRO = """
### Practice

First, a short practice run so you get a feel for the task. The practice clip
is under two minutes and is **not** part of the real data.

If you mark far more or far fewer boundaries than expected, you will be asked
to repeat the practice.
"""

PRACTICE_TOO_FEW = (
    f"You pressed the {RESPONSE_KEY_NAME} **too few** times. Please redo the "
    "practice and try to identify more boundaries."
)
PRACTICE_TOO_MANY = (
    f"You pressed the {RESPONSE_KEY_NAME} **too many** times. Please redo the "
    "practice and try to identify fewer boundaries."
)
PRACTICE_PASSED = "Good job. That is the right kind of response rate."

BREAK_TEXT = """
### Break

You have finished this video. Take a short break if you would like to.

Your progress so far is already saved. You can close the app now and resume
later with the same Participant ID - you will pick up from exactly this point.
"""

FINISH_TEXT = """
### All done - thank you

You have completed every video. Please download your data below and send the
file back to the experimenter.
"""

# -------------------------------------------------- comprehension check -----

#: All questions must be answered correctly before the practice begins. These
#: check that the participant has actually read the instructions, which the
#: PsychoPy version relied on an in-room experimenter to confirm.
COMPREHENSION_QUESTIONS = [
    {
        "id": "q_key",
        "prompt": "What do you do when you notice an event boundary?",
        "options": [
            "Press ENTER",
            "Press the SPACEBAR",
            "Click the mouse on the video",
            "Wait until the video ends, then type the times",
        ],
        "answer": "Press ENTER",
        "explain": (
            "ENTER marks a boundary. SPACE is play/pause, so it will not "
            "record anything."
        ),
    },
    {
        "id": "q_coarse",
        "prompt": "In the COARSE viewing, what should you mark?",
        "options": [
            "The largest, most significant shifts in the activity",
            "The smallest meaningful units of activity",
            "Every time the camera wearer moves their head",
            "Only the very start and very end of the video",
        ],
        "answer": "The largest, most significant shifts in the activity",
        "explain": (
            "Coarse = large, significant shifts in the narrative. Fine = the "
            "smallest units that still feel meaningful."
        ),
    },
    {
        "id": "q_fine",
        "prompt": (
            "Compared with the coarse viewing, how many boundaries do you "
            "expect to mark in the FINE viewing?"
        ),
        "options": ["More", "Fewer", "Exactly the same number", "None"],
        "answer": "More",
        "explain": (
            "Fine segmentation picks out smaller units, so it normally yields "
            "more boundaries than coarse segmentation of the same video."
        ),
    },
    {
        "id": "q_controls",
        "prompt": "Which key pauses and resumes the video?",
        "options": [
            "SPACE",
            "ENTER",
            "P",
            "You cannot pause",
        ],
        "answer": "SPACE",
        "explain": (
            "SPACE toggles play/pause. The arrow keys jump back and forward, "
            "and BACKSPACE removes the mark you just made."
        ),
    },
    {
        "id": "q_repeat",
        "prompt": "How many times do you watch each video?",
        "options": [
            "Twice - once coarse and once fine",
            "Once only",
            "Three times",
            "As many times as I like",
        ],
        "answer": "Twice - once coarse and once fine",
        "explain": "Every video is annotated twice, back to back.",
    },
]
