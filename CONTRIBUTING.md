# Contributing to FaultScribe

Thank you for considering a contribution. FaultScribe is intentionally local-first and dependency-light.

## Before opening a change

1. Do not include real secrets, personal logs, credentials, proprietary source code, or data from a third-party project in an issue, test, fixture, or commit.
2. Use small, focused changes and add tests for behavior changes.
3. Run `python3 -m unittest discover -v` locally.
4. Describe what was actually tested and on which platform. Do not mark unrun checks or untested platforms as passing.

## Scope principles

- No automatic uploads, account requirements, tracking, or calls to paid model APIs.
- `doctor` additions must be fixed, documented version-only commands with a timeout. It must never execute a target project's scripts or arbitrary user-provided commands.
- Redaction patterns must be documented as best effort. A rule needs tests for an intended match and a false-positive/false-negative boundary where practical.
- Preserve input files: commands should create new outputs and refuse unsafe overwrites by default.

## License

Contributions are offered under the repository's MIT License.
