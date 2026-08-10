#!/bin/bash

SATARK_DIR="/home/arduino/Satark"
VENV="/home/arduino/satark-env"

echo "=========================================="
echo "          SATARK AUTO START"
echo "=========================================="

cd "$SATARK_DIR" || exit 1
echo "[INFO] SATARK directory ready"

if [ -f "$VENV/bin/activate" ]; then
    source "$VENV/bin/activate"
    echo "[INFO] Python virtual environment activated"
else
    echo "[ERROR] Virtual environment not found"
    exit 1
fi

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
# AUDIO ENVIRONMENT
# ------------------------------------------

export SDL_AUDIODRIVER=pulse
export XDG_RUNTIME_DIR=/run/user/1000
export PULSE_SERVER=unix:/run/user/1000/pulse/native
export DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/1000/bus

echo "[INFO] Audio environment configured"

# ------------------------------------------
# WAIT FOR NETWORK
# ------------------------------------------

echo "[INFO] Waiting for network..."

while ! ip route | grep -q "default"; do
    sleep 2
done

echo "[INFO] Network is available"

# ------------------------------------------
# WAIT FOR UBON SP-150
# ------------------------------------------

echo "[INFO] Waiting for UBON SP-150..."

UBON_SINK=""

while true; do

    UBON_SINK=$(wpctl status 2>/dev/null | \
        grep -E '[0-9]+\.\s+UBON SP-150' | \
        sed -E 's/^[^0-9]*([0-9]+)\..*/\1/' | \
        head -n 1)

    if [ -n "$UBON_SINK" ]; then

        echo "[INFO] UBON SP-150 detected"
        echo "[INFO] Audio sink ID: $UBON_SINK"

        wpctl set-default "$UBON_SINK" 2>/dev/null

        sleep 2

        echo "[INFO] UBON SP-150 selected as default audio output"

        break
    fi

    echo "[INFO] UBON SP-150 not ready yet..."
    sleep 3

done

# ------------------------------------------
# WAIT FOR ARDUINO UNO Q
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
# AUDIO STABILIZATION
# ------------------------------------------

echo "[INFO] Stabilizing audio system..."
sleep 3

# ------------------------------------------
# START SATARK
# ------------------------------------------

echo "[INFO] Starting SATARK main.py..."

python3 "$SATARK_DIR/main.py" &
MAIN_PID=$!

echo "[INFO] SATARK main.py started"
echo "[INFO] Main PID: $MAIN_PID"

sleep 3

# ------------------------------------------
# START SMS WATCHER
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
echo "[INFO] Audio   : UBON SP-150"

# ------------------------------------------
# KEEP SERVICE ALIVE
# ------------------------------------------

wait "$MAIN_PID"

EXIT_CODE=$?

echo "[WARNING] SATARK main.py stopped"
echo "[WARNING] Exit code: $EXIT_CODE"

exit "$EXIT_CODE"
