# Command reference

| Command | Purpose |
| --- | --- |
| `aegislog analyze FILE` | Full local rule analysis |
| `aegislog threats FILE` | High/critical security findings |
| `aegislog anomalies FILE` | Rare event-class scoring |
| `aegislog incidents FILE` | Correlate findings into incidents |
| `aegislog ask "QUESTION" FILE` | Local investigation summary |
| `aegislog watch FILE` | Analyze newly appended events live |
| `aegislog scan DIR` | Scan candidate log files recursively |
| `aegislog report FILE` | Export findings, anomalies, incidents to JSON |
| `aegislog config` | Save non-secret provider preferences |
| `aegislog doctor` | Runtime/configuration health check |

Use `aegislog COMMAND --help` for command-specific options.
