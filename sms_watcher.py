import requests
import subprocess
import time

STATUS_URL = "http://127.0.0.1:5000/status"

# Alert ke baad minimum gap
COOLDOWN = 300  # 5 minutes

last_sms_time = 0
alert_active = False

print("================================")
print(" SATARK SMS WATCHER STARTED")
print("================================")

while True:
    try:
        data = requests.get(STATUS_URL, timeout=2).json()

        ai = data.get("ai", {})

        drowsy = ai.get("drowsy", False)
        head_down = ai.get("head_down", False)
        driver_present = ai.get("driver_present", False)
        status = ai.get("status", "UNKNOWN")

        print(
            f"Driver: {driver_present} | "
            f"Status: {status} | "
            f"Drowsy: {drowsy} | "
            f"Head Down: {head_down}"
        )

        danger = drowsy or head_down

        if danger and not alert_active:

            current_time = time.time()

            if current_time - last_sms_time >= COOLDOWN:

                print("⚠ SATARK ALERT DETECTED!")
                print("Sending SMS...")

                subprocess.run(
                    [
                        "/home/arduino/satark-env/bin/python",
                        "/home/arduino/Satark/satark_sms.py"
                    ]
                )

                last_sms_time = current_time

            alert_active = True

        # Reset only when driver becomes normal
        if not danger:
            alert_active = False

    except Exception as e:
        print("Waiting for SATARK...", e)

    time.sleep(1)
