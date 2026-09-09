# AegisLog User Guide

This guide covers the current AegisLog terminal workflows on `main` and the published stable Windows release. The published stable release is **v1.6.0**; `main` may contain reviewed improvements that are newer than the latest published binary.

AegisLog is a defensive, local-first, read-only log investigation tool. Its deterministic detection, correlation, incident explanation, and reporting workflows do not require a remote AI provider.

## 1. Windows quick start

For the published Windows release:

1. Open the [v1.6.0 GitHub release](https://github.com/HR-Presents/AegisLog-AI/releases/tag/v1.6.0).
2. Download `AegisLog.exe`.
3. Optionally download `AegisLog.exe.sha256` and verify the executable.
4. Run `AegisLog.exe` to open Mission Control.

The standalone executable does not require Python or a separate support directory. Unless a release explicitly states otherwise, do not assume the executable is digitally signed. Windows SmartScreen or endpoint-security reputation warnings can occur with unsigned one-file applications.

## 2. Mission Control

Run:

```text
AegisLog.exe
```

or from a source installation:

```text
aegislog
```

Mission Control provides these primary workflows:

```text
01  ANALYZE LOG
02  LIVE MONITOR
03  MULTI-SOURCE SOC
04  NATIVE LOGS
05  NATIVE MONITOR
06  INCIDENT INTEL
A   AI ANALYST
07  DEMO
08  HEALTH
09  COMMANDS
C   COMMAND MODE
Q   EXIT
```

`A — AI ANALYST` is optional. Local deterministic analysis remains authoritative whether or not an AI provider is used.

## 3. Analyze a saved log

For normal static analysis:

```text
AegisLog.exe dashboard C:\logs\auth.log
```

From source:

```text
aegislog dashboard examples/auth.log
```

The dashboard summarizes parsed events, findings, severity, correlated incidents, anomaly context, evidence, and analyst guidance. Static dashboard analysis also generates a self-contained HTML investigation report.

If a path contains spaces, quote it:

```text
AegisLog.exe dashboard "C:\Security Logs\auth.log"
```

The lower-level analysis command is also available:

```text
AegisLog.exe analyze C:\logs\auth.log
```

## 4. Live monitoring

Monitor one growing log:

```text
AegisLog.exe live C:\logs\server.log --profile security
```

Monitor multiple growing logs together:

```text
AegisLog.exe live-multi C:\logs\auth.log C:\logs\web.log --profile authentication
```

Supported watch profiles include `security`, `authentication`, `web`, `docker`, and `operations`. Stop live views with `Ctrl+C`.

Live monitoring is read-only. AegisLog does not modify the watched source.

## 5. Native telemetry

Check available native sources:

```text
AegisLog.exe native-sources
```

Examples:

```text
AegisLog.exe native-analyze windows --channel Security
AegisLog.exe native-live windows --channel Security --profile security
AegisLog.exe native-analyze journald
AegisLog.exe native-live journald --profile operations
AegisLog.exe native-analyze docker --container api
AegisLog.exe native-live docker --container api --profile docker
```

Availability depends on the operating system, installed tools, and the current account's permission to read the requested telemetry. Do not weaken host security merely to make a collector work.

## 6. Incident investigation

List correlated incidents:

```text
AegisLog.exe incidents C:\logs\auth.log
```

Inspect an incident:

```text
AegisLog.exe investigate C:\logs\auth.log INC-XXXXXXXX
```

Explain it locally:

```text
AegisLog.exe explain C:\logs\auth.log INC-XXXXXXXX
```

`explain` is deterministic and local. It summarizes why the activity matters, retained evidence, evidence-consistent MITRE ATT&CK context, safe next investigation steps, and uncertainty. Findings and confidence values are investigative signals, not proof of compromise or attribution.

Show ATT&CK context directly:

```text
AegisLog.exe mitre C:\logs\auth.log
```

## 7. AI Analyst

AegisLog now exposes the existing provider backend through Mission Control and the CLI.

Open it from Mission Control with:

```text
A
```

or run:

```text
AegisLog.exe ai-analyst C:\logs\auth.log
```

Available provider modes are:

- `local` — no model and no network request; returns a deterministic rule-backed investigation summary;
- `ollama` — uses a local Ollama endpoint, defaulting to `http://127.0.0.1:11434`;
- `openai-compatible` — uses an explicitly enabled remote OpenAI-compatible HTTPS provider.

AI Analyst runs **after** local deterministic analysis. It does not replace detection, incident correlation, severity, or confidence logic.

### Local Ollama

Start Ollama separately, then choose `ollama` in Mission Control or run:

```text
AegisLog.exe ai-analyst C:\logs\auth.log --provider ollama --model llama3.2
```

Override the local endpoint with `AEGISLOG_OLLAMA_URL` when needed.

### Remote OpenAI-compatible provider

Remote AI is disabled by default. An API key alone is not treated as permission to send investigation context off-host.

PowerShell example:

```powershell
$env:AEGISLOG_ALLOW_REMOTE_AI = "1"
$env:AEGISLOG_API_KEY = "your-key"
AegisLog.exe ai-analyst C:\logs\auth.log --provider openai-compatible --model YOUR_MODEL
```

AegisLog uses the existing redaction and safe-prompt path before remote provider execution, bounds the context sent to the provider, and treats log content as untrusted telemetry. Redaction reduces risk but cannot guarantee recognition of every possible sensitive value. Only send telemetry you are authorized to transmit.

See [AI Providers](AI_PROVIDERS.md), [AI Safety](AI_SAFETY.md), and [Remote AI](REMOTE_AI.md).

## 8. Entity and case intelligence

Useful commands include:

```text
AegisLog.exe intel-entities C:\logs\auth.log
AegisLog.exe entities C:\logs\auth.log
AegisLog.exe index-entities C:\logs\auth.log
AegisLog.exe entity-top
AegisLog.exe save-investigation C:\logs\auth.log INC-XXXXXXXX
AegisLog.exe case-history
AegisLog.exe case-show INC-XXXXXXXX
```

Use `AegisLog.exe <command> --help` for exact arguments and options.

## 9. Large-file and behavioral analysis

Stream a large log with bounded chunks:

```text
AegisLog.exe stream C:\logs\huge-server.log --chunk-size 2000
```

Compare current telemetry with baseline logs:

```text
AegisLog.exe behavior --baseline monday.log --baseline tuesday.log --current today.log
```

## 10. Verify the Windows executable

The official release includes `AegisLog.exe.sha256`.

PowerShell:

```powershell
Get-FileHash .\AegisLog.exe -Algorithm SHA256
Get-Content .\AegisLog.exe.sha256
```

Compare the values exactly. Do not copy an old release checksum from documentation and apply it to a different release; always verify against the checksum published beside the executable you downloaded.

## 11. System health and command help

Inside Mission Control choose:

```text
08  HEALTH
09  COMMANDS
```

Or run:

```text
AegisLog.exe doctor
AegisLog.exe --help
AegisLog.exe <command> --help
```

The executable's own `--help` output is the authoritative syntax reference for that build.

## 12. Troubleshooting

### The EXE opens and closes immediately

Open Command Prompt, PowerShell, or Windows Terminal in the folder containing the executable and run:

```text
AegisLog.exe
```

### File not found

Use the full path and quote paths containing spaces.

### Windows warns about the executable

Verify the download came from the official GitHub Release and compare its SHA-256 with the published checksum. Reputation warnings can occur for unsigned applications.

### A native source is unavailable

Run:

```text
AegisLog.exe native-sources
```

Then check operating-system support and your authorization to read the requested source.

### Remote AI is blocked

This is expected unless explicit opt-in is present. See [Remote AI](REMOTE_AI.md). Core AegisLog analysis continues to work without remote AI.

## 13. Source/developer installation

Python 3.10+ is supported for source development:

```bash
git clone https://github.com/HR-Presents/AegisLog-AI.git
cd AegisLog-AI
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e '.[dev]'
aegislog doctor
pytest
ruff check .
bandit -q -r src
```

For normal Windows users, prefer the standalone GitHub Release executable.

## Security model

AegisLog is defensive, local-first, evidence-led, and read-only by design. It does not exploit hosts or automatically modify accounts, privileges, services, firewall rules, or system configuration. Log-derived content is untrusted input. AI assistance is optional and secondary to deterministic local analysis.
