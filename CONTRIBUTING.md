# Contributing to AegisLog

Thanks for helping improve AegisLog. Contributions are welcome when they keep the project **defensive, local-first, evidence-led, and testable**.

## Before you start

Please review:

- [README](README.md) — product scope and current workflows
- [Documentation](docs/README.md) — technical and operator guides
- [Security policy](SECURITY.md) — private vulnerability reporting
- [Support guide](SUPPORT.md) — public support and issue boundaries

Use Python 3.10+ for source development.

## Development workflow

1. Create a focused branch from `main`.
2. Keep each pull request limited to one clear improvement or fix.
3. Add or update tests when behavior changes.
4. Run the relevant validation locally.
5. Open a pull request with a concise summary, validation notes, and user-facing impact.
6. Merge only after repository checks are satisfied.

Typical validation:

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e '.[dev]'
pytest
ruff check .
bandit -q -r src
```

Use the exact checks relevant to your change; CI remains the final shared verification surface.

## What makes a good contribution?

Good AegisLog changes usually improve one or more of these areas:

- analyst clarity and terminal usability;
- defensive detections with evidence-backed wording;
- parser or collector correctness;
- bounded live-monitoring behavior;
- incident correlation and explanation quality;
- reporting and investigation workflow quality;
- tests, documentation, diagnostics, or portability;
- safe local-first integrations.

New detections should avoid overstating certainty. Prefer wording such as **possible**, **suspicious**, or **requires review** unless the underlying evidence genuinely supports a stronger statement.

## Security expectations

Contributions must preserve AegisLog’s defensive model.

Do not add functionality whose purpose is:

- exploitation;
- credential theft;
- persistence;
- privilege escalation;
- stealth or evasion;
- destructive host changes;
- automatic offensive action;
- silent external transmission of telemetry.

AegisLog should continue to fail safely, keep external AI optional, and treat log-derived text as untrusted input.

## Test data and privacy

Never commit:

- passwords, tokens, API keys, or cookies;
- real customer logs;
- private production hostnames;
- sensitive internal IP/addressing information;
- personal data;
- proprietary incident evidence.

Use synthetic or clearly sanitized fixtures. Documentation screenshots must follow the verified capture and sanitization requirements in [`docs/SCREENSHOT_CAPTURE.md`](docs/SCREENSHOT_CAPTURE.md).

## Pull requests

A useful pull request explains:

- **What changed**
- **Why it is needed**
- **How it was verified**
- **User-facing impact**
- **Security/privacy impact**, if any

Small, reviewable PRs are preferred over large unrelated change sets.

## Collaboration and co-authorship

When multiple people materially contribute to the same change, GitHub-compatible co-authorship trailers may be used with the contributor’s GitHub-linked email.

```text
feat: improve defensive log analysis

Co-authored-by: Contributor Name <github-linked-email@example.com>
```

Only use co-authorship when the named person genuinely participated in the work.

## Community feedback

If you used AegisLog but are not contributing code, you can still help by:

- opening a sanitized bug report;
- suggesting a defensive feature;
- improving documentation;
- submitting an honest [User Review](https://github.com/HR-Presents/AegisLog-AI/issues/new?template=user_review.yml);
- starring or forking the repository if you find it useful.

A star is a public signal of interest or support, not proof of installation or usage.

Thank you for helping keep AegisLog practical, transparent, and analyst-controlled.
