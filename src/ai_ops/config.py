from __future__ import annotations

import sys
from dataclasses import dataclass, field
from pathlib import Path

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib

import tomli_w

CONFIG_DIR = Path.home() / ".aiops"
CONFIG_FILE = CONFIG_DIR / "config.toml"

DEFAULT_CONFIG = {
    "llm": {
        "base_url": "https://api.openai.com/v1",
        "api_key": "",
        "model": "gpt-4o",
        "temperature": 0.0,
        "max_tokens": 256,
        "timeout_seconds": 30,
    },
    "safety": {
        "comment_mode": True,
        "extra_deny_patterns": [],
    },
    "display": {
        "language": "zh-CN",
        "animation_style": "spinner",
    },
}


@dataclass
class LLMConfig:
    base_url: str = "https://api.openai.com/v1"
    api_key: str = ""
    model: str = "gpt-4o"
    temperature: float = 0.0
    max_tokens: int = 256
    timeout_seconds: int = 30


@dataclass
class SafetyConfig:
    comment_mode: bool = True
    extra_deny_patterns: list[str] = field(default_factory=list)


@dataclass
class DisplayConfig:
    language: str = "zh-CN"
    animation_style: str = "spinner"


@dataclass
class Config:
    llm: LLMConfig = field(default_factory=LLMConfig)
    safety: SafetyConfig = field(default_factory=SafetyConfig)
    display: DisplayConfig = field(default_factory=DisplayConfig)


def load() -> Config:
    """Load config from ~/.aiops/config.toml.

    If the file doesn't exist, create it with defaults and exit with instructions.
    If api_key is missing, exit with instructions.
    """
    if not CONFIG_FILE.exists():
        _init_config()

    with CONFIG_FILE.open("rb") as f:
        raw = tomllib.load(f)

    cfg = Config()
    if "llm" in raw:
        cfg.llm = LLMConfig(**{k: v for k, v in raw["llm"].items() if k in LLMConfig.__dataclass_fields__})
    if "safety" in raw:
        cfg.safety = SafetyConfig(**{k: v for k, v in raw["safety"].items() if k in SafetyConfig.__dataclass_fields__})
    if "display" in raw:
        cfg.display = DisplayConfig(**{k: v for k, v in raw["display"].items() if k in DisplayConfig.__dataclass_fields__})

    if not cfg.llm.api_key:
        print(f"请在 {CONFIG_FILE} 中设置 llm.api_key")
        sys.exit(1)

    return cfg


def _init_config() -> None:
    """Create default config file on first run."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with CONFIG_FILE.open("wb") as f:
        tomli_w.dump(DEFAULT_CONFIG, f)
    print(f"未找到配置文件。已在 {CONFIG_FILE} 创建默认配置，请填入 api_key 后重试。")
    sys.exit(1)
