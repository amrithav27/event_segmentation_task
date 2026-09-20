"""Event-boundary segmentation experiment (Streamlit).

Participants watch Ego4D Moment Queries clips and press ENTER at event
boundaries, with SPACE and the arrow keys controlling playback. Each video is
annotated twice, back to back, once coarse and once fine, in a per-participant
random order.

Run with::

    streamlit run app.py
"""

from __future__ import annotations

import math

import streamlit as st
import streamlit.components.v1 as components

import config
import storage

st.set_page_config(page_title="Event Segmentation Study", page_icon="⏱️",
                   layout="wide")

_player = components.declare_component(
    "boundary_player", path=str(config.ROOT / "components" / "boundary_player")
)

PRACTICE_ORDER = ("coarse", "fine")

#: Screens where the video should take the whole window.
VIEWING_STAGES = ("viewing", "practice_viewing")

#: Wide and padding-free while a video plays, so it gets the full screen;
#: narrow elsewhere, because full-width prose is hard to read.
_CSS_VIEWING = """
<style>
  /* padding-top clears Streamlit's fixed header, which otherwise overlaps
     the granularity heading. */
  .block-container { max-width: 100% !important;
                     padding: 3.25rem 1.5rem 0 1.5rem !important; }
  .block-container h4 { margin-bottom: 0.3rem; }
</style>
"""
_CSS_TEXT = """
<style>
  .block-container { max-width: 48rem !important; padding-top: 2.5rem !important; }
</style>
"""


# ------------------------------------------------------------- helpers ------

def ss() -> dict:
    return st.session_state


def practice_bounds(duration_sec: float, granularity: str) -> tuple[int, int]:
    """Accepted press count on the practice clip, from a per-minute rate."""
    low_rate, high_rate = config.PRACTICE_RATE_BOUNDS[granularity]
    minutes = duration_sec / 60.0
    return max(1, math.floor(low_rate * minutes)), math.ceil(high_rate * minutes)


def play(stimulus: storage.Stimulus, token: str, title: str, subtitle: str):
    """Render the player and return its result dict once the video has ended."""
    return _player(
        token=token,
        video_url=stimulus.url,
        muted=config.MUTE_VIDEO,
        title=title,
        subtitle=subtitle,
        key=f"player_{token}",
        default=None,
    )


def is_new_result(result) -> bool:
    """True once per completed viewing, ignoring Streamlit's later reruns."""
    if not result or result.get("status") != "completed":
        return False
    if result.get("token") == ss().get("last_recorded_token"):
        return False
    ss()["last_recorded_token"] = result["token"]
    return True


def goto(stage: str) -> None:
    ss()["stage"] = stage
    st.rerun()


def current_step() -> dict | None:
    schedule = ss()["session"]["schedule"]
    idx = ss()["store"].n_completed()
    return schedule[idx] if idx < len(schedule) else None


def stimulus_by_id(video_id: str) -> storage.Stimulus:
    return next(s for s in ss()["main"] if s.video_id == video_id)


# --------------------------------------------------------------- login ------

def screen_login(main, practice_stim) -> None:
    st.title("Event Segmentation Study")
    st.markdown(
        "Enter the Participant ID you were given. If you are returning to "
        "finish a session, enter the **same ID** and you will resume where you "
        "left off."
    )

    with st.form("login"):
        pid = st.text_input("Participant ID", max_chars=32,
                            placeholder="e.g. P07").strip()
        submitted = st.form_submit_button("Start / Resume", type="primary")

    if not submitted:
        return
    if not pid:
        st.error("Please enter a Participant ID.")
        return

    try:
        store = storage.Store(pid)
    except ValueError as exc:
        st.error(str(exc))
        return

    session, resumed = store.open_or_create(main)
    ss().update(store=store, session=session, main=main, practice=practice_stim,
                last_recorded_token=None)

    done = store.n_completed()
    total = len(session["schedule"])
    if not session.get("comprehension"):
        goto("welcome")
    elif not session.get("practice_completed"):
        goto("practice_intro")
    elif done >= total:
        goto("done")
    else:
        ss()["resumed_at"] = done
        goto("resume" if resumed else "block_intro")


# ----------------------------------------------------- instruction flow -----

def screen_welcome() -> None:
    st.markdown(config.WELCOME)
    if st.button("Continue", type="primary"):
        goto("overview")


def screen_overview() -> None:
    st.markdown(config.TASK_OVERVIEW)
    with st.expander("What counts as an event boundary?"):
        st.markdown(
            "There is no right answer - we want *your* intuition. A boundary "
            "is simply the moment where it feels like one thing the person was "
            "doing has finished and something else has started."
        )
    if st.button("Continue to comprehension check", type="primary"):
        goto("comprehension")


def screen_comprehension() -> None:
    st.markdown("### Comprehension check")
    st.markdown(
        "Please answer all questions. This just confirms the instructions were "
        "clear - you can retake it as many times as you need."
    )

    with st.form("comprehension"):
        answers = {}
        for q in config.COMPREHENSION_QUESTIONS:
            answers[q["id"]] = st.radio(
                q["prompt"], q["options"], index=None, key=f"c_{q['id']}"
            )
        submitted = st.form_submit_button("Submit answers", type="primary")

    if not submitted:
        return

    if any(v is None for v in answers.values()):
        st.error("Please answer every question.")
        return

    wrong = [q for q in config.COMPREHENSION_QUESTIONS
             if answers[q["id"]] != q["answer"]]
    attempts = ss().setdefault("comprehension_attempts", 0) + 1
    ss()["comprehension_attempts"] = attempts

    if wrong:
        st.error(f"{len(wrong)} answer(s) need another look:")
        for q in wrong:
            st.markdown(f"- **{q['prompt']}** {q['explain']}")
        st.info("Re-read the highlighted points above, then submit again.")
        return

    session = ss()["session"]
    session["comprehension"] = {
        "passed_utc": storage.utc_now(),
        "attempts": attempts,
        "n_questions": len(config.COMPREHENSION_QUESTIONS),
    }
    ss()["store"].save_session(session)
    st.success("All correct.")
    goto("practice_intro")


# ------------------------------------------------------------ practice ------

def screen_practice_intro() -> None:
    st.markdown(config.PRACTICE_INTRO)
    ss().setdefault("practice_index", 0)
    ss().setdefault("practice_attempts", {"coarse": 0, "fine": 0})
    if st.button("Begin practice", type="primary"):
        goto("practice_instructions")


def screen_practice_instructions() -> None:
    ss().setdefault("practice_index", 0)
    ss().setdefault("practice_attempts", {"coarse": 0, "fine": 0})
    granularity = PRACTICE_ORDER[ss()["practice_index"]]
    st.markdown(f"### Practice {ss()['practice_index'] + 1} of {len(PRACTICE_ORDER)}")
    st.markdown(config.INSTRUCTIONS[granularity])
    st.info(
        f"**{config.RESPONSE_KEY_NAME}** marks a boundary, **SPACE** pauses, "
        "and the **arrow keys** jump back and forward. **BACKSPACE** removes "
        "the mark you just made."
    )
    if st.button("I'm ready", type="primary"):
        goto("practice_viewing")


def screen_practice_viewing() -> None:
    granularity = PRACTICE_ORDER[ss()["practice_index"]]
    attempt = ss()["practice_attempts"][granularity] + 1
    stim = ss()["practice"]
    token = f"{ss()['store'].participant_id}|practice|{granularity}|{attempt}"

    st.markdown(f"#### Practice - {granularity} segmentation")
    result = play(
        stim, token,
        title="Click here to start the practice clip",
        subtitle=f"{config.RESPONSE_KEY_NAME} marks a {granularity} boundary. "
                 "SPACE pauses, arrow keys seek.",
    )

    if is_new_result(result):
        ss()["practice_attempts"][granularity] = attempt
        ss()["practice_result"] = result
        # Not written here: only the accepted attempt is kept, so the CSV
        # write happens in screen_practice_feedback once the outcome is known.
        goto("practice_feedback")


def screen_practice_feedback() -> None:
    granularity = PRACTICE_ORDER[ss()["practice_index"]]
    result = ss()["practice_result"]
    attempt = ss()["practice_attempts"][granularity]
    n = result["n_presses"]
    low, high = practice_bounds(ss()["practice"].duration_sec, granularity)

    session = ss()["session"]
    if n < low:
        outcome = "too_few"
    elif n > high:
        outcome = "too_many"
    else:
        outcome = "passed"

    # Streamlit reruns this screen on every button click, so the attempt is
    # logged once per (granularity, attempt) rather than once per render.
    logged = ss().setdefault("practice_logged", set())
    if (granularity, attempt) not in logged:
        logged.add((granularity, attempt))
        session["practice"].append({
            "granularity": granularity, "attempt": attempt, "n_presses": n,
            "outcome": outcome, "recorded_utc": storage.utc_now(),
        })
        ss()["store"].save_session(session)

    forced = outcome != "passed" and attempt >= config.PRACTICE_MAX_ATTEMPTS

    if outcome == "passed":
        st.success(config.PRACTICE_PASSED)
    elif forced:
        st.warning(
            f"You marked {n} boundaries. That is outside the usual range "
            f"({low}-{high}), but you have practised "
            f"{config.PRACTICE_MAX_ATTEMPTS} times, so let's move on. Please "
            "keep the instructions above in mind."
        )
    else:
        st.error(config.PRACTICE_TOO_FEW if outcome == "too_few"
                 else config.PRACTICE_TOO_MANY)
        st.markdown(
            f"You pressed **{n}** time(s). For a clip this length we typically "
            f"expect **{low}-{high}** {granularity} boundaries."
        )

    if outcome == "passed" or forced:
        # This attempt is the one that counts, so it is the one stored. Earlier
        # rejected runs are deliberately discarded -- they are people finding
        # the keys, not annotations. `attempt` records which run this was.
        stored = ss().setdefault("practice_stored", set())
        if granularity not in stored:
            stored.add(granularity)
            ss()["store"].record_practice(
                {"block_index": 0, "video_id": ss()["practice"].video_id,
                 "granularity": granularity,
                 "viewing_in_block": ss()["practice_index"] + 1},
                result, attempt=attempt,
            )

        last = ss()["practice_index"] == len(PRACTICE_ORDER) - 1
        label = "Start the experiment" if last else "Continue to the next practice"
        if st.button(label, type="primary"):
            if last:
                session["practice_completed"] = True
                ss()["store"].save_session(session)
                goto("block_intro")
            ss()["practice_index"] += 1
            goto("practice_instructions")
    else:
        if st.button("Redo the practice", type="primary"):
            goto("practice_instructions")


# ---------------------------------------------------------- main blocks -----

def screen_resume() -> None:
    store, session = ss()["store"], ss()["session"]
    done, total = store.n_completed(), len(session["schedule"])
    st.markdown(f"### Welcome back, {store.participant_id}")
    st.markdown(
        f"You have completed **{done} of {total}** viewings. Nothing you did "
        "before is lost, and you will continue from the next viewing."
    )
    if st.button("Continue where I left off", type="primary"):
        goto("block_intro")


def screen_block_intro() -> None:
    step = current_step()
    if step is None:
        goto("done")

    store = ss()["store"]
    total = len(ss()["session"]["schedule"])
    done = store.n_completed()
    n_blocks = ss()["session"]["n_main_videos"]

    st.progress(done / total, text=f"Viewing {done + 1} of {total}")
    st.markdown(f"### Video {step['block_index']} of {n_blocks} - "
                f"viewing {step['viewing_in_block']} of {len(config.GRANULARITIES)}")

    if step["viewing_in_block"] == 1:
        st.markdown("This is a **new video**. You will watch it twice.")
    else:
        st.markdown(
            "This is the **same video again**, now at a different granularity. "
            "Read the instructions carefully - they have changed."
        )

    st.markdown(config.INSTRUCTIONS[step["granularity"]])
    st.info(
        f"About {stimulus_by_id(step['video_id']).duration_sec / 60:.0f} minutes, "
        "silent. You can pause and rewind while you watch, but please watch "
        "all of it rather than skipping ahead."
    )

    if st.button("I'm ready - start this viewing", type="primary"):
        goto("viewing")


def screen_viewing() -> None:
    step = current_step()
    if step is None:
        goto("done")

    store = ss()["store"]
    stim = stimulus_by_id(step["video_id"])
    token = (f"{store.participant_id}|{step['block_index']}|"
             f"{step['video_id']}|{step['granularity']}")

    st.markdown(f"#### {step['granularity'].capitalize()} segmentation")
    result = play(
        stim, token,
        title="Click here to start the video",
        subtitle=f"{config.RESPONSE_KEY_NAME} marks a {step['granularity']} "
                 "boundary. SPACE pauses, arrow keys seek.",
    )

    if is_new_result(result):
        store.record_viewing(step, result)
        goto("break")


def screen_break() -> None:
    store = ss()["store"]
    total = len(ss()["session"]["schedule"])
    done = store.n_completed()

    if done >= total:
        goto("done")

    st.progress(done / total, text=f"{done} of {total} viewings complete")
    next_step = ss()["session"]["schedule"][done]

    if next_step["viewing_in_block"] == 1:
        st.markdown(config.BREAK_TEXT)
        label = "Start the next video"
    else:
        st.markdown(
            "### Second viewing\n\nYou have finished the first pass of this "
            "video. Next you will watch the **same video again** at a "
            "different granularity."
        )
        label = "Continue to the second viewing"

    st.success("Progress saved.")
    if st.button(label, type="primary"):
        goto("block_intro")


def screen_done() -> None:
    store = ss()["store"]
    st.balloons()
    st.markdown(config.FINISH_TEXT)
    viewings = store.completed_viewings()
    st.markdown(f"**{len(viewings)}** viewings recorded, "
                f"**{sum(int(v['n_presses']) for v in viewings)}** boundaries "
                "in total.")
    download_buttons(store, prominent=True)


# ------------------------------------------------------------- chrome -------

def download_buttons(store: storage.Store, prominent: bool = False) -> None:
    target = st if prominent else st.sidebar
    target.download_button(
        "Download all my data (.zip)", store.bundle_zip(),
        file_name=f"{store.participant_id}_event_segmentation.zip",
        mime="application/zip", type="primary" if prominent else "secondary",
        use_container_width=True,
    )
    target.download_button(
        "boundaries.csv", store.read_csv_bytes("boundaries"),
        file_name=f"{store.participant_id}_boundaries.csv", mime="text/csv",
        use_container_width=True,
    )
    target.download_button(
        "viewings.csv", store.read_csv_bytes("viewings"),
        file_name=f"{store.participant_id}_viewings.csv", mime="text/csv",
        use_container_width=True,
    )


def sidebar(stage: str) -> None:
    store = ss().get("store")
    if store is None:
        return
    # Hidden mid-viewing: any sidebar widget triggers a rerun, and we keep the
    # page inert while a video is playing.
    if stage in ("viewing", "practice_viewing"):
        st.sidebar.markdown("### Viewing in progress")
        st.sidebar.caption(
            "ENTER marks a boundary, SPACE pauses, arrow keys seek. "
            "Saving and download return when the video ends."
        )
        return

    st.sidebar.markdown(f"### {store.participant_id}")
    total = len(ss()["session"]["schedule"])
    done = store.n_completed()
    st.sidebar.markdown(f"**{done} / {total}** viewings complete")
    st.sidebar.caption(
        "Progress saves automatically after each viewing. You can close the "
        "app and resume with the same Participant ID."
    )
    st.sidebar.divider()
    st.sidebar.markdown("**Save your progress**")
    download_buttons(store)
    st.sidebar.divider()
    if st.sidebar.button("Log out", use_container_width=True):
        st.session_state.clear()
        st.rerun()


SCREENS = {
    "welcome": screen_welcome,
    "overview": screen_overview,
    "comprehension": screen_comprehension,
    "practice_intro": screen_practice_intro,
    "practice_instructions": screen_practice_instructions,
    "practice_viewing": screen_practice_viewing,
    "practice_feedback": screen_practice_feedback,
    "resume": screen_resume,
    "block_intro": screen_block_intro,
    "viewing": screen_viewing,
    "break": screen_break,
    "done": screen_done,
}


def main() -> None:
    try:
        main_videos, practice_stim = storage.load_stimuli()
    except FileNotFoundError as exc:
        st.error(str(exc))
        return

    if not main_videos or practice_stim is None:
        st.error("No stimuli staged. Run: python scripts/prepare_stimuli.py")
        return

    stage = ss().get("stage", "login")
    st.markdown(_CSS_VIEWING if stage in VIEWING_STAGES else _CSS_TEXT,
                unsafe_allow_html=True)

    # Never while a video is playing: nothing should compete with the stimulus.
    if len(main_videos) < config.N_MAIN_VIDEOS and stage not in VIEWING_STAGES:
        st.warning(
            f"Only {len(main_videos)} of {config.N_MAIN_VIDEOS} videos are "
            "staged. New participants will be scheduled for the videos that "
            "are present. See docs/EXPERIMENTER.md, 'Stimuli'."
        )

    sidebar(stage)

    if "store" not in ss() or stage not in SCREENS:
        screen_login(main_videos, practice_stim)
        return

    SCREENS[stage]()


if __name__ == "__main__":
    main()
