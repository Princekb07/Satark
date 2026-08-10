"""
SATARK v2.0
UNO Q RPC Bridge
"""

import threading
import time

from logger import info, warning, error


class RPCBridge:

    def __init__(self):

        self.connected = False
        self.running = False

        self.lock = threading.Lock()
        self.thread = None

        self.last_update = 0

        self.data = {
            "front": None,
            "back": None,
            "left": None,
            "right": None,

            "temperature": None,
            "humidity": None,

            "alcohol_detected": False,

            "hazard": False,
            "buzzer": False,

            "connected": False
        }

        info("RPC Bridge initialized")


    # ==========================================
    # START RPC BRIDGE
    # ==========================================

    def start(self):

        if self.running:
            return

        self.running = True

        self.thread = threading.Thread(
            target=self._worker,
            daemon=True
        )

        self.thread.start()

        info("RPC Bridge started")


    # ==========================================
    # BACKGROUND WORKER
    # ==========================================

    def _worker(self):

        while self.running:

            try:

                self._read_uno()

            except Exception as e:

                self.connected = False

                with self.lock:
                    self.data["connected"] = False

                warning(
                    f"RPC communication unavailable: {e}"
                )

            time.sleep(0.25)


    # ==========================================
    # READ UNO Q DATA
    # ==========================================

    def _read_uno(self):

        """
        Hardware RPC communication will be
        connected here.

        Until the MCU-side RPC service is ready,
        keep SATARK running safely.
        """

        self.connected = False

        with self.lock:
            self.data["connected"] = False


    # ==========================================
    # UPDATE DATA
    # ==========================================

    def update_data(self, new_data):

        if not isinstance(new_data, dict):
            return

        with self.lock:

            for key in self.data:

                if key in new_data:
                    self.data[key] = new_data[key]

            self.last_update = time.time()

            self.connected = True
            self.data["connected"] = True


    # ==========================================
    # GET RPC DATA
    # ==========================================

    def get_data(self):

        with self.lock:
            return self.data.copy()


    # ==========================================
    # HAZARD CONTROL
    # ==========================================

    def set_hazard(self, state):

        state = bool(state)

        with self.lock:
            self.data["hazard"] = state

        return state


    # ==========================================
    # BUZZER CONTROL
    # ==========================================

    def set_buzzer(self, state):

        state = bool(state)

        with self.lock:
            self.data["buzzer"] = state

        return state


    # ==========================================
    # STOP
    # ==========================================

    def stop(self):

        self.running = False

        if self.thread is not None:
            self.thread.join(timeout=1)

        self.connected = False

        with self.lock:
            self.data["connected"] = False

        info("RPC Bridge stopped")


# ==============================================
# GLOBAL RPC BRIDGE
# ==============================================

rpc = RPCBridge()
