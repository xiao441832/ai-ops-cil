from __future__ import annotations

import time


class Timer:
    """Async-compatible timer context manager."""

    def __init__(self) -> None:
        self.start: float = 0.0
        self.elapsed: float = 0.0

    async def __aenter__(self) -> Timer:
        self.start = time.monotonic()
        return self

    async def __aexit__(self, *args: object) -> None:
        self.elapsed = time.monotonic() - self.start
