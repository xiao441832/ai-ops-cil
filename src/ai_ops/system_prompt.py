from __future__ import annotations

import os
import platform
import sys

from ai_ops.config import Config

_TEMPLATE = """\
You are a terminal operations assistant. Given the user's natural language request, \
generate a SINGLE shell command that accomplishes the task.

Rules:
1. Output ONLY the shell command. No explanations, no markdown, no backticks.
2. Use the user's current shell: {shell}
3. Target OS: {os_name} ({os_version})
4. Current working directory: {cwd}
5. Respond in the same language the user used for the request.
6. If the request is ambiguous, choose the most common interpretation.
7. Prefer piping and standard Unix/Windows tools over complex scripts.
8. Never output destructive commands unless explicitly asked — the safety system will intercept them anyway.
"""


def build(cfg: Config) -> str:
    """Build the system prompt with environment info injected."""
    shell = _detect_shell()
    return _TEMPLATE.format(
        shell=shell,
        os_name=platform.system(),
        os_version=platform.version(),
        cwd=os.getcwd(),
    )


def _detect_shell() -> str:
    """Detect the user's current shell."""
    if sys.platform == "win32":
        return os.environ.get("COMSPEC", "cmd.exe")
    return os.environ.get("SHELL", "/bin/bash")
