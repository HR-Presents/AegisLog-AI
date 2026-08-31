# Contributing to AegisLog AI

Use Python 3.10+ and keep changes defensive, testable, and local-first.

## Development workflow

1. Create a focused branch from `main`.
2. Keep each pull request limited to one clear improvement or fix.
3. Add or update tests when behavior changes.
4. Run the relevant validation before requesting merge.
5. Open a pull request with a short summary, verification notes, and any user-facing impact.
6. Merge only after the change is ready and the repository checks are satisfied.

For Python changes, run the relevant checks where applicable:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
pytest
ruff check .
bandit -q -r src
```

New detections should include tests and should avoid overstating certainty. Prefer evidence-backed labels such as "possible" or "suspicious" when a pattern is not conclusive. Never add real credentials or production logs to fixtures.

## Collaboration and co-authorship

When two or more people genuinely work on the same change, record that collaboration in the commit history. GitHub-compatible co-authorship trailers may be added to the commit message using the contributor's GitHub-linked email.

Example:

```text
feat: improve defensive log analysis

Co-authored-by: Contributor Name <github-linked-email@example.com>
```

Use co-authorship only when the named contributor materially participated in the work.

## Security expectations

Contributions should preserve AegisLog's defensive security model. Avoid automatic remediation, destructive system changes, privilege escalation, exploitation behavior, or unsafe handling of untrusted log content. New functionality should remain understandable from the terminal, fail safely, and keep external AI services optional.

## Pull request notes

A useful pull request description should explain what changed, why it is needed, how it was verified, and whether it changes the customer-facing terminal experience, packaging, release behavior, or security assumptions.
