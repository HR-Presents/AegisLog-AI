#!/usr/bin/env sh
set -eu
cd "$(dirname "$0")"

echo "This removes only the private AegisLog environment in this customer folder."
printf "Type YES to continue: "
IFS= read -r CONFIRM
[ "$CONFIRM" = "YES" ] || exit 1
rm -rf .aegislog-venv
echo "AegisLog AI local environment removed."
