#!/usr/bin/env sh
set -eu

cd "$(dirname "$0")"
PYTHON="${PYTHON:-python3}"
VENV=".aegislog-venv"

if ! command -v "$PYTHON" >/dev/null 2>&1; then
  echo "Python 3.10+ is required." >&2
  exit 1
fi

if [ ! -d "$VENV" ]; then
  "$PYTHON" -m venv "$VENV"
fi

"$VENV/bin/python" -m pip install --upgrade pip
"$VENV/bin/python" -m pip install .

cat > aegislog <<'EOF'
#!/usr/bin/env sh
set -eu
BASE_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
exec "$BASE_DIR/.aegislog-venv/bin/python" -m aegislog "$@"
EOF
chmod +x aegislog

cat > OPEN_AEGISLOG_TERMINAL.sh <<'EOF'
#!/usr/bin/env sh
set -eu
BASE_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
cd "$BASE_DIR"
echo "AegisLog AI terminal is ready."
echo ""
echo "Examples:"
echo "  ./aegislog analyze /var/log/auth.log"
echo "  ./aegislog dashboard /var/log/auth.log"
echo "  ./aegislog doctor"
exec "${SHELL:-/bin/sh}"
EOF
chmod +x OPEN_AEGISLOG_TERMINAL.sh

echo "AegisLog AI installed successfully."
echo "Run: ./aegislog --version"
echo "Or launch: ./OPEN_AEGISLOG_TERMINAL.sh"
