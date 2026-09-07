# Security hardening behavior

This document describes the security-relevant behavior introduced by the production-hardening work after commit `4f2eca3`.

## Authentication correlation

Authentication failures are correlated by parsed **source** address. AegisLog validates IPv4 and IPv6 with Python's `ipaddress` module and does not count every address-looking token on a line. Destination addresses and repeated copies of the same address are therefore not treated as additional failures.

Timestamped events use an event-time window. The default is 300 seconds and can be overridden through the Python analysis API with `auth_window_seconds`. Events that arrive out of order but are still inside the active window are retained. Events older than the active window are expired immediately and do not contribute to escalation.

ISO/RFC3339 timestamps remain authoritative absolute timestamps. RFC3164-style syslog timestamps such as `Sep  7 10:00:00` participate in event-time correlation only when a year is known safely: callers may supply `timestamp_year_hint`, or the analysis state may inherit a year after observing an absolute timestamp in the same analysis. AegisLog does **not** assume the current year for yearless archived logs. If no safe year context exists, the event uses the bounded missing-timestamp fallback.

When a timestamp cannot be parsed safely, AegisLog does not invent one. Those failures are correlated separately by bounded event order. Findings state that the timestamp is unavailable so evidence does not imply precision absent from the source.

A single generic authentication failure is LOW context, two to four are MEDIUM, five or more are HIGH, and twenty or more are CRITICAL within retained correlation state. A sudo-specific authentication failure is evaluated by the privilege rule before generic authentication correlation so the more specific context is preserved.

Correlation state is globally bounded. Defaults retain at most 10,000 authentication events and 2,048 authentication sources; per-source missing-timestamp buckets retain at most 20 events. Evictions are reflected by `dropped_auth_events` and `dropped_auth_sources`, and expired empty buckets are removed.

## Streaming and large files

`analyze_file()` iterates over the file instead of calling `readlines()`. `analyze_stream()` shares one correlation state across the entire stream, so authentication results are independent of chunk boundaries.

Streaming applies a default 1,000,000-byte per-line limit. Oversized lines are truncated before analysis and `StreamSummary.truncated_lines` reports those truncations. `StreamSummary.dropped_findings` and `StreamSummary.dropped_auth_events` expose losses at the streaming API boundary.

Non-authentication findings are bounded during ingest rather than accumulated without limit. The default is 5,000 retained non-auth findings; `AnalysisState.dropped_findings` records findings discarded after that cap.

## Live ingestion reliability

The live file cursor retains an incomplete final line until its newline arrives. Each poll reads at most 4,000,000 bytes. Partial lines are capped at 1,000,000 bytes; excess bytes are discarded until newline, emitted content is marked `[TRUNCATED]`, and cumulative dropped bytes are tracked.

The cursor reports source loss, recovery, replacement, and truncation state. Real-time rolling analysis is bounded by both event count and bytes, with defaults of 500 lines, 5,000,000 retained bytes, and 1,000,000 bytes per line. `RealtimeState` exposes truncation, eviction, and retained-byte telemetry.

The legacy numeric-offset API remains available, while `FileCursor` is preferred for robust live following.

## Detection severity

A standalone `/wp-login.php` request is LOW context rather than HIGH severity. Higher-confidence patterns such as traversal, exposed environment-file probes, script injection patterns, and UNION SELECT retain stronger severity. Findings remain investigative signals, not proof of compromise.

## Secret redaction and AI boundaries

Redaction is centralized in `aegislog.sanitize.redact_sensitive()` and used by the compatibility `engine.redact()` helper. Valid JSON is recursively redacted; unstructured text covers common credential fields, Authorization/Bearer/Basic headers, URL credentials, cookies, JWT-shaped values, OpenAI-style keys, GitHub-style tokens, and AWS access-key identifiers.

Prompt construction redacts untrusted log data, and provider adapters redact the complete prompt again immediately before outbound payload creation. Redaction is conservative and cannot guarantee discovery of every proprietary secret format, so operators should still minimize context sent to remote providers.

## Provider transport security

Remote providers require HTTPS. Plain HTTP is only allowed for a local provider when every resolved address is loopback. Embedded URL credentials are rejected.

DNS is resolved and validated once. Connections are attempted only against addresses from that validated set while TLS verification and SNI use the original hostname. Connection/transport failures may fail over to another already-validated address without repeating DNS resolution. HTTP responses, redirects, malformed bodies, and provider/application errors are not retried across addresses.

Redirects are rejected, response bodies are limited to 2 MB, malformed JSON is rejected, and provider-specific response shapes are validated. Proxy environment variables are intentionally ignored by this direct transport path; proxy-only deployments need an explicitly validated proxy design.

## Dependency integrity

The customer runtime is transitively SHA-256 locked in `packaging/runtime-lock.txt`. Its eight universal wheels were independently resolved on `ubuntu-24.04` and `windows-2025` with Python 3.12 and produced identical hashes. Runtime-lock audit and customer-bundle workflows enforce the file with `--require-hashes`; the bundle includes `RUNTIME_LOCK.txt` for traceability.

The artifact-producing build/release toolchain is also transitively hash-locked. Direct inputs are pinned in `packaging/build-tools.txt` (`pip`, `setuptools`, `build`, `twine`, and `pyinstaller`), with resolved platform-specific lockfiles in `packaging/build-lock-linux.txt` and `packaging/build-lock-windows.txt`. The build-lock audit independently re-resolves the direct inputs on each supported OS, compares the exact name/version/artifact-hash set against the reviewed lock, and verifies download under `--require-hashes`.

Package construction uses `python -m build --no-isolation`, preventing an isolated build environment from silently re-downloading a different `setuptools`. Windows executable workflows install the locked build toolchain plus the locked runtime dependencies, then install AegisLog with `--no-deps` before PyInstaller runs.

Release validation/test tooling installed through the project dev extra (`pytest`, `ruff`, `bandit`, `pip-audit`, and their transitives) is still not fully hash-locked. This is a remaining validation-tool supply-chain gap, distinct from the artifact-producing build toolchain.

## Detection evaluation

`tools/evaluate_detections.py evaluation/labeled_events.jsonl` runs a small labeled synthetic regression set and reports overall and per-category precision/recall at a default MEDIUM threshold. The dataset is intentionally small and synthetic; it measures regression consistency, not real-world effectiveness, deployment-specific false-positive rates, or adversarial robustness.

Representative legally obtained, sanitized telemetry with independent labeling is still required before effectiveness claims.

## Performance measurement

`benchmarks/stream_benchmark.py` records Python/platform/CPU identity, dataset size, elapsed time, lines per second, Python allocation peak, process max RSS, and truncation/drop counters. CI runs a 250,000-line benchmark on Python 3.12. Hosted-runner measurements are regression context only, not a throughput SLA.

## Migration and compatibility

Existing CLI commands and `engine.redact()` are preserved. Authentication evidence keeps its existing failure-count wording while adding account/host/time-window qualifiers where available.

`_validate_url()` retains URL-string return behavior for compatibility. `FileCursor` preserves its original first three positional fields and adds optional state with defaults.

CLI registration is isolated behind the stable `aegislog.commands` boundary. Historical version-numbered command modules remain for compatibility but no longer need to spread version-specific imports through public entrypoints.

## Known remaining limitations

Production-readiness gaps remain: pure RFC3164 logs without a safe year hint use the bounded missing-timestamp fallback; proxy-only deployments need explicit provider proxy support; release validation/test dependencies are not yet fully hash-locked; GitHub may refresh the VM image behind a fixed runner label; Windows binaries are unsigned; release provenance is configured but has not been exercised in an authorized tag/release run; historical command modules remain compatibility debt; and the synthetic detection dataset is too small to establish real-world security effectiveness.

See `docs/RELEASE_SECURITY.md` for signing, reproducibility, provenance, and release-gate details.
