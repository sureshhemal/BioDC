#!/bin/bash
# Start the BioDC web app. Run ./setup.sh first (once).
cd "$(dirname "$0")"   # the webapp/ directory
if [ ! -d ../.venv ]; then
  echo "No environment found. Run ./setup.sh first."
  exit 1
fi
# shellcheck disable=SC1091
source ../.venv/bin/activate
echo "Starting BioDC web app at http://localhost:8000  (press Ctrl+C to stop)"
exec uvicorn main:app --reload --port 8000
