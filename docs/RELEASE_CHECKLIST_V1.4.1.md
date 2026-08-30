# AegisLog AI v1.4.1 release checklist

- Merge the v1.4.1 release-preparation pull request only after CI, security, package, and Windows executable workflows pass on the exact head commit.
- Confirm `main` contains version `1.4.1` in both `pyproject.toml` and `src/aegislog/__init__.py`.
- Confirm no existing `v1.4.1` tag or release exists.
- Manually dispatch `Release v1.4.1` from the `main` branch and enter the exact confirmation value `RELEASE-v1.4.1`.
- Verify the release workflow validate, build, and publish jobs all succeed.
- Verify the release contains exactly `AegisLog.exe` and `AegisLog.exe.sha256`.
- Record the published executable SHA-256 before customer acceptance testing.
- Re-run the real-machine live-monitor acceptance test, including the default new-lines-only flow and the intentional `--from-start` flow.
