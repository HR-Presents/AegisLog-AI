# Security hardening behavior

This document describes the security-relevant behavior introduced by the production-hardening work after commit `4f2eca3`.

## Authentication correlation

Authentication failures are correlated by parsed **source** address. AegisLog validates IPv4 and IPv6 with Python's `ipaddress` module and does not count every address-looking token on a line. Destination addresses and repeated copies of the same address are therefore not treated as additional failures.

Timestamped events use an event-time window. The default is 300 seconds and can be overridden through the Python analysis API with `auth_window_seconds`. Events that arrive out of order but are still inside the active window are retained. Events older than the active window are expired immediately and do not contribute to escalation.

ISO/RFC3339-style timestamps remain the authoritative absolute timestamps. RFC3164-style syslog timestamps such as `Sep  7 10:00:00` are also supported when a year is known safely: callers can supply `timestamp_year_hint`, or the analysis state can inherit a year after observing an absolute timestamp in the same analysis. AegisLog intentionally does **not** assume the current year for yearless archived logs. If no safe year context exists, the event uses the bounded missing-timestamp fallback.

When a timestamp cannot be parsed safely, AegisLog does not invent one. Those failures are correlated separately by bounded event order. Findings state `timestamp unavailable; correlated by bounded event order` so the evidence does not imply time precision that was not present in the source data.

A single generic authentication failure is LOW context, two to four failures from the same source are MEDIUM, five or more are HIGH, and twenty or more are CRITICAL within the retained correlation state. A sudo-specific authentication failure is evaluated by the privilege rule before generic authentication correlation so the more specific context is preserved.

Correlation state is globally bounded. Defaults retain at most 10,000 authentication events across timestamped and missing-timestamp buckets and at most 2,048 distinct retained authentication sources. Per-source missing-timestamp buckets retain at most 20 events. When source or event limits require eviction, `dropped_auth_events` and `dropped_auth_sources` record the loss. Empty timestamped source buckets are removed as their events expire so old source keys do not accumulate indefinitely.

## Streaming and large files

`analyze_file()` iterates over the file instead of calling `readlines()`. `analyze_stream()` shares one correlation state across the entire stream, so authentication results are independent of progress chunk boundaries.

Streaming also applies a per-line byte limit. The default is 1,000,000 bytes. Oversized lines are truncated before analysis and `StreamSummary.truncated_lines` reports how many were truncated. `StreamSummary.dropped_findings` and `StreamSummary.dropped_auth_events` expose losses visible at the streaming API boundary.

Non-authentication findings are bounded during ingest rather than accumulated without limit and sliced only after analysis. The default state limit is 5,000 retained non-auth findings. `AnalysisState.dropped_findings` tracks findings discarded after that limit, and streaming includes those drops in `StreamSummary.dropped_findings`.

Callers should not silently treat a run with dropped or truncated data as complete evidence. The configured bounds make memory use deterministic with respect to retained findings, source cardinality, authentication-event count, and per-line size, but Python/container overhead and other application state still contribute to total process memory.

## Live ingestion reliability

The live file cursor retains an incomplete final line instead of emitting it as a complete event. A line is released only after a newline arrives. Each poll reads at most 4,000,000 bytes, so a large append is consumed over multiple polls rather than one unbounded `read()`.

Partial lines are capped at 1,000,000 bytes. Excess bytes are discarded until the terminating newline, the emitted line includes `[TRUNCATED]`, and the cursor records cumulative `dropped_bytes`. The cursor also records `source_missing`, `source_recovered`, `source_replaced`, or `source_truncated` reset metadata while preserving the existing `(lines, cursor)` interface.

The real-time rolling analysis window is bounded both by event count and bytes. Defaults are 500 lines and 5,000,000 retained bytes, with a 1,000,000-byte per-line limit. `RealtimeState` exposes `truncated_lines`, `dropped_window_lines`, and `rolling_bytes`, and the terminal status displays those losses.

The legacy numeric-offset `read_new_lines()` API remains available. It retries ordinary incomplete trailing data by returning an offset before the pending bytes. The richer `FileCursor` API should be preferred for robust live monitoring because it can preserve truncation and source-availability state across polls.

## Detection severity

A standalone request for `/wp-login.php` is no longer treated as a HIGH-severity probing event. It produces a LOW-severity contextual finding so operators can correlate it with repetition, source diversity, HTTP status, and whether WordPress is actually deployed. Higher-confidence web patterns such as traversal, exposed environment-file probes, script injection patterns, and UNION SELECT patterns retain stronger severity.

Findings remain investigative signals, not proof of compromise.

## Secret redaction and AI boundaries

Redaction is centralized in `aegislog.sanitize.redact_sensitive()` and is used by the compatibility `engine.redact()` helper. Valid JSON is parsed recursively so nested sensitive keys can be replaced before re-serialization. Unstructured text covers common credential fields, Authorization/Bearer/Basic headers, credentials embedded in URLs, cookies, JWT-shaped values, OpenAI-style keys, GitHub-style tokens, and AWS access-key identifiers.

Prompt construction redacts untrusted log data, and provider adapters redact the complete prompt again immediately before creating an outbound payload. The second boundary check prevents a direct provider call from bypassing prompt-builder redaction.

Redaction is intentionally conservative but cannot guarantee discovery of every proprietary or arbitrary secret format. Operators should still minimize the log context sent to remote providers.

## Provider transport security

Remote AI providers require HTTPS. Plain HTTP is only allowed for a local provider when every resolved address is loopback. Provider URLs with embedded credentials are rejected.

For remote providers, DNS is resolved and validated once before the request. Connections are attempted only against IP addresses from that exact validated set, while TLS verification and SNI continue to use the original hostname. If one validated address fails at the connection/transport layer, AegisLog can try the next validated address without performing a second DNS lookup. This preserves the DNS-rebinding/time-of-check-time-of-use defense while improving ordinary multi-address endpoint resilience.

HTTP responses, redirects, malformed response bodies, and provider/application errors are **not** retried across addresses. Once a provider responds, repeating the request could duplicate side effects or hide a real provider failure. Redirects are rejected, response bodies are limited to 2 MB, malformed JSON is rejected, and provider-specific response shapes are validated before use.

Proxy environment variables are not used by this direct `http.client` transport path. This avoids a proxy silently changing the network destination, but deployments that require an outbound HTTP proxy still need an explicitly validated proxy design or an external supported network path.

## Runtime dependency integrity

The customer bundle now uses `packaging/runtime-lock.txt`, which transitively pins the runtime wheel set and records an exact SHA-256 hash for every required wheel. The eight-wheel set was independently resolved on `ubuntu-24.04` and `windows-2025` with Python 3.12 and produced identical artifacts and hashes on both platforms.

The dedicated runtime-lock workflow and both customer-bundle build paths use `pip download --require-hashes`, so an unexpected wheel, changed hash, or changed dependency version fails the build rather than silently entering the offline vendor directory. The bundle includes a copy of the reviewed lock as `RUNTIME_LOCK.txt`, and its normal bundle checksum manifest covers the copied lock and downloaded wheels.

This closes the previously identified runtime/customer-bundle transitive dependency gap. It does **not** yet fully hash-lock transitive dependencies of the build/release toolchain itself.

## Detection evaluation

`tools/evaluate_detections.py evaluation/labeled_events.jsonl` runs a small labeled synthetic regression set and reports overall and per-category precision/recall. The default reporting threshold is MEDIUM, so LOW contextual findings such as a single `/wp-login.php` request or a single generic authentication failure are not counted as positive detections.

The evaluation set is intentionally synthetic and small. It is useful for reproducibility and regression detection, but it is **not** proof of real-world effectiveness, deployment-specific false-positive rates, adversarial robustness, or production readiness. Real deployment validation should use legally obtained, appropriately sanitized, representative telemetry with independent labeling.

## Performance measurement

`benchmarks/stream_benchmark.py` creates a documented synthetic dataset, records Python/platform/CPU information, dataset bytes, elapsed time, lines per second, Python allocation peak from `tracemalloc`, process maximum RSS, and truncation/drop counters. CI executes a 250,000-line benchmark on Python 3.12. Hosted-runner results are useful for regression context only and vary between runs; they are not a service-level throughput guarantee.

## Migration and compatibility

Existing CLI commands and the public `engine.redact()` helper are preserved. Existing authentication evidence wording (`N authentication failures`) is retained for compatibility while additional qualifiers document account, host, time-window, or missing-timestamp behavior.

The provider helper `_validate_url()` keeps its URL-string return behavior for compatibility even though the hardened transport uses a separate internal endpoint-validation result. `FileCursor` preserves its original first three positional fields and adds optional state fields with defaults.

The public CLI entrypoint registers commands through the stable `aegislog.commands` boundary. Historical release-numbered command modules remain in place for compatibility, but their imports are isolated behind that registry so future renames can be staged without continuing to spread version-specific coupling through entrypoints.

## Known remaining limitations

Production-readiness gaps remain. Pure RFC3164 logs without a safe year hint still use the explicit missing-timestamp fallback rather than inventing a year. The direct provider transport intentionally does not inherit environment proxy settings. Runtime/customer-bundle dependencies are hash-locked, but transitive **build/release toolchain** dependencies are not yet fully hash-locked. GitHub-hosted runner labels are pinned to explicit OS versions, but GitHub can still refresh the underlying image for that OS label over time. Windows binaries are not code-signed. Release provenance is configured for tagged package artifacts and the v1.6.0 executable path, but it still requires validation in an actual authorized tag/release execution. The synthetic detection dataset is too small to establish real-world false-positive rates or security effectiveness.

See `docs/RELEASE_SECURITY.md` for signing, reproducibility, provenance, and release-gate details.
