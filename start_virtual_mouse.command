#!/bin/zsh
# Double-click this file in Finder to launch the local Virtual Mouse companion.
set -e
cd "$(dirname "$0")"

if [[ ! -x ".venv/bin/python" ]]; then
  echo "First-time setup required. Run: python3 -m venv .venv && .venv/bin/python -m pip install -r requirements.txt"
  read "?Press Enter to close..."
  exit 1
fi

exec .venv/bin/python mouse_server.py
