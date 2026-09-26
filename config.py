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

#: Key participants press to mark a boundary, as shown in the instructions.
#: SPACE is the transport play/pause toggle instead, so marking uses ENTER.
RESPONSE_KEY_NAME = "ENTER"

#: Participants may rewind but never skip forward, so every boundary is judged
#: from video they have actually watched. One step size, to keep the transport
#: simple enough to use without looking away from the video.
REWIND_STEP_SEC = 5

#: How far a mark may be dragged along the bar, in seconds either way. Marks
#: are placed by keypress, so they inherit the participant's reaction time;
#: dragging is for correcting that lag. Wide enough to cover a slow response
#: and a rewatch of the moment, without letting a mark travel to a different
#: part of the activity.
MARK_DRAG_LIMIT_SEC = 10.0

#: The staged videos carry no audio track, but muting is also what keeps
#: browsers from blocking playback.
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
### Welcome, and thank you for your particiaption

You will watch a series of egocentric videos of
everyday activities and mark where you think one event ends and the next
begins. You control playback, so you can pause and rewind as you go.

The whole session takes about **1 hour 15 minutes**. You are not expected to do
it in one sitting: you can stop between videos and resume later with the same
Participant ID - your progress is saved automatically.
"""

TASK_OVERVIEW = f"""
### What you will do

You will see **{N_MAIN_VIDEOS} videos** of quite different lengths, and watch
**each one twice, back to back** - once marking coarse (large) boundaries and
once marking fine (small) ones. The order of the videos, and of the two
viewings, is different for every participant.

While a video plays, press **{RESPONSE_KEY_NAME}** every time you believe a
meaningful unit of activity has ended and another has begun.

| key | does |
|---|---|
| **{RESPONSE_KEY_NAME}** | mark a boundary |
| **SPACE** | play / pause |
| **LEFT ARROW** | rewind {REWIND_STEP_SEC} seconds |
| **BACKSPACE** | remove the mark you just made |

There is no way to skip forward - you will see all of every video.

**Rewinding.** If you think you missed a boundary, rewind and watch that
stretch again. You can press **{RESPONSE_KEY_NAME}** while rewound or while
paused: a mark is recorded wherever the video is sitting, not only during
normal playback.

**Fixing the timing.** Marks appear as orange handles on the wide bar under
the video. Because it takes a moment to react, a mark usually lands slightly
*after* the change you noticed - **drag the handle** left or right (up to
{MARK_DRAG_LIMIT_SEC:.0f} seconds) to put it where the change actually
happened.

The videos are **silent**, so there is no need to adjust your volume. Don't
agonise over exact placement: we want your intuition, not a perfect answer.
"""

#: Shown once, before the comprehension check. The three cues -- goal,
#: location, entities -- are the situational dimensions whose change predicts
#: boundary judgements in event segmentation theory (Zacks & Swallow 2007;
#: Zacks, Speer, Swallow, Braver & Reynolds 2007). Phrased as "your prediction
#: stops working" rather than in terms of prediction error, since the
#: participant has to apply it without the theory.
EVENT_DEFINITION = """
### What counts as an event?

As you watch, you build up a picture of what is going on - what the person is
doing, where they are, what they are handling - and use it to anticipate what
comes next.

* An **event** is a stretch of video over which that picture keeps working.
* An **event boundary** is the moment it stops working: what happens next is
  not what the activity so far led you to expect, and you need a fresh picture
  to follow along.

Three things tend to mark a boundary, of which a change of **goal** is the
strongest:

| what changes | example |
|---|---|
| **Goal** - what the person is trying to get done | stops collecting ingredients, starts mixing them |
| **Location** - where the action is happening | walks from the kitchen out to the garden |
| **Entities** - who or what is involved | puts the knife down and picks up a drill; someone walks in |

**A camera movement is not a boundary.** The camera is on the person's head,
so the view swings around constantly. Mark changes in *what is being done*, not
in what the camera happens to point at.
"""

#: One worked example, shown twice: on the overview screen with both grains
#: side by side, so the nesting is visible before the comprehension check asks
#: about it, and again in the per-viewing instructions below. Defined here once
#: so the two copies cannot drift apart.
COARSE_EXAMPLE = (
    "`Removing all the old bedding` → `Putting on the fresh sheets and "
    "blankets` → `Placing the pillows back on top`"
)
FINE_EXAMPLE = (
    "`Pulling off the first pillowcase` → `Pulling off the next pillowcase` → "
    "`Tugging the corner of the fitted sheet` → and so on..."
)
#: The coarse event the fine example sits inside.
FINE_EXAMPLE_PARENT = "Removing all the old bedding"

GRANULARITY_OVERVIEW = f"""
### Coarse and fine boundaries

You watch each video twice, marking at two different grains. The instructions
before each viewing say which one you are doing, so read them - they change.

**Coarse** - the **large** shifts, where you would start a new sentence if you
were describing the video. Making a bed might divide into:

> {COARSE_EXAMPLE}

**Fine** - the **smallest** units that still feel like a complete, meaningful
thing the person did. The single coarse event `{FINE_EXAMPLE_PARENT}` divides
into:

> {FINE_EXAMPLE}

Fine boundaries sit **inside** the coarse ones - the same activity divided more
finely, not something different - so expect to press **noticeably more often**
in a fine viewing than in a coarse one.
"""

COARSE_INSTRUCTIONS = f"""
### This viewing: COARSE boundaries

Mark only the **large** shifts - the points where you would start a new
sentence if you were describing the video to someone else.

*For example, making a bed might divide into:*

> {COARSE_EXAMPLE}
"""

FINE_INSTRUCTIONS = f"""
### This viewing: FINE boundaries

Mark the **smallest** units of activity that still feel like a complete,
meaningful thing the person did.

*For example, the single coarse event `{FINE_EXAMPLE_PARENT}` divides into:*

> {FINE_EXAMPLE}

Expect to press **noticeably more often** than in the coarse viewing.
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
    f"You pressed **{RESPONSE_KEY_NAME}** too few times. Please redo the "
    "practice and try to identify more boundaries."
)
PRACTICE_TOO_MANY = (
    f"You pressed **{RESPONSE_KEY_NAME}** too many times. Please redo the "
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
#:
#: Options are shuffled per participant at render time
#: (``storage.comprehension_options``), so the order written here does not
#: reach the screen and position cannot signal the answer.
COMPREHENSION_QUESTIONS = [
    {
        "id": "q_boundary",
        "prompt": "What is an event boundary?",
        "options": [
            "Any moment the camera swings to look somewhere else",
            "The moment the activity changes, so what you expected to happen "
            "next no longer fits",
            "A cut or fade between two shots",
            "Every few seconds, at a steady rate",
        ],
        "answer": ("The moment the activity changes, so what you expected to "
                   "happen next no longer fits"),
        "explain": (
            "A boundary is where your sense of what is going on stops working "
            "and you need a fresh one. The camera is on the person's head, so "
            "it moves constantly - that on its own is not a boundary."
        ),
    },
    {
        "id": "q_coarse",
        "prompt": "In the COARSE viewing, what should you mark?",
        "options": [
            "Every time the person picks up a different object",
            "Only the very start and very end of the video",
            "The largest shifts - where one whole part of the activity ends "
            "and another begins",
            "Every time the camera wearer moves their head",
        ],
        "answer": ("The largest shifts - where one whole part of the activity "
                   "ends and another begins"),
        "explain": (
            "Coarse = the large shifts, usually a change of goal or location. "
            "The smaller steps inside them belong to the fine viewing."
        ),
    },
    {
        "id": "q_fine",
        "prompt": (
            "Compared with the coarse viewing, how many boundaries do you "
            "expect to mark in the FINE viewing?"
        ),
        "options": ["Exactly the same number", "More", "Fewer", "None"],
        "answer": "More",
        "explain": (
            "Fine segmentation divides the same activity into smaller units, "
            "so it normally yields more boundaries than coarse segmentation."
        ),
    },
    {
        "id": "q_key",
        "prompt": "What do you do when you notice an event boundary?",
        "options": [
            "Click the mouse on the video",
            "Press the SPACEBAR",
            "Press ENTER",
            "Wait until the video ends, then type the times",
        ],
        "answer": "Press ENTER",
        "explain": (
            "ENTER marks a boundary. SPACE is play/pause, so it will not "
            "record anything."
        ),
    },
    {
        "id": "q_drag",
        "prompt": (
            "You notice a boundary, but by the time you press the key the "
            "video has moved slightly past it. What can you do?"
        ),
        "options": [
            "Drag the mark on the bar left until it lines up with the change",
            "Nothing - the mark is fixed where you pressed",
            "Delete the mark and start the video again from the beginning",
            "Press ENTER a second time to correct it",
        ],
        "answer": "Drag the mark on the bar left until it lines up with the change",
        "explain": (
            "Marks are draggable for exactly this reason: pressing a key takes "
            "a moment, so your mark lands slightly late. Drag it back into "
            "place. BACKSPACE is for removing a mark you did not mean at all."
        ),
    },
]
