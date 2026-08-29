# Troubleshooting

## `aegislog` command not found

Use `pipx ensurepath`, reopen the terminal, or run `python -m aegislog` from an environment where the package is installed.

## Permission denied while scanning `/var/log`

AegisLog skips unreadable files. Run it with only the permissions appropriate for your environment; it does not elevate itself.

## No anomalies reported

The V0.2 anomaly scorer requires enough events to identify rare event classes. A small or uniform sample may legitimately return none.

## Findings look incomplete

Rules are intentionally limited in early releases. Use sanitized reproducible samples when opening an issue for a missing detection.
