"""Start the experiment, on Windows, macOS or Linux alike.

    python run.py

Plain ``streamlit run app.py`` also works, but only as long as
``.streamlit/config.toml`` is next to it: static file serving is off by
default, and without it the videos never load. That file is hidden, so it is
easily lost when a project is zipped, emailed or copied by hand. This launcher
sets the same option through the environment, so the app works even then.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent


def main() -> int:
    # Streamlit reads its config at startup, before app.py is imported, so the
    # option has to be set out here rather than in the app itself.
    os.environ.setdefault("STREAMLIT_SERVER_ENABLE_STATIC_SERVING", "true")
    os.environ.setdefault("STREAMLIT_BROWSER_GATHER_USAGE_STATS", "false")

    # Run from the project directory whatever path the participant typed, so
    # stimuli/, static/ and responses/ resolve.
    os.chdir(HERE)

    try:
        from streamlit.web import cli as streamlit_cli
    except ImportError:
        sys.stderr.write(
            "Streamlit is not installed in this Python environment.\n"
            "Install it with:  python -m pip install -r requirements.txt\n"
        )
        return 1

    sys.argv = ["streamlit", "run", str(HERE / "app.py")]
    return streamlit_cli.main()


if __name__ == "__main__":
    raise SystemExit(main())
