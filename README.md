# Event Segmentation Study

You will watch short first-person videos of everyday activities and mark, as you
watch, where you think one event ends and the next begins.

This app requires Python 3.10 or later, and **Chrome or Firefox**.

## Install and run with uv

1. Install [uv](https://docs.astral.sh/uv/getting-started/installation/).
2. From this directory, run:

   ```bash
   uv sync
   uv run streamlit run app.py
   ```

## Install and run with pip

1. Create and activate a virtual environment from this directory:

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate        # Windows: .venv\Scripts\activate
   ```

2. Install the dependencies and start the app:

   ```bash
   python -m pip install -r requirements.txt
   streamlit run app.py
   ```

The app opens at <http://localhost:8501>.

## Before you start

Put the video files you were sent into `static/videos/`, so that the folder
contains `practice.mp4`, `V01.mp4`, `V02.mp4` and `V03.mp4`. The app will not
run without them.

## Doing the task

Use the **Participant ID** given to you to log in.

You will get instructions, a short comprehension check, two practice clips, and
then the videos themselves. **Press ENTER every time you feel one event has
ended and another has begun.**

You control playback:

| key | does |
|---|---|
| **Enter** | mark a boundary |
| **Space** | play / pause |
| **← / →** | jump back / forward 5 seconds |
| **↑ / ↓** | jump forward / back 30 seconds |
| **Backspace** | remove the mark you just made |

You can also click the bar under the video to jump to any point. Your marks
appear as ticks on that bar.

Each video is watched **twice in a row** - once marking large event boundaries
and once marking small ones. The instructions before each viewing tell you
which, so please read them: they change between the two viewings.

Pause and rewind as much as you need, but please **watch the whole video**
rather than skipping to the end. The videos are silent, so there is no need to
adjust your volume. Don't agonise over exact placement - we want your
intuition, not a perfect answer.

There are **three videos** of quite different lengths - roughly 6, 8 and 18
minutes - so the whole thing takes about **1 hour 15 minutes**. It is not meant
to be done in one sitting.

## Pausing and resuming

Your progress is saved automatically after every video, so you can stop between
videos and come back later - just log in with the **same Participant ID** and
you will continue from where you left off.

You can also click **Download all my data (.zip)** in the sidebar at any point
to save your progress so far.

## When you are done

Click **Download all my data (.zip)** and send me the file. It contains your
marks for all eight viewings — the two practice clips and both passes over
each of the three videos.

In case of any questions, you can contact me.

Thanks for agreeing to this.


