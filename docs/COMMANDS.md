# Command reference

AegisLog exposes the same core workflows through the terminal control center and direct CLI commands. Use `aegislog COMMAND --help` (or `AegisLog.exe COMMAND --help`) for command-specific options.

| Command | Purpose |
| --- | --- |
| `aegislog start` | Open the AegisLog terminal control center |
| `aegislog analyze FILE` | Run the primary deterministic local analysis workflow |
| `aegislog dashboard FILE` | Analyze one log and render the investigation dashboard/report |
| `aegislog live FILE` | Monitor one growing log continuously |
| `aegislog live-multi FILE1 FILE2 ...` | Correlate multiple live log sources |
| `aegislog native-sources` | Show supported native OS/container sources |
| `aegislog native-analyze ...` | Analyze a bounded native telemetry snapshot |
| `aegislog native-live ...` | Monitor supported native telemetry read-only |
| `aegislog incidents FILE` | List correlated incidents |
| `aegislog investigate FILE` | Open investigation-oriented output |
| `aegislog explain FILE INCIDENT_ID` | Explain an incident using retained local evidence |
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

## Product model

AegisLog's supported command surface is deterministic, local-first, read-only, and defensive. Detection, correlation, incident explanation, MITRE context, reporting, and monitoring operate without an AI analyst or external model provider.

Mission Control intentionally does not expose AI/Ollama/OpenAI provider controls. The terminal UI is focused on evidence, incidents, telemetry, and analyst review.
