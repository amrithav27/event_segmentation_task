# Event Segmentation Study

You will watch short first-person videos of everyday activities and mark, as you
watch, where you think one event ends and the next begins.

This app requires Python 3.10 or later, and **Chrome, Edge or Firefox**. It
runs the same way on Windows, macOS and Linux.

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

## If the video does not play

The page loads and the buttons work, but the video area stays black:

* Check that **`.streamlit/config.toml` is present**. It is what lets the app
  serve the videos, and `.streamlit` is a hidden folder, so it is easily lost
  if the project was copied by hand or unzipped selectively - on Windows, turn
  on **View > Hidden items** in File Explorer to see it. If it is gone, start
  the app with the setting instead:

  ```
  streamlit run app.py --server.enableStaticServing=true
  ```

* Check `static/videos/` really holds the four `.mp4` files.
* Use Chrome, Edge or Firefox. Safari and Internet Explorer are not supported.
* Click **Click to begin** on the video before pressing any keys - that click
  is what gives the player keyboard focus.

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
marks for all eight viewings — the two practice runs and both passes over
each of the three videos.

In case of any questions, you can contact me.

Thanks for agreeing to this.


