# Remote AI boundary

Remote AI is implemented as an optional post-detection analysis layer. It is **not required** for AegisLog detection, correlation, incident generation, local explanations, live monitoring, or reporting.

## Default state

Remote AI is disabled by default. AegisLog will not treat the presence of an API key as permission to transmit investigation context.

Mission Control exposes remote AI through **`A — AI ANALYST`**. The operator must select `openai-compatible` and explicitly confirm the transmission before the request is enabled.

The CLI requires the explicit `--allow-remote` flag:

```bash
AEGISLOG_API_KEY='your-key' aegislog ai-analyst examples/auth.log \
  --provider openai-compatible \
  --model YOUR_MODEL \
  --allow-remote
```

## What is sent

AegisLog first runs its deterministic local engine. The AI layer then receives a bounded investigation prompt built from:

- the analyst's question;
- a limited set of local findings;
- a bounded log excerpt.

Recognized secrets are redacted before provider execution. Log-derived text is explicitly treated as untrusted telemetry rather than instructions.

## Network safeguards

Remote provider transport requires HTTPS and validates the destination before connection. Remote endpoints resolving to local/private/link-local/multicast/reserved addresses are rejected. Redirects are disabled, provider response bodies are bounded, and malformed/non-object JSON responses are rejected.

An explicit HTTPS proxy can be configured with `AEGISLOG_HTTPS_PROXY`; proxy and provider addresses are validated before the connection is attempted.

## Local alternatives

Use either of these to keep the workflow local:

```bash
aegislog ai-analyst examples/auth.log --provider local
aegislog ai-analyst examples/auth.log --provider ollama --model llama3.2
```

The `local` provider requires no model. Ollama uses a local loopback endpoint by default.

## Important limitation

Remote AI output is analyst assistance, not a new detection verdict. Provider text can be incomplete or wrong and must not override retained evidence or deterministic findings. AegisLog keeps the analyst responsible for the final conclusion.
