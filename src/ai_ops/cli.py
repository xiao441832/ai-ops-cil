from __future__ import annotations

import asyncio
import sys

from ai_ops import config, executor, llm, prefill, safety, utils


def main() -> None:
    """CLI entry point for @ai / ai-ops."""
    if len(sys.argv) < 2:
        print("Usage: @ai <natural language description>")
        print("  Example: @ai 查询当前目录下最大的三个文件")
        sys.exit(1)

    user_prompt = " ".join(sys.argv[1:])
    cfg = config.load()

    try:
        asyncio.run(_run(user_prompt, cfg))
    except KeyboardInterrupt:
        print("\n已退出")
        sys.exit(130)
    except httpx_errors() as e:
        _handle_network_error(e, cfg)
    except Exception as e:
        print(f"错误: {e}", file=sys.stderr)
        sys.exit(1)


def httpx_errors() -> tuple[type[Exception], ...]:
    """Return httpx error types lazily (avoid import error if httpx not installed)."""
    import httpx
    return (httpx.ConnectError, httpx.TimeoutException, httpx.HTTPStatusError)


def _handle_network_error(e: Exception, cfg: config.Config) -> None:
    """Handle httpx network errors with user-friendly messages."""
    import httpx
    if isinstance(e, httpx.ConnectError):
        print(f"无法连接到 LLM 服务 ({cfg.llm.base_url})，请检查网络或 base_url 配置")
    elif isinstance(e, httpx.TimeoutException):
        print(f"LLM 服务响应超时 ({cfg.llm.timeout_seconds}s)，请稍后重试")
    elif isinstance(e, httpx.HTTPStatusError):
        if e.response.status_code in (401, 403):
            print(f"API 密钥无效，请检查 {config.CONFIG_FILE} 中的 llm.api_key")
        elif e.response.status_code == 429:
            print("API 调用频率超限，请稍后重试")
        else:
            print(f"LLM 服务错误: {e.response.status_code}")
    sys.exit(1)


async def _run(user_prompt: str, cfg: config.Config) -> None:
    """Main async pipeline: think → safety → prefill → execute."""
    # Phase 1: Call LLM with spinner
    print("AI 正在思考...")

    async with utils.Timer() as t:
        spinner_task = asyncio.create_task(_spinner())
        llm_task = asyncio.create_task(llm.call(user_prompt, cfg))

        command, tokens = await llm_task

        # Stop spinner
        spinner_task.cancel()
        try:
            await spinner_task
        except asyncio.CancelledError:
            pass

    # Clear the "AI 正在思考..." line
    sys.stdout.write("\r" + " " * 30 + "\r")
    sys.stdout.flush()

    if not command:
        print("LLM 未返回有效命令，请尝试更具体的描述")
        sys.exit(1)

    # Phase 2: Safety validation
    safe_cmd, intercepted = safety.validate_with_extra(
        command, cfg.safety.extra_deny_patterns
    )
    if intercepted:
        print("⚠ 检测到风险命令，已转为注释")

    # Phase 3: Show completion metrics
    print(f"思考完成，请回车执行（耗时 {t.elapsed:.1f}s, token: {tokens}）")

    # Phase 4: Prefill and wait for user
    final_cmd = prefill.prompt(safe_cmd)
    if final_cmd is None:
        print("已取消")
        return

    # Phase 5: Execute
    returncode = executor.run(final_cmd)
    sys.exit(returncode)


async def _spinner() -> None:
    """Simple spinner animation for async waiting."""
    import itertools
    chars = itertools.cycle("⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏")
    try:
        while True:
            sys.stdout.write(f"\rAI 正在思考... {next(chars)}")
            sys.stdout.flush()
            await asyncio.sleep(0.1)
    except asyncio.CancelledError:
        pass
