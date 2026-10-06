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

#: Each video is viewed once, marking coarse boundaries only.
GRANULARITIES = ("coarse",)

#: Key participants press to mark a boundary, as shown in the instructions.
#: SPACE is the transport play/pause toggle instead, so marking uses ENTER.
RESPONSE_KEY_NAME = "ENTER"

#: Annotation offers no seeking at all - no rewind, no skip - so every boundary
#: is judged on one first viewing. This step is used only by the demos, where
#: the arrow keys rewind and skip ahead.
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

# ----------------------------------------------------------------- demos ----

#: Worked examples shown before the practice. Each plays with the reference
#: coarse boundaries from ``static/videos/Annotations_in_seconds.txt``
#: animated as ENTER presses, so participants see when a press belongs.
#: ``annotation_index`` is the "Video N" entry in that file.
DEMO_ANNOTATIONS_FILE = ROOT / "static" / "videos" / "Annotations_in_seconds.txt"
DEMO_VIDEOS = [
    {"video_id": "V04", "filename": "V04.mp4", "annotation_index": 1},
    {"video_id": "V05", "filename": "V05.mp4", "annotation_index": 2},
]

# ------------------------------------------------------- practice limits ----

#: Accepted mark counts on the practice clip, as marks per minute.
#:
#: The practice clip is the one from the PsychoPy study in
#: ``../pooja_experiment``, so these reproduce the thresholds that study's code
#: hard-codes for this exact clip: coarse 1-4 (see
#: ``segmentation_exp_lab_lastrun.py``, the ``lower``/``upper`` pairs). Stated
#: as rates rather than counts so they still mean something if the clip is
#: swapped.
PRACTICE_RATE_BOUNDS = {
    "coarse": (0.5, 2.0),   # 1-4 marks on the 106 s practice clip
}

#: How many times a participant may fail the practice before the app lets them
#: through anyway (prevents an unwinnable loop for an unusual but honest rater).
PRACTICE_MAX_ATTEMPTS = 3

# ---------------------------------------------------------------- text ------

WELCOME = """
### Welcome, and thank you for your participation

You will watch a series of egocentric videos of everyday activities and mark
where you think one large event ends and the next begins. You control
playback, so you can pause whenever you need to.

The whole session takes about **1 hour**. You are not expected to do it in one
sitting: you can stop between videos and resume later with the same
Participant ID - your progress is saved automatically.
"""

TASK_OVERVIEW = f"""
### What you will do

You will see **{N_MAIN_VIDEOS} videos** of quite different lengths and watch
**each one once**, marking **coarse** (large) event boundaries. The order of
the videos is different for every participant.

While a video plays, press **{RESPONSE_KEY_NAME}** every time you believe one
large unit of activity has ended and another has begun.

| key | does |
|---|---|
| **{RESPONSE_KEY_NAME}** | mark a boundary |
| **SPACE** | play / pause |
| **BACKSPACE** | remove the mark you just made |

**No rewinding or skipping.** Each video plays through once, from start to
end - you cannot go back or jump ahead, so watch closely. You can pause at any
time, and you can press **{RESPONSE_KEY_NAME}** while paused.

**Fixing the timing.** Marks appear as orange handles on the wide bar under
the video. Because it takes a moment to react, a mark usually lands slightly
*after* the change you noticed - **drag the handle** left or right (up to
{MARK_DRAG_LIMIT_SEC:.0f} seconds) to put it where the change actually
happened.

The videos are **silent**, so there is no need to adjust your volume. Don't
agonise over exact placement: we want your intuition, not a perfect answer.
"""

#: The three cues -- goal, location, entities -- are the situational
#: dimensions whose change predicts boundary judgements in event segmentation
#: theory (Zacks & Swallow 2007; Zacks, Speer, Swallow, Braver & Reynolds
#: 2007). Phrased as "your prediction stops working" rather than in terms of
#: prediction error, since the participant has to apply it without the theory.
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

#: The coarse example, shown in the overview and again before every viewing.
COARSE_EXAMPLE = (
    "`Removing all the old bedding` → `Putting on the fresh sheets and "
    "blankets` → `Placing the pillows back on top`"
)
#: Shown only as a counter-example, so participants know what *not* to mark.
TOO_SMALL_EXAMPLE = (
    "`Pulling off the first pillowcase` → `Pulling off the next pillowcase` → "
    "`Tugging the corner of the fitted sheet`"
)

GRANULARITY_OVERVIEW = f"""
### Mark only the large (coarse) boundaries

Mark the **large** shifts - the points where you would start a new sentence if
you were describing the video to someone else. Making a bed might divide into:

> {COARSE_EXAMPLE}

**What is too small.** The same activity could be chopped much more finely -
for example, `Removing all the old bedding` could be split into
{TOO_SMALL_EXAMPLE}. Those small steps are **not** what we are asking for.
They all sit *inside* one coarse event, so do **not** press for them.
"""

COARSE_INSTRUCTIONS = f"""
### Mark COARSE boundaries

Mark only the **large** shifts - the points where you would start a new
sentence if you were describing the video to someone else.

*For example, making a bed might divide into:*

> {COARSE_EXAMPLE}

Ignore the small steps inside each of these - press only when one large part
of the activity ends and the next begins.
"""

INSTRUCTIONS = {"coarse": COARSE_INSTRUCTIONS}

DEMO_INTRO = f"""
### Demos: what a good annotation looks like

Before you practise, watch **two demo videos** that have already been
annotated. Each time the video reaches a coarse boundary, you will see the
**{RESPONSE_KEY_NAME}** key light up and a mark drop onto the bar - that is the
moment you would press **{RESPONSE_KEY_NAME}** yourself.

You do not press anything during a demo. You can pause, rewind, skip ahead and
watch each demo **as many times as you like**. Once you have watched both to
the end, you can go on to the practice.
"""

PRACTICE_INTRO = """
### Practice

Next, a short practice run so you get a feel for the task. The practice clip
is under two minutes and is **not** part of the real data.

If you mark far more or far fewer boundaries than expected, you will be asked
to repeat the practice.
"""

PRACTICE_TOO_FEW = (
    f"You pressed **{RESPONSE_KEY_NAME}** too few times. Please redo the "
    "practice and try to identify more boundaries."
)
PRACTICE_TOO_MANY = (
    f"You pressed **{RESPONSE_KEY_NAME}** too many times. Remember to mark "
    "only the large (coarse) shifts. Please redo the practice and try to "
    "identify fewer boundaries."
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
