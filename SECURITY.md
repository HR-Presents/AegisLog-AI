# Security Policy

AegisLog AI is defensive analysis software. Treat findings as investigation leads and validate them before changing production systems.

## Supported versions

Security fixes are prioritized for the latest published release. Users should reproduce security-sensitive issues on the newest available version whenever practical before reporting them.

## Sensitive logs and data

Logs can contain credentials, session identifiers, personal data, internal hostnames, and proprietary application data. AegisLog performs local redaction for common secret patterns, but no redactor is perfect.

Review data handling before enabling any external AI provider. Do not commit real production logs, credentials, API keys, tokens, private customer data, or `.env` files to this repository.

## Reporting a vulnerability

Please do not open a public issue containing exploitable details, credentials, sensitive logs, or proof-of-concept material that could put users at risk.

Report suspected vulnerabilities privately to the maintainers at `haziqxruveeha@gmail.com`. Include, where possible:

- the affected AegisLog version;
- operating system and installation type, such as the Windows EXE or Python package;
- a clear description of the issue and realistic impact;
- minimal reproduction steps using sanitized data;
- any relevant logs or screenshots with secrets and personal data removed.

We will review the report, confirm whether it affects a supported release, and coordinate remediation and disclosure when appropriate.

## Scope and safety

Useful reports include weaknesses in parsing, redaction, local data handling, configuration security, packaging, dependency exposure, unsafe command execution, privilege handling, and unintended external data transfer.

AegisLog is designed to remain defensive, local-first, and read-only. Reports showing unexpected system modification, automatic privilege escalation, or transmission of data without explicit configuration are especially important.
