#!/bin/bash

# ==========================================
# SATARK AUTO START
# Arduino UNO Q + AI + Sensors + SMS
# ==========================================

SATARK_DIR="/home/arduino/Satark"
VENV="/home/arduino/satark-env"

echo "=========================================="
echo "          SATARK AUTO START"
echo "=========================================="

# ------------------------------------------
# Go to SATARK directory
# ------------------------------------------

cd "$SATARK_DIR" || exit 1

echo "[INFO] SATARK directory ready"


# ------------------------------------------
# Activate Python virtual environment
# ------------------------------------------

if [ -f "$VENV/bin/activate" ]; then

    source "$VENV/bin/activate"

    echo "[INFO] Python virtual environment activated"

else

    echo "[ERROR] Virtual environment not found:"
    echo "$VENV"

    exit 1

fi


# ------------------------------------------
# Load local secrets
# ------------------------------------------

if [ -f "$SATARK_DIR/.env" ]; then

    set -a
    source "$SATARK_DIR/.env"
    set +a

    echo "[INFO] Local .env loaded"

else

    echo "[WARNING] .env not found"
    echo "[WARNING] SMS may not work"

fi


# ------------------------------------------
# Wait for network
# ------------------------------------------

echo "[INFO] Waiting for network..."

while ! ip route | grep -q "default"; do

    sleep 2

done

echo "[INFO] Network is available"


# ------------------------------------------
# Wait for Arduino UNO Q
# ------------------------------------------

echo "[INFO] Waiting for Arduino UNO Q..."

while true; do

    if arduino-cli board list 2>/dev/null | \
        grep -q "arduino:zephyr:unoq"; then

        echo "[INFO] Arduino UNO Q detected"

        break

    fi

    echo "[INFO] UNO Q not detected yet..."

    sleep 3

done


echo "[INFO] Arduino UNO Q connected"


# ------------------------------------------
# Start SATARK main system
# ------------------------------------------

echo "[INFO] Starting SATARK main.py..."

python3 "$SATARK_DIR/main.py" &

MAIN_PID=$!

echo "[INFO] SATARK main.py started"
echo "[INFO] Main PID: $MAIN_PID"


# ------------------------------------------
# Give main system time to initialize
# ------------------------------------------

sleep 3


# ------------------------------------------
# Start SMS watcher
# ------------------------------------------

echo "[INFO] Starting SMS watcher..."

python3 "$SATARK_DIR/sms_watcher.py" &

SMS_PID=$!

echo "[INFO] SMS watcher started"
echo "[INFO] SMS PID: $SMS_PID"


# ------------------------------------------
# SATARK ONLINE
# ------------------------------------------

echo "=========================================="
echo "          SATARK IS ONLINE"
echo "=========================================="

echo "[INFO] Main PID: $MAIN_PID"
echo "[INFO] SMS PID : $SMS_PID"


# ------------------------------------------
# Keep service alive
# ------------------------------------------

wait "$MAIN_PID"

EXIT_CODE=$?

echo "[WARNING] SATARK main.py stopped"
echo "[WARNING] Exit code: $EXIT_CODE"

exit "$EXIT_CODE"
