# Examples

## Authentication investigation

```bash
aegislog analyze examples/auth.log
aegislog threats examples/auth.log
aegislog incidents examples/auth.log
aegislog ask "Could this be brute-force activity?" examples/auth.log
```

## Web-server investigation

```bash
aegislog analyze examples/access.log
aegislog anomalies examples/access.log
```

## Journald JSON export

A journald export can be supplied as JSON lines. For example, a local administrator may export permitted records to a file and analyze that file with:

```bash
aegislog analyze journal.jsonl
```

## Recursive scan

```bash
aegislog scan /var/log
```

Permission errors are skipped. AegisLog does not attempt to elevate its own privileges.
