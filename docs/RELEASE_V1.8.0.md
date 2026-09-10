# AegisLog v1.8.0

AegisLog v1.8.0 is a visual-identity and presentation release for the deterministic, local-first defensive log investigation workflow.

## Highlights

- New AegisLog visual identity with an angular shield and telemetry-pulse mark.
- Stronger terminal hierarchy with larger AEGISLOG branding, clearer workspace headings, and more prominent primary actions.
- Professional midnight / graphite / steel palette with one controlled Aegis-blue accent.
- Semantic green, amber, and red are reserved for actual state and severity instead of decorative use.
- HTML investigation reports now use the same brand system as the terminal and README, including the embedded AegisLog mark, dark surfaces, stronger headings, and clearer evidence presentation.
- README presentation has been rebuilt around the same identity and feature hierarchy.
- AI Analyst remains removed from the public product surface; AegisLog continues to rely on deterministic detection, correlation, and read-only investigation workflows.

## Product behavior

AegisLog remains terminal-first, local-first, read-only by default, and deterministic for detection and correlation. The visual redesign does not change the underlying detection semantics.

## Validation

The release candidate is gated by CI, security checks, dependency lock audits, package builds, synthetic regression evaluation, and a Windows single-executable smoke test. The release workflow explicitly checks the packaged executable version and fails if removed AI/Ollama/OpenAI surfaces reappear in public help or Mission Control.

## Windows

The GitHub release publishes an unsigned `AegisLog.exe` and matching SHA-256 checksum file. Windows SmartScreen may warn because the executable is not code-signed.

## Detection evidence note

Automated and synthetic regression tests validate expected behavior for the maintained fixtures. Real-world detection effectiveness varies by environment and has not been independently benchmarked.
