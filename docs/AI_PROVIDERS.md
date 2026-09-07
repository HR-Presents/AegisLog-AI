# AI providers

AegisLog remains useful without an LLM. Core detection, correlation, investigation, triage, and deterministic explanations run locally and do not require a network connection.

## Local Ollama

```bash
aegislog config --provider ollama --model llama3.2
aegislog ask "What likely happened?" examples/auth.log
```

The default endpoint is `http://127.0.0.1:11434`. Override it with `AEGISLOG_OLLAMA_URL` or `--base-url` in config. Local/private addresses are permitted for the explicit Ollama adapter. Ollama does not require the remote-AI opt-in flag.

## Remote OpenAI-compatible endpoint

Remote AI is disabled by default. An API key alone is not treated as consent to transmit analysis context.

To use a remote OpenAI-compatible provider, the operator must explicitly opt in for the current environment:

```bash
export AEGISLOG_ALLOW_REMOTE_AI=1
export AEGISLOG_API_KEY='your-key'
aegislog config --provider openai-compatible --model YOUR_MODEL
aegislog ask "Explain the strongest security signals" examples/auth.log
```

On PowerShell:

```powershell
$env:AEGISLOG_ALLOW_REMOTE_AI = "1"
$env:AEGISLOG_API_KEY = "your-key"
aegislog config --provider openai-compatible --model YOUR_MODEL
aegislog ask "Explain the strongest security signals" examples/auth.log
```

`AEGISLOG_ALLOW_REMOTE_AI` accepts `1`, `true`, `yes`, or `on` (case-insensitive). If it is absent or false, the remote adapter fails closed before attempting provider transport.

`AEGISLOG_BASE_URL` can point at a public compatible `/v1` API. `OPENAI_API_KEY` is accepted as a fallback. Keys are never written by the `config` command. The remote adapter rejects endpoints resolving to loopback, link-local, private, multicast, or reserved addresses and disables HTTP redirects so the validated destination cannot silently redirect into a different network boundary. Use Ollama for local models.

## Privacy boundary

The default behavior is local-first: AegisLog does not need to send log data or analysis context to an external AI service for its core workflow.

When an operator explicitly enables remote AI, AegisLog redacts recognized passwords, tokens, API keys and secrets before provider execution, bounds the amount of telemetry, labels log data as untrusted, and tells the model to ignore instructions embedded in logs. Redaction reduces exposure risk but is not a guarantee that every possible sensitive value can be recognized. Remote-provider users are responsible for reviewing their provider's data-processing terms and ensuring the selected telemetry is permitted to leave the host or environment.

Use `aegislog ask --local ...` to force local rule-backed investigation even when a provider is configured.
