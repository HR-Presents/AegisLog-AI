#!/usr/bin/env sh
set -eu
cd "$(dirname "$0")"

if [ ! -x ".aegislog-venv/bin/aegislog" ]; then
  echo "AegisLog is not installed in this folder." >&2
  echo "Run ./INSTALL_LINUX_MACOS.sh first." >&2
  exit 1
fi

export PATH="$(pwd)/.aegislog-venv/bin:$PATH"
printf '\033c'
echo "========================================"
echo "               AEGISLOG"
echo "      Defensive Log Investigation"
echo "========================================"
aegislog --version
echo
echo "Ready. Examples:"
echo "  aegislog dashboard /path/to/auth.log"
echo "  aegislog analyze /path/to/server.log"
echo "  aegislog doctor"
echo
exec "${SHELL:-/bin/sh}" -i
