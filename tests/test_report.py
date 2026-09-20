from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from faultscribe.report import InputError, build_report, parse_doctor_json, parse_environment, read_text, to_markdown, write_report_pair


class ReportTests(unittest.TestCase):
    def test_normal_unicode_report_pair(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            report = build_report(
                "Unicode failure: 中文 ✓",
                "保存后出现错误。",
                "1. 打开项目\n2. 点击保存",
                {"OS": "测试系统", "Python": "3.x"},
                None,
                created_at="2026-09-20T00:00:00+00:00",
            )
            markdown, data = write_report_pair(report, root, "case")
            self.assertIn("中文 ✓", markdown.read_text(encoding="utf-8"))
            self.assertEqual(json.loads(data.read_text(encoding="utf-8"))["title"], "Unicode failure: 中文 ✓")

    def test_environment_requires_key_value(self) -> None:
        with self.assertRaisesRegex(InputError, "KEY=VALUE"):
            parse_environment(["not-a-pair"])

    def test_corrupt_inputs_are_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "broken.txt"
            path.write_bytes(b"\xff\xfe")
            with self.assertRaisesRegex(InputError, "UTF-8"):
                read_text(path)

    def test_invalid_doctor_json_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "doctor.json"
            path.write_text("{not json", encoding="utf-8")
            with self.assertRaisesRegex(InputError, "invalid doctor JSON"):
                parse_doctor_json(path)

    def test_markdown_uses_only_selected_values(self) -> None:
        report = build_report("T", "D", "", {"OS": "SyntheticOS"}, None, created_at="2026-09-20T00:00:00+00:00")
        markdown = to_markdown(report)
        self.assertIn("SyntheticOS", markdown)
        self.assertIn("Only information explicitly supplied", markdown)
