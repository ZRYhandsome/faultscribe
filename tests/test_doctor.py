from __future__ import annotations

import subprocess
import unittest

from faultscribe.doctor import ToolSpec, collect_doctor


class DoctorTests(unittest.TestCase):
    def test_missing_tool_is_not_run(self) -> None:
        calls: list[object] = []

        def runner(*args: object, **kwargs: object) -> subprocess.CompletedProcess[str]:
            calls.append(args)
            raise AssertionError("missing tools must not be run")

        result = collect_doctor(
            specs=(ToolSpec("synthetic-missing", ("synthetic-missing", "--version")),),
            runner=runner,
            which=lambda _: None,
        )
        self.assertEqual(result["tools"][0]["status"], "missing")  # type: ignore[index]
        self.assertEqual(calls, [])

    def test_timeout_is_reported(self) -> None:
        def runner(*args: object, **kwargs: object) -> subprocess.CompletedProcess[str]:
            raise subprocess.TimeoutExpired(["synthetic", "--version"], 0.01)

        result = collect_doctor(
            specs=(ToolSpec("synthetic-slow", ("synthetic", "--version")),),
            runner=runner,
            which=lambda _: "/synthetic",
        )
        self.assertEqual(result["tools"][0]["status"], "timeout")  # type: ignore[index]

    def test_only_fixed_version_commands_are_declared(self) -> None:
        result = collect_doctor(
            specs=(ToolSpec("synthetic", ("synthetic", "--version")),),
            runner=lambda *args, **kwargs: subprocess.CompletedProcess(args[0], 0, "synthetic 1.0\n", ""),  # type: ignore[index]
            which=lambda _: "/synthetic",
        )
        tool = result["tools"][0]  # type: ignore[index]
        self.assertEqual(tool["status"], "available")
        self.assertEqual(tool["version"], "synthetic 1.0")
