"""Safe, bounded developer-tool discovery."""

from __future__ import annotations

import platform
import shutil
import subprocess
import sys
from dataclasses import asdict, dataclass
from typing import Callable, Iterable, Optional

DEFAULT_TIMEOUT_SECONDS = 2.0


@dataclass(frozen=True)
class ToolSpec:
    name: str
    command: tuple[str, ...]


# This is intentionally an allowlist of version-only commands.  No project
# command, shell, or user-provided executable is ever run by ``doctor``.
SAFE_TOOL_SPECS: tuple[ToolSpec, ...] = (
    ToolSpec("git", ("git", "--version")),
    ToolSpec("node", ("node", "--version")),
    ToolSpec("npm", ("npm", "--version")),
    ToolSpec("pnpm", ("pnpm", "--version")),
    ToolSpec("yarn", ("yarn", "--version")),
    ToolSpec("python", ("python3", "--version")),
    ToolSpec("docker", ("docker", "--version")),
    ToolSpec("go", ("go", "version")),
    ToolSpec("cargo", ("cargo", "--version")),
    ToolSpec("rustc", ("rustc", "--version")),
    ToolSpec("java", ("java", "-version")),
    ToolSpec("swift", ("swift", "--version")),
)


Runner = Callable[..., subprocess.CompletedProcess[str]]
Which = Callable[[str], Optional[str]]


def _system_info() -> dict[str, str]:
    return {
        "platform": platform.system(),
        "platform_release": platform.release(),
        "architecture": platform.machine(),
        "python": sys.version.split()[0],
    }


def _run_tool(spec: ToolSpec, timeout: float, runner: Runner) -> dict[str, object]:
    try:
        completed = runner(
            list(spec.command),
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
    except subprocess.TimeoutExpired:
        return {"name": spec.name, "status": "timeout", "command": list(spec.command)}
    except OSError as error:
        return {
            "name": spec.name,
            "status": "error",
            "command": list(spec.command),
            "detail": str(error),
        }

    output = (completed.stdout or completed.stderr or "").strip().splitlines()
    if completed.returncode != 0:
        return {
            "name": spec.name,
            "status": "error",
            "command": list(spec.command),
            "returncode": completed.returncode,
            "detail": output[0] if output else "version command returned a non-zero exit status",
        }
    return {
        "name": spec.name,
        "status": "available",
        "command": list(spec.command),
        "version": output[0] if output else "(no version output)",
    }


def collect_doctor(
    timeout: float = DEFAULT_TIMEOUT_SECONDS,
    specs: Iterable[ToolSpec] = SAFE_TOOL_SPECS,
    runner: Runner = subprocess.run,
    which: Which = shutil.which,
) -> dict[str, object]:
    """Return system and allowed-tool results without executing project code."""
    if timeout <= 0:
        raise ValueError("timeout must be greater than zero")

    tools = []
    for spec in specs:
        if which(spec.command[0]) is None:
            tools.append({"name": spec.name, "status": "missing", "command": list(spec.command)})
        else:
            tools.append(_run_tool(spec, timeout, runner))
    return {"system": _system_info(), "tools": tools}
