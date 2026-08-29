# Collectors

AegisLog V0.3 adds bounded read-only collectors for common Linux telemetry sources.

## journald

```bash
aegislog collect journal --lines 500 --output journal.log
aegislog collect journal --target ssh.service --lines 300 --output ssh.log
```

The collector invokes `journalctl` without mutation options and caps requests at 5,000 lines.

## Docker

```bash
aegislog collect docker --target my-container --lines 300 --output container.log
aegislog analyze container.log
```

The collector invokes `docker logs --tail` and does not start, stop, exec into, or alter containers.

Permissions are inherited from the current user. AegisLog does not attempt to elevate privileges automatically.
