# Security and privacy boundaries

FaultScribe operates locally and has no network client, telemetry, account system, automatic upload, or automatic submission feature.

## Data handling

- `doctor` only runs a fixed allowlist of version queries with a timeout. It does not run project scripts.
- `report` includes only fields and files explicitly selected by the operator. It does not automatically read source code, environment variables, Git remotes, emails, user names, or paths.
- `redact` reads exactly one operator-specified UTF-8 text file and writes a new output; the original is not changed. It is pattern based and can both miss secrets and redact harmless text.

Never share a generated report or redacted file without manual review. Do not rely on FaultScribe as a secret-scanning or compliance guarantee.

## Reporting a vulnerability

Until a public repository and private reporting contact are explicitly configured, do not include sensitive details in a public issue. If you discover a possible data-exposure risk while evaluating this local source tree, keep the details local and ask the maintainer for a secure contact channel.

There is currently no claim of a response-time SLA, security certification, or external audit.
