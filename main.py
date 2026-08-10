"""
SATARK v2.0
Driver Monitoring & Safety System
Main Application
"""

import signal
import sys

from dashboard import start, shutdown


def stop_satark(signum=None, frame=None):

    print("\n[INFO] Shutdown requested...")

    try:
        shutdown()
    except Exception as e:
        print("[WARNING] Shutdown error:", e)

    sys.exit(0)


# Ctrl+C / termination handling
signal.signal(signal.SIGINT, stop_satark)
signal.signal(signal.SIGTERM, stop_satark)


if __name__ == "__main__":

    print("")
    print("======================================")
    print("          SATARK v2.0")
    print(" Driver Monitoring & Safety System")
    print("======================================")
    print("")

    try:

        start()

    except KeyboardInterrupt:

        stop_satark()

    except Exception as e:

        print("[ERROR] SATARK failed:", e)

        try:
            shutdown()
        except Exception:
            pass

        sys.exit(1)
