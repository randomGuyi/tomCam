
#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="$HOME/tomCam"
PYTHON="$PROJECT_DIR/.venv/bin/python"

if [[ $# -lt 1 ]]; then
    echo "Usage: $0 script.py [arguments...]"
    exit 2
fi

SCRIPT="$PROJECT_DIR/$1"
shift

if [[ ! -f "$SCRIPT" ]]; then
    echo "ERROR: Script not found: $SCRIPT"
    exit 1
fi

if [[ ! -x "$PYTHON" ]]; then
    echo "ERROR: Virtual environment Python not found."
    exit 1
fi

exec "$PYTHON" "$SCRIPT" "$@"

