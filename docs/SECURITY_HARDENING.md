# Security hardening behavior

This document describes the security-relevant behavior introduced by the production-hardening work after commit `4f2eca3`.

## Authentication correlation

Authentication failures are correlated by parsed **source** address. AegisLog validates IPv4 and IPv6 with Python's `ipaddress` module and does not count every address-looking token on a line. Destination addresses and repeated copies of the same address are therefore not treated as additional failures.

Timestamped events use an event-time window. The default is 300 seconds and can be overridden through the Python analysis API with `auth_window_seconds`. Events that arrive out of order but are still inside the active window are retained. Events older than the active window are expired immediately and do not contribute to escalation.

When a timestamp cannot be parsed, AegisLog does not invent one. Those failures are correlated separately by bounded event order. Findings state `timestamp unavailable; correlated by bounded event order` so the evidence does not imply time precision that was not present in the source data.

The correlation state is bounded by event count. Streaming analysis defaults to 10,000 retained timestamped authentication events and reports dropped correlation events when the limit is exceeded.

## Streaming and large files

`analyze_file()` now iterates over the file instead of calling `readlines()`. `analyze_stream()` shares one correlation state across the entire stream, so authentication results are independent of progress chunk boundaries.

Streaming also applies a per-line byte limit. The default is 1,000,000 bytes. Oversized lines are truncated before analysis and `StreamSummary.truncated_lines` reports how many were truncated. `StreamSummary.dropped_findings` and `StreamSummary.dropped_auth_events` expose other bounded-retention losses.

These counters are important operational signals: callers should not silently treat a run with dropped or truncated data as complete evidence.

## Detection severity

A standalone request for `/wp-login.php` is no longer treated as a HIGH-severity probing event. It produces a LOW-severity contextual finding so operators can correlate it with repetition, source diversity, HTTP status, and whether WordPress is actually deployed. Higher-confidence web patterns such as traversal, exposed environment-file probes, script injection patterns, and UNION SELECT patterns retain stronger severity.

Findings remain investigative signals, not proof of compromise.

## Secret redaction and AI boundaries

Redaction is centralized in `aegislog.sanitize.redact_sensitive()` and is used by the compatibility `engine.redact()` helper. Valid JSON is parsed recursively so nested sensitive keys can be replaced before re-serialization. Unstructured text covers common credential fields, Authorization/Bearer/Basic headers, credentials embedded in URLs, cookies, JWT-shaped values, OpenAI-style keys, GitHub-style tokens, and AWS access-key identifiers.

Prompt construction redacts untrusted log data, and provider adapters redact the complete prompt again immediately before creating an outbound payload. The second boundary check prevents a direct provider call from bypassing prompt-builder redaction.

Redaction is intentionally conservative but cannot guarantee discovery of every proprietary or arbitrary secret format. Operators should still minimize the log context sent to remote providers.

## Provider transport security

Remote AI providers require HTTPS. Plain HTTP is only allowed for a local provider when every resolved address is loopback. Provider URLs with embedded credentials are rejected.

For remote providers, DNS is resolved and validated before the request. The HTTP/TLS connection is then made to one of those validated IP addresses rather than resolving the hostname a second time. TLS verification and SNI still use the original hostname. This narrows DNS-rebinding/time-of-check-time-of-use exposure.

Redirects are rejected, response bodies are limited to 2 MB, malformed JSON is rejected, and provider-specific response shapes are validated before use.

Proxy environment variables are not used by this direct `http.client` transport path. This avoids a proxy silently changing the network destination, but it also means deployments that require an outbound HTTP proxy must currently use a supported network path outside AegisLog or extend the provider transport with an explicitly validated proxy design.

## Detection evaluation

`tools/evaluate_detections.py evaluation/labeled_events.jsonl` runs a small labeled synthetic regression set and reports overall and per-category precision/recall. The default reporting threshold is MEDIUM, so LOW contextual findings such as a single `/wp-login.php` request are not counted as positive detections.

The evaluation set is intentionally synthetic and small. It is useful for reproducibility and regression detection, but it is **not** proof of real-world effectiveness, deployment-specific false-positive rates, adversarial robustness, or production readiness. Real deployment validation should use legally obtained, appropriately sanitized, representative telemetry with independent labeling.

## Migration and compatibility

Existing CLI commands and the public `engine.redact()` helper are preserved. Existing authentication evidence wording (`N authentication failures`) is retained for compatibility while additional qualifiers document account, host, time-window, or missing-timestamp behavior.

The provider helper `_validate_url()` keeps its URL-string return behavior for compatibility even though the hardened transport uses a separate internal endpoint-validation result.

## Known remaining limitations

The live file follower still requires additional hardening for partial-line writes, explicit source-loss/recovery reporting, and byte-bounded rolling buffers. Release build dependencies are not fully locked, Windows binaries are not code-signed, and release provenance/attestation is not yet enforced. Those are release-readiness gaps, not claims of completed production readiness.
