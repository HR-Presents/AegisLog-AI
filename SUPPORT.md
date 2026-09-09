# AegisLog Support

AegisLog is an open-source defensive security project. This page helps users choose the right public or private support path without exposing sensitive telemetry.

## Before opening an issue

1. Confirm the AegisLog version or build you are using.
2. Check the user guide and troubleshooting documentation.
3. Reproduce the problem with sanitized or synthetic data where possible.
4. Remove credentials, tokens, cookies, private hostnames, IP addresses that identify private infrastructure, personal data, customer data, and proprietary log content.

## Choose the right path

### Bug report

Use the GitHub **Bug report** issue template when AegisLog behaves incorrectly and the report can be shared publicly with sanitized reproduction details.

Useful reports include:

- a command that fails unexpectedly;
- incorrect parsing or presentation;
- Windows EXE problems;
- installation or startup failures;
- report-generation problems;
- reproducible terminal UX issues.

### User review

Use the GitHub **User review** form after trying AegisLog. Reviews can include an honest 1–10 rating, whether you would recommend the project, what worked well, and what should improve.

A short testimonial can be offered for the README, but it will only be featured when the reviewer explicitly grants attribution permission.

### Feature request

Use the **Feature request** template for defensive, local-first improvements. Requests that require exploitation, destructive host changes, stealth, credential theft, persistence, or automatic offensive action are outside the project scope.

### Security vulnerability

Do **not** open a public issue for vulnerabilities, sensitive proof-of-concept details, credentials, or private logs. Follow `SECURITY.md` and use the private reporting route listed there.

## Privacy boundary

AegisLog does not add product telemetry simply to identify who runs the application. Public GitHub activity such as Stars, Forks, Issues, Reviews, Pull Requests, and commits is visible because users deliberately interact with GitHub.

A Star indicates public interest or support; it is not proof that the person installed or used AegisLog. A public User Review is the preferred way for someone to identify themselves as a user and share their experience.

## Maintainer response expectations

Maintainers will prioritize reproducible bugs, security-sensitive reports, release regressions, and reports that include clear sanitized evidence. Open-source support is best-effort and does not imply a service-level agreement.

For general usage, start with:

- `docs/USER_GUIDE.md`
- `docs/TROUBLESHOOTING.md`
- `docs/COMMANDS.md`
- `docs/COMMUNITY_REVIEWS.md`
- `SECURITY.md`
