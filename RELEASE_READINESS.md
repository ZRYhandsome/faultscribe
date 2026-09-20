# Release-readiness record

## Proposed identity

- Project and distribution name: `faultscribe` / FaultScribe.
- Name check on 2026-09-20: PyPI's `faultscribe` endpoint returned HTTP 404, and GitHub's public repository search returned no exact `faultscribe` names in its first ten results. This is a point-in-time check, not a reservation or a guarantee.
- Proposed repository target: `https://github.com/<verified-GitHub-username>/faultscribe`.

## Public-push blockers

1. A current GitHub browser session was verified on 2026-09-20. Confirm its authorization to create the proposed public repository and confirm the target URL. The GitHub CLI is not installed, so token scopes were not available for local inspection.
2. The maintainer confirmed the MIT license on 2026-09-20. The canonical text is `LICENSE`.
3. Review the public file list and Git author metadata. The ignored `application-private/` directory must remain local and untracked.
4. After the first public push, verify repository visibility, the rendered install instructions, the pushed file list, and the actual GitHub Actions result. None has occurred yet.

## Intended public file scope

- Python source: `faultscribe/`
- Tests using synthetic data only: `tests/`
- Documentation and license: `README.md`, `README.zh-CN.md`, `CONTRIBUTING.md`, `SECURITY.md`, `CHANGELOG.md`, `VERIFICATION.md`, `RELEASE_READINESS.md`, `LICENSE`
- Packaging, ignore rules, and minimal-permission CI: `pyproject.toml`, `.gitignore`, `.github/`

Not intended for publication: `application-private/`, generated reports, example inputs/outputs, virtual environments, package artifacts, and any personal material.
