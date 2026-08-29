# Five-minute demo

Install in a virtual environment, then run:

```bash
aegislog doctor
aegislog analyze examples/auth.log
aegislog threats examples/auth.log
aegislog incidents examples/auth.log
aegislog analyze examples/access.log
aegislog ask "What should I investigate first?" examples/auth.log
aegislog report examples/auth.log --output aegislog-report.json
```

For a live demo, copy a sample file to a temporary path, start `aegislog watch <path>` in one terminal, and append new log lines from another terminal. AegisLog analyzes only newly appended events during the watch session.

The sample addresses use documentation-only IP ranges and do not identify real systems.
