# AI providers

AegisLog remains useful without an LLM. AI is optional and is used only to explain already-collected, redacted investigation context.

## Local Ollama

```bash
aegislog config --provider ollama --model llama3.2
aegislog ask "What likely happened?" examples/auth.log
```

The default endpoint is `http://127.0.0.1:11434`. Override it with `AEGISLOG_OLLAMA_URL` or `--base-url` in config. Local/private addresses are permitted for the explicit Ollama adapter.

## OpenAI-compatible endpoint

```bash
export AEGISLOG_API_KEY='your-key'
aegislog config --provider openai-compatible --model YOUR_MODEL
aegislog ask "Explain the strongest security signals" examples/auth.log
```

`AEGISLOG_BASE_URL` can point at a public compatible `/v1` API. `OPENAI_API_KEY` is accepted as a fallback. Keys are never written by the `config` command. The remote adapter rejects endpoints resolving to loopback, link-local, private, multicast, or reserved addresses; use Ollama for local models.

## Privacy boundary

Before provider execution, AegisLog redacts recognized passwords, tokens, API keys and secrets, bounds the amount of telemetry, labels log data as untrusted, and tells the model to ignore instructions embedded in logs. Remote-provider users are still responsible for reviewing their provider's data-processing terms and ensuring logs are permitted to leave the host/environment.

Use `aegislog ask --local ...` to force local rule-backed investigation even when a provider is configured.
