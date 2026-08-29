#!/usr/bin/env sh
set -eu
cd "$(dirname "$0")"

PYTHON="${PYTHON:-python3}"
if ! command -v "$PYTHON" >/dev/null 2>&1; then
  echo "ERROR: Python 3.10 or newer is required." >&2
  exit 1
fi

if [ ! -x ".aegislog-venv/bin/python" ]; then
  echo "Creating private AegisLog environment..."
  "$PYTHON" -m venv .aegislog-venv
fi

VPY="$(pwd)/.aegislog-venv/bin/python"
echo "Installing AegisLog AI and bundled dependencies offline..."
"$VPY" -m pip install --disable-pip-version-check --no-index --find-links "$(pwd)/vendor" "$(pwd)"/package/aegislog_ai-*.whl
"$VPY" -m aegislog --version

echo
echo "Installation complete."
echo "Run ./OPEN_AEGISLOG_TERMINAL.sh to start a ready AegisLog shell."
