#!/usr/bin/env sh
set -eu
cd "$(dirname "$0")"

printf '\033[2J\033[H'
printf '%s\n' '========================================'
printf '%s\n' '             AegisLog AI'
printf '%s\n' '      One-File Customer Launcher'
printf '%s\n' '========================================'
printf '\n'

PYTHON=""
for candidate in python3 python; do
  if command -v "$candidate" >/dev/null 2>&1; then
    PYTHON="$candidate"
    break
  fi
done

if [ -z "$PYTHON" ]; then
  echo "ERROR: Python 3.10 or newer is required."
  exit 1
fi

if [ ! -x ".aegislog-venv/bin/python" ]; then
  echo "First run detected. Installing AegisLog AI locally..."
  "$PYTHON" -m venv .aegislog-venv
  WHEEL=$(find package -maxdepth 1 -type f -name 'aegislog_ai-*.whl' | head -n 1)
  if [ -z "$WHEEL" ]; then
    echo "ERROR: AegisLog package wheel is missing."
    exit 1
  fi
  .aegislog-venv/bin/python -m pip install --disable-pip-version-check --no-index --find-links "$PWD/vendor" "$WHEEL"
  echo "Installation complete. Starting AegisLog in this terminal..."
fi

PATH="$PWD/.aegislog-venv/bin:$PATH"
export PATH
exec .aegislog-venv/bin/aegislog start
