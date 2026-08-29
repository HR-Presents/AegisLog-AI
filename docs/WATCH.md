# Live watch

`aegislog watch FILE` opens an existing readable file, seeks to its current end, and evaluates lines appended afterward. Stop it with Ctrl+C.

It does not currently handle file rotation, truncation, journald cursors, or multiple files in one process. Those behaviors belong in a later collector/daemon layer. The simple file-tail design keeps V0.2 easy to demonstrate and audit.
