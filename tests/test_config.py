"""Tests for the config module."""

import os
import tempfile
from pathlib import Path
from unittest import mock

from ai_ops.config import Config, LLMConfig, SafetyConfig, DisplayConfig


class TestConfigDataclass:
    """Test config dataclass defaults."""

    def test_default_config(self):
        cfg = Config()
        assert cfg.llm.base_url == "https://api.openai.com/v1"
        assert cfg.llm.api_key == ""
        assert cfg.llm.model == "gpt-4o"
        assert cfg.llm.temperature == 0.0
        assert cfg.llm.max_tokens == 256
        assert cfg.llm.timeout_seconds == 30

    def test_safety_defaults(self):
        cfg = Config()
        assert cfg.safety.comment_mode is True
        assert cfg.safety.extra_deny_patterns == []

    def test_display_defaults(self):
        cfg = Config()
        assert cfg.display.language == "zh-CN"
        assert cfg.display.animation_style == "spinner"


class TestLoadConfig:
    """Test config loading from file."""

    def test_load_with_api_key(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.toml"
            config_path.write_text(
                '[llm]\nbase_url = "https://api.example.com/v1"\n'
                'api_key = "sk-test123"\nmodel = "gpt-4o-mini"\n'
                "temperature = 0.5\nmax_tokens = 512\ntimeout_seconds = 60\n"
            )
            with mock.patch("ai_ops.config.CONFIG_FILE", config_path):
                from ai_ops.config import load
                cfg = load()
                assert cfg.llm.api_key == "sk-test123"
                assert cfg.llm.base_url == "https://api.example.com/v1"
                assert cfg.llm.model == "gpt-4o-mini"
                assert cfg.llm.temperature == 0.5
                assert cfg.llm.max_tokens == 512

    def test_load_missing_api_key_exits(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.toml"
            config_path.write_text('[llm]\napi_key = ""\n')
            with mock.patch("ai_ops.config.CONFIG_FILE", config_path):
                from ai_ops.config import load
                try:
                    load()
                    assert False, "Should have exited"
                except SystemExit as e:
                    assert e.code == 1

    def test_load_missing_file_creates_default(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.toml"
            with mock.patch("ai_ops.config.CONFIG_FILE", config_path):
                from ai_ops.config import load
                try:
                    load()
                    assert False, "Should have exited"
                except SystemExit:
                    pass
                assert config_path.exists()

    def test_load_with_extra_deny_patterns(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.toml"
            config_path.write_text(
                '[llm]\napi_key = "sk-test"\n\n'
                '[safety]\nextra_deny_patterns = ["custom-danger"]\n'
            )
            with mock.patch("ai_ops.config.CONFIG_FILE", config_path):
                from ai_ops.config import load
                cfg = load()
                assert "custom-danger" in cfg.safety.extra_deny_patterns
