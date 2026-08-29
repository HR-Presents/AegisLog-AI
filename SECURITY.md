# Security Policy

AegisLog AI is defensive analysis software. Treat findings as investigation leads and validate them before changing production systems.

## Sensitive logs

Logs can contain credentials, session identifiers, personal data, internal hostnames, and proprietary application data. AegisLog performs local redaction for common secret patterns, but no redactor is perfect. Review data handling before enabling any future remote AI provider.

Do not commit real production logs, credentials, API keys, or `.env` files to this repository.

## Reporting vulnerabilities

Please report vulnerabilities privately to the maintainers rather than publishing exploitable details in a public issue before a fix is available.
