"""Command-line interface for FaultScribe."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from faultscribe import __version__
from faultscribe.doctor import collect_doctor
from faultscribe.redact import redact_file
from faultscribe.report import InputError, build_report, parse_doctor_json, parse_environment, read_text, write_report_pair


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="faultscribe",
        description="Prepare local, developer-readable failure reports without automatic data collection.",
    )
    parser.add_argument("--version", action="version", version=f"FaultScribe {__version__}")
    commands = parser.add_subparsers(dest="command", required=True)

    doctor = commands.add_parser("doctor", help="inspect the OS and fixed allowlisted developer-tool version commands")
    doctor.add_argument("--timeout", type=float, default=2.0, help="per-command timeout in seconds (default: 2.0)")
    doctor.add_argument("--output", type=Path, help="write JSON to this new local file instead of standard output")

    report = commands.add_parser("report", help="write Markdown and JSON from information you explicitly select")
    report.add_argument("--title", required=True, help="short report title")
    report.add_argument("--description", required=True, type=Path, help="UTF-8 text file containing the problem description")
    report.add_argument("--steps", type=Path, help="optional UTF-8 text file with reproduction steps")
    report.add_argument("--environment", action="append", default=[], metavar="KEY=VALUE", help="selected environment item; may be repeated")
    report.add_argument("--doctor-json", type=Path, help="optional doctor JSON produced by this tool")
    report.add_argument("--output-dir", type=Path, default=Path("reports"), help="local output directory (default: reports)")
    report.add_argument("--name", default="faultscribe-report", help="output filename stem (default: faultscribe-report)")

    redact = commands.add_parser("redact", help="best-effort offline redaction of one explicitly selected UTF-8 text log")
    redact.add_argument("input", type=Path, help="input text log; it is never modified")
    redact.add_argument("--output", type=Path, help="new output path (default: INPUT.redacted.EXT)")
    redact.add_argument("--preview", action="store_true", help="print redacted text to standard output after writing it")
    return parser


def _write_new_json(path: Path, data: dict[str, object]) -> None:
    if path.exists():
        raise InputError(f"refusing to overwrite existing output: {path}")
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    except OSError as error:
        raise InputError(f"cannot write {path}: {error.strerror or error}") from error


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        if args.command == "doctor":
            result = collect_doctor(args.timeout)
            if args.output:
                _write_new_json(args.output, result)
                print(f"Wrote doctor output to {args.output}")
            else:
                print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0
        if args.command == "report":
            description = read_text(args.description)
            steps = read_text(args.steps) if args.steps else ""
            report = build_report(
                args.title, description, steps, parse_environment(args.environment), parse_doctor_json(args.doctor_json)
            )
            markdown_path, json_path = write_report_pair(report, args.output_dir, args.name)
            print(f"Wrote local report files: {markdown_path} and {json_path}")
            return 0
        if args.command == "redact":
            output_path, preview, counts = redact_file(args.input, args.output)
            print(f"Wrote redacted copy: {output_path}", file=sys.stderr)
            print(f"Replacements: {json.dumps(counts, sort_keys=True)}", file=sys.stderr)
            print("Warning: pattern-based redaction can miss secrets or redact benign text; inspect the output before sharing.", file=sys.stderr)
            if args.preview:
                print(preview, end="" if preview.endswith("\n") else "\n")
            return 0
    except (InputError, ValueError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2
    return 2
