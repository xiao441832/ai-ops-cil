"""Tests for the LLM module's response parsing."""

from ai_ops.llm import _strip_code_fences


class TestStripCodeFences:
    """Test markdown code fence stripping."""

    def test_bash_fence(self):
        result = _strip_code_fences("```bash\nls -la\n```")
        assert result == "ls -la"

    def test_plain_fence(self):
        result = _strip_code_fences("```\nls -la\n```")
        assert result == "ls -la"

    def test_sh_fence(self):
        result = _strip_code_fences("```sh\ndu -sh *\n```")
        assert result == "du -sh *"

    def test_no_fence(self):
        result = _strip_code_fences("ls -la")
        assert result == "ls -la"

    def test_fence_with_extra_whitespace(self):
        result = _strip_code_fences("  ```bash\nls -la\n  ```  ")
        assert result == "ls -la"

    def test_multiline_in_fence(self):
        result = _strip_code_fences("```bash\nfind . -name '*.log'\n| xargs rm\n```")
        assert "find . -name '*.log'" in result

    def test_plain_text_explanation(self):
        raw = "The command to list files is:\n```bash\nls -la\n```"
        result = _strip_code_fences(raw)
        # The regex only matches if the ENTIRE text is a fence
        assert result == raw
