# AegisLog Support

AegisLog is an open-source defensive security project. This page helps you choose the right support path without exposing sensitive telemetry.

## Start here

For normal usage questions, check these first:

- [User Guide](docs/USER_GUIDE.md)
- [Command Reference](docs/COMMANDS.md)
- [Troubleshooting](docs/TROUBLESHOOTING.md)
- [FAQ](docs/FAQ.md)
- [Documentation Index](docs/README.md)

## Before opening a public issue

Please include enough information to reproduce the problem, but sanitize everything first.

Good public reports include:

- AegisLog version or commit/build information;
- operating system and environment;
- the command or workflow used;
- the observed behavior;
- the expected behavior;
- sanitized terminal output or synthetic reproduction data.

Never post credentials, tokens, cookies, customer data, private production logs, personal data, proprietary incident evidence, or identifying infrastructure details.

## Choose the right path

### Bug report

Use the GitHub **Bug report** issue template when AegisLog behaves incorrectly and the problem can be reproduced safely in public.

Examples:

- startup or installation failures;
- incorrect parsing or display;
- Windows EXE problems;
- report-generation problems;
- reproducible terminal UX issues;
- unexpected behavior in supported read-only collection workflows.

### Feature request

Use the **Feature request** template for defensive, local-first improvements.

Requests centered on exploitation, credential theft, persistence, stealth, destructive host changes, or automatic offensive action are outside the project scope.

### User review

If you have tried AegisLog, use the **User Review** form to share an honest experience publicly.

Reviews may include:

- rating and recommendation;
- version/environment;
- workflows used;
- what worked well;
- what should improve;
- an optional short testimonial.

Testimonials are only featured with explicit attribution permission. See [Community Reviews](docs/COMMUNITY_REVIEWS.md).

### Security vulnerability

Do **not** open a public issue for a vulnerability, sensitive proof-of-concept details, secrets, or private logs.

Follow [`SECURITY.md`](SECURITY.md) and use the private reporting path described there.

## Privacy boundary

AegisLog does not add product telemetry simply to identify who runs the application. Public GitHub activity is visible because users deliberately interact with GitHub.

Stars, forks, issues, pull requests, and reviews are community signals. A star shows public interest or support; it is not proof that someone installed or used AegisLog.

## Maintainer response expectations

Open-source support is best-effort and does not imply a service-level agreement. Reproducible bugs, security-sensitive reports, release regressions, and reports with clear sanitized evidence are generally the easiest to investigate effectively.

For private security issues, use `SECURITY.md`. For everything else, keep reports focused, reproducible, and safe to share publicly.
