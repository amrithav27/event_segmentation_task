# Event Segmentation Study

You will watch egocentric videos of everyday activities and mark, as you
watch, event boundaries.

## Install and run with uv

1. Install [uv](https://docs.astral.sh/uv/getting-started/installation/).
2. From this directory, run:

   ```
   uv sync
   uv run streamlit run app.py
   ```

## Install and run with pip

1. Create and activate a virtual environment from this directory:

   **Linux / macOS**

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

   **Windows** (PowerShell)

   ```powershell
   py -3 -m venv .venv
   .venv\Scripts\Activate.ps1
   ```

2. Install the dependencies and start the app:

   ```
   python -m pip install -r requirements.txt
   streamlit run app.py
   ```

The app opens at <http://localhost:8501>. Leave the terminal window open while
you work - closing it stops the app. Press Ctrl+C there when you are done.

## Before you start

Check that `static/videos/` contains `practice.mp4`, `V01.mp4`, `V02.mp4` and
`V03.mp4`. If the videos were sent to you separately, put them there. The app
will not run without them.
## Doing the task

Use the **Participant ID** given to you to log in.

You will get instructions, a short comprehension check, two practice runs, and
then the videos themselves. **Press ENTER every time you feel one event has
ended and another has begun.**

You control playback:

| key | does |
|---|---|
| **Enter** | mark a boundary |
| **Space** | play / pause |
| **←** | rewind 5 seconds |
| **Backspace** | remove the mark you just made |

There is no way to skip forward - you will see all of every video.

If you think you missed a boundary, rewind and watch that stretch again. You
can press **Enter** while rewound or while paused.**Drag a handle left or right** (up to 10 seconds) to put it where the change actually happened if you think theree waas some latency when marking the label.

Each video is watched **twice in a row** - once marking large event boundaries
and once marking small ones. The instructions before each viewing tell you
which, so please read them: they change between the two viewings.

The videos are silent, so there is no
need to adjust your volume. Don't agonise over exact placement - we want your
intuition, not a perfect answer.

There are **three videos** of quite different lengths - roughly 6, 8 and 18
minutes - so the whole thing takes about **1 hour 15 minutes**. It is not meant
to be done in one sitting.

## Pausing and resuming

Your progress is saved automatically **after every video**, so you can stop between
videos and come back later - just log in with the **same Participant ID** and
you will continue from where you left off.

You can also click **Download all my data (.zip)** in the sidebar at any point
to save your progress so far.

## When you are done

Click **Download all my data (.zip)** and send me the file. It contains your
marks for all eight viewings — the two practice runs and both passes over
each of the three videos.

In case of any questions, you can contact me.

Thanks for your participation.


