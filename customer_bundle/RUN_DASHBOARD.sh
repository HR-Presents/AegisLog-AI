#!/usr/bin/env sh
set -eu
cd "$(dirname "$0")"

if [ ! -x ".aegislog-venv/bin/aegislog" ]; then
  echo "AegisLog AI is not installed. Run ./INSTALL_LINUX_MACOS.sh first." >&2
  exit 1
fi

printf "Enter full path to the log file: "
IFS= read -r LOGFILE
[ -n "$LOGFILE" ] || exit 1
"$(pwd)/.aegislog-venv/bin/aegislog" dashboard "$LOGFILE"
