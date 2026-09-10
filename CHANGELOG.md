# Changelog

## Unreleased

- No unreleased changes yet.

## 2.1.2 - 2026-09-10

- Evolved the existing terminal interface into a more polished security command center without replacing AegisLog architecture or commands.
- Adopted the Shield A terminal identity while preserving the established AegisLog signature and Windows-safe ASCII/cp1252 rendering.
- Upgraded Analyze Log with compact real-data metrics, severity/category distributions, timestamp-aware activity and investigation timelines, stronger Analyst Focus, improved incident/finding presentation, and raw evidence views.
- Improved Live Monitor and Multi-Source with real state-backed metrics, distributions, trends, source activity, alert feeds, and status presentation.
- Reworked Health and Help into consistent command-center panels and strengthened responsive behavior across narrow, normal, and wide terminals.
- Added regression coverage for command-center rendering, data-aware visualization, terminal-width behavior, Windows encoding safety, and executable smoke validation.
- Preserved detection, parsing, streaming, authentication, incident-correlation, evidence, and local-first/read-only security semantics; no mock security results were introduced.

## 2.1.1 - 2026-09-10

- Reworked Mission Control based on the actual Windows Terminal render rather than synthetic layout assumptions.
- Replaced the spreadsheet-style dashboard composition with dedicated INVESTIGATE and MONITOR work areas and a compact SYSTEM action row.
- Bounded the home-screen composition on ultra-wide terminals so the interface no longer stretches awkwardly or leaves wrapped descriptions beside large unused space.
- Preserved AegisLog public identity, ASCII/cp1252 compatibility, narrow-terminal fallback, deterministic behavior, and the local-first/read-only security model.
- Added regression coverage for wide Windows-terminal rendering, bounded line width, action visibility, prompt/footer behavior, and ASCII-safe output.
- No detection, parsing, correlation, streaming, authentication, or security semantics changed in this patch.

## 2.1.0 - 2026-09-10

- Added deterministic fuzz-style reliability regressions for malformed input, randomized streaming chunk boundaries, authentication event reordering, and bounded authentication-source floods.
- Strengthened the external detection-evidence model with schema v2, including explicit source types, collection period, sampling method, known exclusions, class balance, expected-category counts, per-category metrics, and confidence intervals.
- Expanded the maintained representative synthetic benchmark corpus beyond the core regression fixture with additional benign controls, near-miss cases, authentication variants, and coverage across audit, error, network, privilege, service, and web detections.
- Added release-readiness regression coverage and synchronized development-state documentation before release preparation.
- Kept synthetic benchmark claims explicitly scoped to regression consistency; no deployment-specific or real-world detection-effectiveness claim is made without independently labeled external evidence.
- Preserved detection, parsing, streaming, authentication, CLI, monitoring, and read-only security semantics while hardening reliability and evaluation evidence.

## 2.0.1 - 2026-09-10

- Aligned the public CLI, customer bundle launchers/installers, README terminal example, documentation index, project status, and roadmap with the AegisLog v2 product identity.
- Removed stale public-facing `AegisLog AI` branding from supported runtime and customer-startup surfaces while preserving historical release records unchanged.
- Updated the README Mission Control example to show v2.0.x and removed the obsolete duplicate `SELECT` prompt from the documented console flow.
- Added regression coverage to keep current public branding and release-status documentation synchronized.
- Preserved all v2.0 detection, streaming, authentication, parser, and security semantics unchanged.

## 2.0.0 - 2026-09-10

- Rebuilt Mission Control into a responsive, full-width terminal workspace with balanced investigation and monitoring panels on wide terminals and clean single-column fallbacks on narrow terminals.
- Reworked startup branding, hierarchy, status placement, menu grouping, rules, footer hints, and shared input/operation chrome while preserving the terminal-first product identity.
- Removed the duplicate fake `SELECT >` prompt so the shell presents one authoritative command input path.
- Added regression coverage for wide-screen utilization, narrow-screen fit, ASCII-safe Windows rendering, and prompt/footer behavior across common terminal widths.
- Preserved the v1.9 streaming, authentication, timestamp-window, parser-accuracy, and synthetic detection-regression hardening without changing detection semantics in this UI-focused release.
- Kept AI Analyst removed from the public product surface; deterministic local detection, correlation, and read-only investigation remain authoritative.

## 1.9.0 - 2026-09-10

- Made streaming authentication correlation independent of chunk boundaries by preserving one bounded correlation state across the full stream.
- Added explicit RFC3164 year-hint support to streaming analysis so full-file and streaming paths share timestamp context.
- Improved authentication parsing for RFC3164 syslog hosts and validated IPv4/IPv6 source addresses.
- Prevented destination-only addresses from being treated as authentication sources.
- Added regression coverage for out-of-order authentication events, exact correlation-window boundaries, expired events, and missing-timestamp fallback behavior.
- Expanded the maintained synthetic detection corpus from 12 to 18 labeled cases, including IPv6, structured-source, destination-only, distinct-source, and out-of-order authentication scenarios.
- Enforced zero false positives and zero false negatives on the maintained synthetic regression corpus while preserving explicit limitations about real-world effectiveness.
- Preserved the responsive, Windows-console-safe terminal identity from v1.8.0.
- Kept AI Analyst removed from the public product surface; deterministic local detection and read-only investigation remain authoritative.

## 1.6.0 - 2026-09-02

- Added analyst triage summaries to investigation workflows using existing severity and confidence signals, with explicit non-attribution guidance.
- Improved native telemetry diagnostics for Windows Event Logs, journald, and Docker by distinguishing unsupported and temporarily unavailable sources and adding read-only troubleshooting guidance.
- Hardened single-file and multi-source live monitoring for temporary source loss and recovery while preserving the active dashboard and safe cursor behavior.
- Bounded long-running multi-source arrival history and alert fingerprint state, including aggregation for large ingest batches and conservative oldest-state compaction/eviction.
- Added focused v1.6 regression coverage for analyst triage, native diagnostics, source recovery, 50,000-line ingest batches, bounded runtime state, and release metadata.
- Preserved the defensive, local-first, read-only security model; findings, anomalies, incident priorities, and ATT&CK mappings remain investigative signals rather than proof or attribution.
- Prepared version-locked v1.6.0 package, release-note, checksum, and immutable release workflow metadata.

## 1.5.0 - 2026-09-02

- Improved incident and investigation terminal workflows with ordered, incident-specific analyst next actions and clearer evidence-led guidance.
- Added runtime-aware command examples so standalone Windows builds show `AegisLog.exe` while source installs continue to show `aegislog`.
- Unified operator startup/status presentation across single-file, multi-source, and native live monitoring while preserving immediate initial-result rendering.
- Hardened long-running live trend state with ingest-cycle aggregation, bounded history, and count-preserving compaction under unusually high event rates.
- Added stress regressions for large batches and bounded rolling live/multi-source windows plus a dedicated live-state benchmark.
- Preserved the defensive, local-first, read-only security model; findings and ATT&CK mappings remain investigative signals rather than proof or attribution.
- Prepared version-locked v1.5.0 package, customer-bundle, release-note, checksum, and immutable release workflow metadata.

## 1.4.2 - 2026-08-30

- Fixed interactive control-center launch paths for the real-time file dashboard, multi-source live SOC, native analysis, and native real-time monitor.
- Added menu-level exception containment so launch failures are reported inside AegisLog instead of unexpectedly closing the control center.
- Added regression coverage for interactive launch defaults and crash containment.
- Retained the v1.4.1 live-monitoring improvements, Windows telemetry normalization, Security Event intelligence, incident IDs, MITRE context, watch profiles, native collectors, and local-first/read-only analysis.
- Published the Windows single-file `AegisLog.exe` with a SHA-256 checksum.

## 1.4.1 - 2026-08-30

- Clarified live-monitor startup behavior: by default AegisLog follows newly appended lines, with `--from-start` available when existing file content should also be processed.
- Reworked live-rate and activity wording to distinguish average rate, rolling activity, waiting state, and time since last activity.
- Deduplicated growing versions of the same live finding, including repeated authentication-failure scenarios.
- Improved first-run live dashboard messaging and added regression coverage based on real Windows testing.

## 1.4.0 - 2026-08-29

- Improved Windows Event Log timestamp, provider, level, and service normalization.
- Added friendly permission guidance for protected Windows Security Event Log access while keeping normal operation unprivileged.
- Improved Docker readiness checks to distinguish missing CLI, unavailable engine/access, and ready state.
- Surfaced actionable `INC-XXXXXXXX` incident IDs and aligned dashboard guidance with `incidents`, `investigate`, and `explain` workflows.
- Added defensive Windows Security Event context for selected audit events, including failed logons, privileged logons, process creation, account changes, group membership changes, lockouts, and audit-log clearing.
- Added regression coverage based on real Windows acceptance-test findings.
- Published the Windows single-file executable and checksum while preserving the local-first, read-only defensive model.

## 1.0.0 - Release candidate

- Promoted the complete terminal analysis, SOC workflow, persistent entity graph,
  streaming, behavioral correlation, collectors, reports, and optional AI stack.
- Added versioned, allowlisted, atomic configuration with private file permissions.
- Hardened collector execution with an executable allowlist and argument isolation.
- Replaced legacy incident identifiers with deterministic SHA-256 identifiers.
- Removed dynamic SQL composition and expanded static application security checks.
- Bounded remote AI response bodies and rejected non-object JSON responses.
- Escaped log-derived and database-derived terminal table values.
- Expanded CI to Python 3.10–3.13 and added Bandit, Twine, and release checksums.
- Added a conventional, script-friendly `aegislog --version` terminal option.

## 0.9.0 - Release candidate hardening

- Completed the security, configuration, migration, packaging, and terminal-safety gate.

## 0.2.0 - Unreleased

- Added generic, syslog, journald/JSON, and web access-log parsing.
- Added `watch` for live appended-log analysis.
- Added `anomalies` with local frequency-based scoring.
- Added `ask` with a local investigation summary and privacy-first provider abstraction.
- Added `incidents` to correlate findings by investigation category.
- Added non-secret local configuration.
- Extended JSON reports with anomalies and incidents.
- Added Linux/macOS and Windows installation helpers.
- Added security guidance, dependency audit workflow, demo guide, and broader tests.

## 0.1.0

- Initial installable terminal CLI.
- Deterministic defensive detection rules, redaction, scanning, threat view, and JSON reporting.
