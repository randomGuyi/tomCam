#!/usr/bin/env bash
set -Eeuo pipefail

PRINTER_MAC="4C:70:09:A1:29:8E"
RFCOMM_CHANNEL="1"
PORT="/dev/rfcomm0"
PROJECT_DIR="$HOME/pm290"
VENV="$PROJECT_DIR/venv"

# Require a Python script argument.
if (( $# < 1 )); then
    echo "Usage: $0 script.py [script arguments...]"
    echo "Example: $0 print_chat.py lena.png"
    exit 2
fi

SCRIPT="$1"
shift

cd "$PROJECT_DIR"

if [[ ! -f "$VENV/bin/activate" ]]; then
    echo "ERROR: Python virtual environment not found: $VENV"
    exit 1
fi

if [[ ! -f "$SCRIPT" ]]; then
    echo "ERROR: Python script not found: $PROJECT_DIR/$SCRIPT"
    exit 1
fi

# Check that the RFCOMM connection tool is installed.
if ! command -v rfcomm >/dev/null 2>&1; then
    echo "ERROR: rfcomm not found. Install BlueZ tools:"
    echo "  sudo apt install bluez"
    exit 1
fi

# Avoid competing with a previous connection.
if [[ -e "$PORT" ]]; then
    echo "NOTE: $PORT already exists."
    echo "Check for an existing connection before proceeding:"
    echo "  rfcomm"
    echo "  sudo rfcomm release 0"
    echo "If another rfcomm connect process is active, stop it first."
    exit 1
fi

# Activate the project's Python environment.
source "$VENV/bin/activate"

echo "Project: $PROJECT_DIR"
echo "Python:  $(command -v python)"
echo "Printer: $PRINTER_MAC"
echo "Port:    $PORT"
echo
echo "Connecting to printer..."

# Keep the RFCOMM process alive while the Python script runs.
sudo rfcomm connect 0 "$PRINTER_MAC" "$RFCOMM_CHANNEL" &
RFCOMM_PID=$!

cleanup() {
    echo
    echo "Closing RFCOMM connection..."
    sudo kill "$RFCOMM_PID" 2>/dev/null || true
    wait "$RFCOMM_PID" 2>/dev/null || true
    sudo rfcomm release 0 2>/dev/null || true
}
trap cleanup EXIT INT TERM

# Wait up to 15 seconds for the device and connection to appear.
connected=0
for _ in {1..30}; do
    if [[ -e "$PORT" ]] && kill -0 "$RFCOMM_PID" 2>/dev/null; then
        # A device node alone does not prove the link is ready.
        sleep 0.5
        if kill -0 "$RFCOMM_PID" 2>/dev/null; then
            connected=1
            break
        fi
    fi
    sleep 0.5
done

if (( ! connected )); then
    echo "ERROR: RFCOMM connection did not become ready."
    exit 1
fi

echo "RFCOMM process is running."
echo "Starting: python $SCRIPT $*"
echo

python "$SCRIPT" "$@"


