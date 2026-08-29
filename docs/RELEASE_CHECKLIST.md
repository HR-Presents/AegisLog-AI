# Release checklist

- [x] CI tests pass locally on the available supported Python runtime
- [x] Ruff passes
- [x] Package build and metadata checks succeed
- [x] Dependency audit and static security scan reviewed
- [x] Demo commands run against sanitized fixtures
- [x] README/version/changelog updated
- [x] No credentials, private logs, or `.env` files committed
- [x] Security/privacy changes reviewed
- [ ] GitHub Actions matrix passes on Python 3.10–3.13
- [ ] Maintainer verifies `dist/SHA256SUMS` against downloaded artifacts
- [ ] Tag created only after merge approval
