from __future__ import annotations

import re

import httpx

from ai_ops.config import Config
from ai_ops import system_prompt


async def call(user_prompt: str, cfg: Config) -> tuple[str, int]:
    """Call OpenAI-compatible chat completions API.

    Returns (command_string, total_tokens).
    """
    url = f"{cfg.llm.base_url.rstrip('/')}/chat/completions"
    headers = {
        "Authorization": f"Bearer {cfg.llm.api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": cfg.llm.model,
        "messages": [
            {"role": "system", "content": system_prompt.build(cfg)},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": cfg.llm.temperature,
        "max_tokens": cfg.llm.max_tokens,
    }

    async with httpx.AsyncClient(timeout=cfg.llm.timeout_seconds) as client:
        resp = await client.post(url, headers=headers, json=payload)
        resp.raise_for_status()
        data = resp.json()

    content = data["choices"][0]["message"]["content"].strip()
    tokens = data.get("usage", {}).get("total_tokens", 0)

    command = _strip_code_fences(content)
    # Take only the first non-empty line as the command
    command = next((line for line in command.splitlines() if line.strip()), "")

    return command, tokens


def _strip_code_fences(text: str) -> str:
    """Strip all markdown formatting LLMs commonly add around commands.

    Handles: ```lang\\ncmd\\n```, `cmd`, and mixed surrounding text.
    """
    # 1. Try multi-line triple-backtick fence (e.g. ```bash\\ncmd\\n```)
    m = re.search(r"```(?:\w+)?\s*\n(.*?)\n\s*```", text, re.DOTALL)
    if m:
        return m.group(1)
    # 2. Try single-line triple-backtick fence (e.g. ```df -h```)
    m = re.search(r"```(.+?)```", text)
    if m:
        return m.group(1).strip()
    # 3. Try inline backtick (e.g. `df -h`)
    m = re.search(r"`([^`]+)`", text)
    if m:
        return m.group(1).strip()
    return text
