# AI providers

AegisLog remains fully useful without an LLM. Core detection, correlation, incident creation, triage, and deterministic explanations run locally and do not require a network connection.

The optional AI layer is exposed in two places:

- Mission Control: **`A — AI ANALYST`**
- CLI: `aegislog ai-analyst FILE`

The AI layer runs **after** deterministic analysis. It does not decide whether a detection exists, change findings, or modify the host.

## Local provider

`local` is the default AI Analyst mode. It uses AegisLog's rule-backed findings and deterministic recommendations only.

```bash
aegislog ai-analyst examples/auth.log --provider local
```

No model, API key, or network connection is required.

## Local Ollama

Ollama runs on the local machine and does not require the remote-AI opt-in flag.

```bash
aegislog ai-analyst examples/auth.log \
  --provider ollama \
  --model llama3.2
```

The default Ollama endpoint is `http://127.0.0.1:11434`. Override it with `AEGISLOG_OLLAMA_URL` or `--base-url`.

Plain HTTP is restricted to loopback addresses for local-provider use.

## Remote OpenAI-compatible endpoint

Remote AI is disabled by default. An API key alone is not treated as consent to transmit analysis context.

For one explicit CLI request:

```bash
AEGISLOG_API_KEY='your-key' aegislog ai-analyst examples/auth.log \
  --provider openai-compatible \
  --model YOUR_MODEL \
  --allow-remote
```

`OPENAI_API_KEY` is accepted as a fallback. `AEGISLOG_BASE_URL` can point at a compatible public `/v1` endpoint, or use `--base-url` for the current command.

Inside Mission Control, selecting `openai-compatible` triggers an explicit confirmation before any remote request is allowed. The consent flag is enabled only for that request and then restored.

Remote provider safeguards include:

- explicit opt-in before provider transport;
- HTTPS requirement for remote endpoints;
- rejection of embedded URL credentials;
- rejection of loopback/private/link-local/multicast/reserved remote destinations;
- pinned validated destination addresses;
- redirects disabled;
- bounded provider response size;
- JSON response validation;
- optional explicit HTTPS proxy support;
- recognized sensitive-value redaction before provider execution.

## Privacy boundary

The default behavior is local-first. AegisLog does not need to send log data or analysis context to an external AI service for its core workflow.

For optional AI analysis, AegisLog first runs local deterministic detection, then builds a bounded investigation context from findings and a limited log excerpt. Recognized passwords, tokens, API keys, and secrets are redacted. Log-derived content is labeled as untrusted telemetry, and the prompt tells the model not to follow instructions embedded in logs.

Redaction reduces exposure risk but cannot guarantee that every possible sensitive value will be recognized. Operators are responsible for ensuring selected telemetry is permitted to leave the host or environment and for reviewing the chosen provider's data-processing terms.

## Provider summary

| Provider | Network | Explicit remote consent | Default model |
| --- | --- | --- | --- |
| `local` | No | No | `deterministic` |
| `ollama` | Local loopback | No | `llama3.2` |
| `openai-compatible` | Remote HTTPS | Yes | `gpt-4.1-mini` |

AegisLog does not currently ship a dedicated Gemini adapter. A future provider should be added explicitly rather than being advertised before it exists.
