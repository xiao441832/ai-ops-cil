from __future__ import annotations

import asyncio

from prompt_toolkit import PromptSession


async def prompt_async(default_text: str) -> str | None:
    """Show a pre-filled prompt and return the user's edited command."""
    session = PromptSession()
    try:
        result = await session.prompt_async(
            message="> ",
            default=default_text,
        )
        return result
    except (KeyboardInterrupt, EOFError):
        return None
    except Exception:
        # Fallback to plain input if prompt_toolkit fails
        print(f"> {default_text}")
        try:
            user_input = await asyncio.to_thread(input)
            return user_input if user_input else default_text
        except (KeyboardInterrupt, EOFError):
            return None
