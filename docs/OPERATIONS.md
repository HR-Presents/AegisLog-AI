# Operational guidance

Run AegisLog with the least privileges required to read the intended logs. Prefer analyzing copies or explicitly permitted sources in shared environments. Generated reports should inherit the access protections of their source logs.

AegisLog intentionally skips unreadable files during recursive scans and does not attempt privilege escalation. For live monitoring, use a service account or operator context that already has appropriate read access.
