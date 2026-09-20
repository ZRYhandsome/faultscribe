# FaultScribe

FaultScribe is a small, local-first command-line tool for preparing developer-readable failure reports. It has no account, cloud service, telemetry, paid model API, source-code collection, or automatic uploads.

**Status: 0.1.0 is available from this GitHub source repository and is not published to PyPI. It is licensed under MIT. See the repository's Actions tab for the current remote CI result.**

## What it does

- `doctor` records operating-system details and the installed/missing state of a fixed allowlist of developer tools. It runs only each tool's version query, with a per-command timeout; it never runs a checked project's scripts.
- `report` turns explicitly selected text, environment fields, and optional FaultScribe `doctor` JSON into local Markdown and JSON files.
- `redact` makes a separate, best-effort redacted copy of one explicitly named UTF-8 log file, with optional terminal preview. It never modifies the source file.

FaultScribe does **not** automatically collect source code, environment variables, Git remotes, email addresses, real user names, or full absolute paths. Do not put sensitive data into `report` inputs. Inspect every report and redacted output before sharing.

## Install

Requires Python 3.9 or newer. From a source checkout:

```sh
python3 -m pip install .
faultscribe --help
```

For an isolated development install:

```sh
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -e .
```

## Reproducible local example

The following only creates synthetic local files.

```sh
mkdir -p example-input
printf 'Saving a draft returns an error.\n' > example-input/description.txt
printf '1. Open the demo\n2. Save a draft\n' > example-input/steps.txt
faultscribe doctor --output example-input/doctor.json
faultscribe report \
  --title 'Synthetic save failure' \
  --description example-input/description.txt \
  --steps example-input/steps.txt \
  --environment 'OS=selected manually' \
  --doctor-json example-input/doctor.json \
  --output-dir example-output \
  --name synthetic-save-failure
printf 'contact=synthetic.user@example.test\npath=/Users/synthetic-user/demo\n' > example-input/synthetic.log
faultscribe redact example-input/synthetic.log --preview
```

`doctor` will differ by machine. `report` writes `synthetic-save-failure.md` and `synthetic-save-failure.json`; `redact` writes a separate `synthetic.redacted.log`. All paths are local and no command uploads or submits anything.

## Commands

```text
faultscribe doctor [--timeout SECONDS] [--output FILE]
faultscribe report --title TEXT --description FILE [--steps FILE]
                  [--environment KEY=VALUE] [--doctor-json FILE]
                  [--output-dir DIRECTORY] [--name STEM]
faultscribe redact INPUT [--output FILE] [--preview]
```

`doctor --output` and `report` refuse to overwrite an existing output. `redact` requires a path different from the original and also refuses to overwrite. Text inputs must be UTF-8; malformed text and malformed doctor JSON return an error without producing a report.

## Redaction limitations

The rules look for common email, token/key, password-assignment, and local-user-path patterns. This is a convenience filter, not a security guarantee: opaque values, unusual formats, encoded data, screenshots, archives, and future token formats can be missed; benign text can also be replaced. The tool prints this warning each time. Review the original data boundary and the final output yourself before sharing it.

See [SECURITY.md](SECURITY.md) for reporting and handling guidance, [CONTRIBUTING.md](CONTRIBUTING.md) for contribution guidance, and [CHANGELOG.md](CHANGELOG.md) for the version record. Chinese usage notes are in [README.zh-CN.md](README.zh-CN.md).

## Verification status

The repository's status is deliberately split by evidence:

| Check | Status |
| --- | --- |
| Local unit tests | Passed on 2026-09-20: 14 tests with Python 3.9 |
| Local command smoke tests | Passed on 2026-09-20: isolated install; `doctor`, `report`, and `redact`; synthetic Unicode input; source-log hash unchanged |
| GitHub Actions CI | Runs on pushes and pull requests; check the repository Actions tab for the current remote result |
| Windows/Linux behavior | Not yet verified on those platforms |
| PyPI packaging/install | Not yet verified or published |

## License

FaultScribe is licensed under the [MIT License](LICENSE).
