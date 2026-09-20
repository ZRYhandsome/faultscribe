# Verification record

This record is intentionally narrow: it distinguishes commands actually run locally from checks that need a remote service or another platform.

## Passed locally — 2026-09-20

- `python3 -m compileall -q faultscribe tests`
- `python3 -m unittest discover -v` — **14 tests passed** under Python 3.9.
  - Covers normal report input, Unicode, malformed UTF-8, malformed doctor JSON, missing tool, timeout handling, empty logs, redaction matches, false-positive boundary words, an intentionally opaque-value limitation, separate output, and source-file preservation.
- Clean Python 3.12 virtual environment — built and installed `faultscribe-0.1.0-py3-none-any.whl`, then ran the installed `faultscribe` executable end to end with synthetic local files. `doctor --output`, `report`, and `redact --preview` succeeded; Markdown/JSON files were created, email/path replacements appeared in preview, and SHA-256 hashes before/after confirmed the original synthetic log was unchanged.
- Wheel metadata — Python 3.12 and 3.13 with pip 25.3 each built `faultscribe-0.1.0-py3-none-any.whl` with name, version, console-script metadata, and MIT license metadata.
- The macOS Xcode Python 3.9 bundled pip 21.2.4 incorrectly built `UNKNOWN-0.0.0`; that old-installer result is not counted as packaging verification. Python 3.9 source tests above did pass. The project has not been tested with a newer Python 3.9 installer.

## Not yet verified

- GitHub Actions run #1 on 2026-09-20 failed because its final help check still invoked the pre-rename command `repropack --help` (exit 127). The workflow is corrected in a subsequent commit; its resulting run must pass before CI can be reported as passing.
- Windows and Linux have not been tested.
- PyPI build, upload, and installation from a published distribution have not been attempted.
- No external user feedback, adoption, downloads, stars, issues, contributors, or security review exists.

No simulation, unrun command, or untested platform is represented above as passed.
