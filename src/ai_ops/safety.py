from __future__ import annotations

import re

# ---------------------------------------------------------------------------
# Built-in deny patterns — organized by threat category
# ---------------------------------------------------------------------------

_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    # -- Destructive file operations --
    ("rm -rf variant",
     re.compile(r"rm\s+(-\w*f\w*|\w*f\w*-)\S*\s+", re.IGNORECASE)),
    ("rm -rf root",
     re.compile(r"rm\s+-\w*[rf]\w*[rf]\w*\s+/")),
    ("mkfs",
     re.compile(r"\bmkfs\b")),
    ("dd to disk",
     re.compile(r"\bdd\s+.*of=/dev/")),
    ("shred",
     re.compile(r"\bshred\s")),
    ("direct disk write",
     re.compile(r">\s*/dev/sd[a-z]")),

    # -- Database destruction --
    ("SQL DROP DATABASE",
     re.compile(r"(?i)(drop\s+database|drop\s+schema|truncate\s+table)")),
    ("MongoDB dropDatabase",
     re.compile(r"(?i)(db\.dropDatabase|db\.runCommand.*drop)")),
    ("Redis FLUSH",
     re.compile(r"(?i)(redis-cli.*flushall|redis-cli.*flushdb)")),

    # -- Permissions / System --
    ("chmod 000 root",
     re.compile(r"chmod\s+(-R\s+)?0{3,4}\s+/")),
    ("chown root",
     re.compile(r"chown\s+.*\s+/")),
    ("stop critical service",
     re.compile(r"(?i)(systemctl\s+(stop|disable)\s+(ssh|sshd|network|firewall))")),
    ("shutdown/reboot",
     re.compile(r"(?i)(\bshutdown\b|\breboot\b|\bhalt\b|\bpoweroff\b)")),
    ("iptables flush",
     re.compile(r"\biptables\s+-F\b")),
    ("crontab remove",
     re.compile(r"\bcrontab\s+-r\b")),

    # -- Network / Data exfiltration --
    ("curl|sh pipe",
     re.compile(r"(?i)(curl|wget)\s+.*\|\s*(ba)?sh")),
    ("netcat reverse shell",
     re.compile(r"\bnc\s+.*-e\s+/")),
]


def validate(command: str) -> tuple[str, bool]:
    """Check command against deny-list patterns.

    Returns (safe_command, was_intercepted).
    If intercepted, the command is converted to a comment.
    """
    command = command.strip()
    if not command:
        return ("", False)

    # Check built-in patterns
    for _name, pattern in _PATTERNS:
        if pattern.search(command):
            return (f"# 已拦截风险命令: {command}", True)

    return (command, False)


def load_extra_patterns(patterns: list[str]) -> list[re.Pattern[str]]:
    """Compile user-defined extra deny patterns from config."""
    return [re.compile(p) for p in patterns]


def validate_with_extra(command: str, extra_patterns: list[str]) -> tuple[str, bool]:
    """Validate with both built-in and user-defined patterns."""
    safe_cmd, intercepted = validate(command)
    if intercepted:
        return (safe_cmd, True)

    # Check extra patterns
    for pattern_str in extra_patterns:
        try:
            if re.search(pattern_str, command):
                return (f"# 已拦截风险命令: {command}", True)
        except re.error:
            continue

    return (command, False)
