#!/bin/bash
# One-command setup for the BioDC web app.
# Creates a Python virtual environment and installs all dependencies.
set -e
cd "$(dirname "$0")"   # the webapp/ directory

echo "==> Looking for a suitable Python (3.10-3.13)..."
PY=""
for c in python3.13 python3.12 python3.11 python3.10; do
  if command -v "$c" >/dev/null 2>&1; then PY="$c"; break; fi
done
if [ -z "$PY" ]; then
  echo "ERROR: Need Python 3.10-3.13 (3.14 is too new for the science libraries)."
  echo "Install one, e.g.:  brew install python@3.11"
  exit 1
fi
echo "    Using: $($PY --version)"

echo "==> Creating virtual environment (.venv)..."
$PY -m venv ../.venv
# shellcheck disable=SC1091
source ../.venv/bin/activate

echo "==> Installing dependencies..."
pip install --quiet --upgrade pip
pip install --quiet -r requirements.txt

echo ""
echo "Setup complete. Start the app with:"
echo "    ./run.sh"
echo "Then open http://localhost:8000 in your browser."
