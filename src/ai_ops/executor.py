from __future__ import annotations

import os
import subprocess
import sys


def run(command: str) -> int:
    """Execute command with real-time output, preserving colors.

    Returns the subprocess exit code.
    """
    # Skip execution if command is a comment (safety-intercepted)
    if command.lstrip().startswith("#"):
        print(f"（注释命令，跳过执行: {command}）")
        return 0

    shell = os.environ.get("COMSPEC", "cmd.exe") if sys.platform == "win32" else os.environ.get("SHELL", "/bin/bash")

    if sys.platform == "win32":
        cmd = [shell, "/c", command]
    else:
        cmd = [shell, "-c", command]

    try:
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            bufsize=0,
        )

        # Stream output in real-time
        while True:
            chunk = proc.stdout.read(4096)
            if not chunk:
                break
            sys.stdout.buffer.write(chunk)
            sys.stdout.buffer.flush()

        proc.wait()
        return proc.returncode
    except FileNotFoundError:
        print(f"错误: 找不到 shell: {shell}", file=sys.stderr)
        return 127
    except OSError as e:
        print(f"错误: {e}", file=sys.stderr)
        return 1
