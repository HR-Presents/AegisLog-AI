# Configuration

V0.2 stores non-secret preferences in `~/.config/aegislog/config.json`.

```bash
aegislog config --provider none --model ""
```

Current fields include `ai_provider`, `model`, `redact`, and `max_ai_events`. The CLI currently uses local investigation mode regardless of provider preference; provider execution is planned for V0.3.

Do not place API keys in this file. Future provider adapters should read credentials from environment variables or secure operating-system facilities.
