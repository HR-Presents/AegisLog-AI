# Security notes for operators

AegisLog reads untrusted log content. Treat output as analysis of attacker-controlled input, not trusted instructions. The CLI removes common ANSI/control sequences before rule evidence is rendered, but operators should still avoid copying unknown log content directly into privileged shells.

AegisLog does not automatically block IPs, kill processes, change firewall rules, modify accounts, or edit service configuration. This is deliberate: remediation remains an administrator decision after evidence review.
