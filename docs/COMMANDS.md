# Command reference

AegisLog exposes the same core workflows through Mission Control and direct CLI commands. Use `aegislog COMMAND --help` (or `AegisLog.exe COMMAND --help`) for command-specific options.

| Command | Purpose |
| --- | --- |
| `aegislog start` | Open the Mission Control terminal |
| `aegislog analyze FILE` | Run the primary local analysis workflow |
| `aegislog dashboard FILE` | Analyze one log and render the investigation dashboard/report |
| `aegislog live FILE` | Monitor one growing log continuously |
| `aegislog live-multi FILE1 FILE2 ...` | Correlate multiple live log sources |
| `aegislog native-sources` | Show supported native OS/container sources |
| `aegislog native-analyze ...` | Analyze a bounded native telemetry snapshot |
| `aegislog native-live ...` | Monitor supported native telemetry read-only |
| `aegislog incidents FILE` | List correlated incidents |
| `aegislog investigate FILE` | Open investigation-oriented output |
| `aegislog explain FILE INCIDENT_ID` | Explain an incident using local evidence |
| `aegislog ai-analyst FILE` | Ask Local, Ollama, or opt-in OpenAI-compatible AI about deterministic findings |
| `aegislog mitre FILE` | Show evidence-supported MITRE ATT&CK context |
| `aegislog intel-entities FILE` | Show correlated entities from the current investigation |
| `aegislog save-investigation FILE` | Persist an investigation/case snapshot |
| `aegislog case-history` | Browse saved cases |
| `aegislog case-show CASE_ID` | Show one saved case |
| `aegislog stream FILE` | Run the streaming analysis surface |
| `aegislog entities FILE` | Extract observed entities |
| `aegislog behavior FILE` | Compare behavioral signals |
| `aegislog index-entities FILE` | Persist incident/entity links for later hunting |
| `aegislog entity TYPE VALUE` | Investigate historical incidents linked to one entity |
| `aegislog entity-top` | Rank historically observed entities |
| `aegislog doctor` | Check the local AegisLog environment |

## AI Analyst

Mission Control exposes the AI workflow as **`A — AI ANALYST`**.

Direct CLI examples:

```bash
# Deterministic local summary; no model or network required
aegislog ai-analyst examples/auth.log --provider local

# Local Ollama
aegislog ai-analyst examples/auth.log --provider ollama --model llama3.2

# Remote OpenAI-compatible provider; explicit per-request consent is required
AEGISLOG_API_KEY='your-key' aegislog ai-analyst examples/auth.log \
  --provider openai-compatible \
  --model YOUR_MODEL \
  --allow-remote
```

Remote AI is not part of detection. AegisLog first performs deterministic local analysis, then builds a bounded/redacted investigation prompt for the optional provider.
