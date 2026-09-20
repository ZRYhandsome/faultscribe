"""Local report construction with an explicit, user-selected data boundary."""

from __future__ import annotations

import datetime as dt
import json
from pathlib import Path
from typing import Iterable


class InputError(ValueError):
    """Raised when a selected report input cannot be safely read or parsed."""


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError as error:
        raise InputError(f"{path}: expected UTF-8 text ({error.reason})") from error
    except OSError as error:
        raise InputError(f"cannot read {path}: {error.strerror or error}") from error


def parse_environment(items: Iterable[str]) -> dict[str, str]:
    environment: dict[str, str] = {}
    for item in items:
        if "=" not in item:
            raise InputError(f"invalid --environment value {item!r}; use KEY=VALUE")
        key, value = item.split("=", 1)
        if not key.strip():
            raise InputError("environment keys cannot be empty")
        environment[key.strip()] = value.strip()
    return environment


def parse_doctor_json(path: Path | None) -> dict[str, object] | None:
    if path is None:
        return None
    try:
        data = json.loads(read_text(path))
    except json.JSONDecodeError as error:
        raise InputError(f"{path}: invalid doctor JSON at line {error.lineno}, column {error.colno}") from error
    if not isinstance(data, dict):
        raise InputError(f"{path}: doctor JSON must contain an object")
    return data


def build_report(
    title: str,
    description: str,
    steps: str,
    environment: dict[str, str],
    doctor: dict[str, object] | None,
    created_at: str | None = None,
) -> dict[str, object]:
    if not title.strip():
        raise InputError("title cannot be empty")
    if not description.strip():
        raise InputError("description cannot be empty")

    return {
        "schema_version": 1,
        "created_at": created_at or dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat(),
        "title": title.strip(),
        "description": description,
        "reproduction_steps": steps,
        "environment": environment,
        "doctor": doctor,
        "collection_notice": (
            "Only information explicitly supplied to this command is included. "
            "FaultScribe does not automatically collect source code, environment variables, "
            "Git remotes, email addresses, user names, or absolute paths."
        ),
    }


def to_markdown(report: dict[str, object]) -> str:
    environment = report["environment"]
    assert isinstance(environment, dict)
    steps = str(report["reproduction_steps"]).strip()
    doctor = report.get("doctor")
    lines = [
        f"# {report['title']}",
        "",
        f"Created (UTC): {report['created_at']}",
        "",
        "## Problem description",
        "",
        str(report["description"]).rstrip(),
        "",
        "## Reproduction steps",
        "",
        steps or "Not provided.",
        "",
        "## Selected environment information",
        "",
    ]
    if environment:
        lines.extend(f"- **{key}**: {value}" for key, value in environment.items())
    else:
        lines.append("Not provided.")
    if doctor is not None:
        lines.extend(["", "## Doctor output", "", "```json", json.dumps(doctor, ensure_ascii=False, indent=2), "```"])
    lines.extend(["", "## Collection boundary", "", str(report["collection_notice"]), ""])
    return "\n".join(lines)


def write_report_pair(report: dict[str, object], output_dir: Path, stem: str) -> tuple[Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    markdown_path = output_dir / f"{stem}.md"
    json_path = output_dir / f"{stem}.json"
    if markdown_path.exists() or json_path.exists():
        raise InputError(f"refusing to overwrite existing report: {markdown_path} or {json_path}")
    try:
        markdown_path.write_text(to_markdown(report), encoding="utf-8")
        json_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    except OSError as error:
        raise InputError(f"cannot write report files: {error.strerror or error}") from error
    return markdown_path, json_path
