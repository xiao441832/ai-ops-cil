from __future__ import annotations

import os
import sys

from prompt_toolkit import PromptSession


def prompt(default_text: str) -> str | None:
    """Open a prompt_toolkit session with default text pre-filled.

    Returns the final command string, or None if user pressed Ctrl+C.
    """
    session = PromptSession()

    # If prompt_toolkit has issues (e.g. no TTY), fall back to basic input()
    try:
        result = session.prompt(
            message="> ",
            default=default_text,
        )
        return result
    except (KeyboardInterrupt, EOFError):
        return None
    except Exception:
        # Graceful degradation to basic input
        print(f"> {default_text}")
        try:
            user_input = input()
            return user_input if user_input else default_text
        except (KeyboardInterrupt, EOFError):
            return None
