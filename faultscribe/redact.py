"""Best-effort, offline text-log redaction."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from faultscribe.report import InputError, read_text


@dataclass(frozen=True)
class Rule:
    name: str
    pattern: re.Pattern[str]


RULES: tuple[Rule, ...] = (
    Rule("email", re.compile(r"(?<![\w.+-])[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}(?![\w.-])")),
    Rule("github_token", re.compile(r"\bgh[pousr]_[A-Za-z0-9_]{30,}\b")),
    Rule("openai_style_key", re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b")),
    Rule("aws_access_key", re.compile(r"\b(?:AKIA|ASIA)[A-Z0-9]{16}\b")),
    Rule("assigned_secret", re.compile(r"(?i)\b(api[_-]?key|access[_-]?token|auth[_-]?token|secret|password)\b(\s*[:=]\s*)([^\s\"']{8,})")),
    Rule("macos_user_path", re.compile(r"/Users/[^/\s]+")),
    Rule("linux_user_path", re.compile(r"/home/[^/\s]+")),
    Rule("windows_user_path", re.compile(r"(?i)\b[A-Z]:\\Users\\[^\\\s]+")),
)


def redact_text(text: str) -> tuple[str, dict[str, int]]:
    """Apply conservative pattern rules and return per-rule replacement counts."""
    counts: dict[str, int] = {}
    redacted = text
    for rule in RULES:
        if rule.name == "assigned_secret":
            redacted, count = rule.pattern.subn(
                lambda match: f"{match.group(1)}{match.group(2)}[REDACTED:{rule.name}]", redacted
            )
        else:
            redacted, count = rule.pattern.subn(f"[REDACTED:{rule.name}]", redacted)
        counts[rule.name] = count
    return redacted, counts


def default_output_path(input_path: Path) -> Path:
    suffix = input_path.suffix or ".txt"
    return input_path.with_name(f"{input_path.stem}.redacted{suffix}")


def redact_file(input_path: Path, output_path: Path | None = None) -> tuple[Path, str, dict[str, int]]:
    input_path = input_path.resolve()
    if not input_path.is_file():
        raise InputError(f"input is not a regular file: {input_path}")
    output_path = (output_path or default_output_path(input_path)).resolve()
    if output_path == input_path:
        raise InputError("output path must be different from the original file")
    if output_path.exists():
        raise InputError(f"refusing to overwrite existing output: {output_path}")
    original = read_text(input_path)
    redacted, counts = redact_text(original)
    try:
        output_path.write_text(redacted, encoding="utf-8")
    except OSError as error:
        raise InputError(f"cannot write redacted file {output_path}: {error.strerror or error}") from error
    return output_path, redacted, counts
