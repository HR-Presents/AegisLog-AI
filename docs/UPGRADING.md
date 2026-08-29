# Install, upgrade, and uninstall

Use an isolated `pipx` environment for normal terminal use.

```bash
pipx install aegislog-ai
pipx upgrade aegislog-ai
pipx uninstall aegislog-ai
```

Until the first public package is published, replace the package name in the
install command with the checked-out release directory.

Configuration, declarative rules, and the SQLite investigation database remain in
`~/.config/aegislog` across upgrades and uninstall. Back up that directory before
major upgrades. Remove it manually only when you intentionally want to erase all
local AegisLog state.

V1 reads legacy unversioned configuration as schema version 0, retains recognized
fields, and writes schema version 1 on the next `aegislog config` operation. Future
unknown schemas fail closed to local-only defaults.
