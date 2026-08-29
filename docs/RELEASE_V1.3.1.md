# AegisLog AI v1.3.1

AegisLog AI v1.3.1 is a focused usability and reliability update for the terminal control center.

## What changed

- The main control center now accepts both numbered shortcuts and normal AegisLog CLI commands.
- Added Command Mode so users can run commands without opening another terminal window.
- Commands can be entered with or without the leading `AegisLog.exe` while inside the control center.
- Improved Windows drag-and-drop and quoted-path handling, including paths that contain spaces.
- Improved missing-file guidance so example paths such as `C:\logs\auth.log` are clearly identified as examples.
- Invalid paths now provide retry, built-in demo, and back options instead of leaving users stuck.
- Added clearer command discovery through `--help`, useful-command listings, and system-check visibility.
- Fixed the terminal regression test that could loop indefinitely after the new retry flow was introduced.

## Customer download

For normal Windows use, download only:

- `AegisLog.exe`
- optionally `AegisLog.exe.sha256` to verify the file

No Python installation, virtual environment, requirements file, installer, or support folder is required to run the Windows executable.

Double-click `AegisLog.exe` to open the terminal control center.

You can use the numbered menu or type commands directly, for example:

```text
native-sources
native-analyze windows --channel Security
native-live windows --channel Security --profile security
dashboard "C:\Security Logs\auth.log"
incidents "C:\Security Logs\auth.log"
mitre "C:\Security Logs\auth.log"
```

Direct command-line usage also remains available:

```text
AegisLog.exe --help
AegisLog.exe dashboard <file>
AegisLog.exe live <file> --profile security
AegisLog.exe incidents <file>
AegisLog.exe explain <file> <incident-id>
```

## Security model

AegisLog remains defensive, local-first, and read-only by design. Incident explanation is local unless the user explicitly configures an external AI provider. Log content is redacted before supported external AI usage.

The Windows executable is not digitally signed unless a future release explicitly states otherwise, so Windows SmartScreen or antivirus reputation warnings may occur.
