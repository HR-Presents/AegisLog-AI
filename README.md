# AegisLog AI

**AI-ready defensive log intelligence for the terminal.**

AegisLog AI is an installable CLI for analyzing Linux, server, web, authentication, and application logs. The first engine combines deterministic security/error detection, repeated-authentication correlation, severity classification, sensitive-value redaction, readable terminal output, and JSON reporting. It works locally without sending logs to an AI provider.

> Status: early V0.1 foundation. Detection findings are investigative signals, not proof of compromise.

## Install from source

```bash
git clone https://github.com/HR-Presents/AegisLog-AI.git
cd AegisLog-AI
python -m venv .venv
# Linux/macOS: source .venv/bin/activate
# Windows: .venv\Scripts\activate
pip install -e .
```

## Quick start

```bash
aegislog doctor
aegislog analyze examples/auth.log
aegislog threats examples/auth.log
aegislog report examples/auth.log --output report.json
aegislog scan /var/log
```

## What V0.1 detects

- authentication failures and repeated-source brute-force indicators
- suspicious privilege/sudo activity
- common suspicious web-request indicators
- crashes, fatal errors, OOM and service failures
- application errors, exceptions, access denials and timeouts
- secrets such as passwords, tokens and API keys are redacted before findings are displayed/stored

## Architecture

```text
log files / system logs
        |
        v
 ingestion + normalization
        |
        v
 redaction layer
        |
        +----> deterministic security/error rules
        |                 |
        |                 v
        +----------> correlation
                          |
                          v
                 severity + findings
                          |
                  +-------+-------+
                  |               |
               terminal        JSON report
```

## Roadmap

The next milestones are structured parsers for journald/nginx/apache/docker, streaming `watch`, statistical anomaly baselines, incident timelines, configuration profiles, and an optional provider-neutral AI explanation layer. AI integrations will receive redacted/minimized context and local detection will remain usable without AI.

## Development

```bash
pip install -e '.[dev]'
pytest
ruff check .
```

## Security philosophy

AegisLog AI is defensive tooling. It is designed to identify, explain, correlate, and report suspicious or broken behavior. Recommendations should be validated by an administrator before production changes are made.

## License

MIT
