# AegisLog v1.7.0

AegisLog v1.7.0 is a product-focused release that simplifies the terminal experience and centers the project on deterministic, local-first defensive investigation.

## Highlights

- Redesigned Mission Control with a quieter, minimal navigation hierarchy.
- Reworked workspace presentation to use typography, spacing, and alignment instead of repeated bordered panels.
- Applied a restrained terminal palette with semantic color: neutral text for structure, teal for navigation, green for healthy/completed state, amber for attention, and red only for high/critical security meaning.
- Refined Health, Help, investigation triage, live views, and source-selection screens for faster scanning.
- Removed AI Analyst from Mission Control and the public CLI surface.
- Removed public Ollama/OpenAI/provider configuration from the supported product workflow.
- Kept the deterministic detection, correlation, incident, native telemetry, live monitoring, MITRE context, and reporting workflows intact.

## Product model

AegisLog v1.7.0 is terminal-first, local-first, read-only, and defensive. Findings and confidence values are investigation signals, not proof of compromise, attribution, or attacker intent.

Detection and correlation remain deterministic. This release does not claim universal real-world detection accuracy; automated and synthetic regression coverage is used to protect known behavior, while effectiveness can vary by environment and telemetry quality.

## Windows release

The GitHub release publishes:

- `AegisLog.exe`
- `AegisLog.exe.sha256`

The Windows executable is currently unsigned, so Windows SmartScreen or endpoint-security reputation warnings may appear. Verify the published SHA-256 checksum before use.

## Upgrade note

Users of v1.6.x will notice the interface immediately: the old box-heavy Mission Control and AI Analyst entry point are gone. Core defensive analysis commands remain available through the redesigned terminal interface and direct CLI commands.
