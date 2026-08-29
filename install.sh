#!/usr/bin/env sh
set -eu

PYTHON="${PYTHON:-python3}"

if ! command -v "$PYTHON" >/dev/null 2>&1; then
  echo "Python 3.10+ is required." >&2
  exit 1
fi

if command -v pipx >/dev/null 2>&1; then
  pipx install . --force
else
  "$PYTHON" -m pip install --user .
fi

echo "AegisLog AI installed. Run: aegislog doctor"
