# Privacy model

AegisLog is local-first. Core parsing, rules, anomaly scoring, correlation, reports, investigation, triage, and deterministic explanations run on the user's machine and do not require a remote AI service.

Remote AI is disabled by default. An API key or a configured remote provider is not treated as permission to transmit analysis context. The operator must explicitly set `AEGISLOG_ALLOW_REMOTE_AI=1` (or another accepted true value) before the OpenAI-compatible remote adapter will run. Without that opt-in, the adapter fails closed before provider transport begins.

Local Ollama remains available without the remote-AI opt-in flag and is intended for operators who want AI-assisted analysis while keeping model execution local.

When remote AI is explicitly enabled, AegisLog minimizes and bounds provider context and redacts recognized passwords, tokens, API keys, credentials, cookies, and other supported secret patterns immediately before transport. Remote transport is restricted to validated HTTPS endpoints and uses the provider-network hardening documented in `AI_PROVIDERS.md`.

Redaction is risk reduction, not a guarantee that every sensitive value can be identified. Users remain responsible for checking whether logs contain personal, confidential, regulated, customer, or otherwise sensitive data that is not appropriate to send to a third-party provider.

Configuration files store provider/model preferences only. Secret API credentials should be supplied through environment variables or secure operating-system facilities rather than written into AegisLog configuration.

For environments requiring a strict no-egress posture, use only the local core workflow and, if desired, local Ollama. Do not enable `AEGISLOG_ALLOW_REMOTE_AI`.
