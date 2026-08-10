"""
SATARK v2.0
Sensor Manager
Arduino UNO Q Sensor Integration
"""

import time
import threading
import subprocess
import re

from config import SAFE_DISTANCE, TEMP_WARNING


class SensorManager:

    def __init__(self):

        # =========================
        # ULTRASONIC VALUES
        # =========================

        self.front = None
        self.back = None
        self.left = None
        self.right = None

        # =========================
        # DHT11
        # =========================

        self.temperature = None
        self.humidity = None

        # =========================
        # MQ ALCOHOL SENSOR
        # =========================

        self.mq_analog = None
        self.mq_digital = None
        self.alcohol_detected = False

        # =========================
        # HEAD STATUS
        # =========================

        self.head_down = False

        # =========================
        # HARDWARE
        # =========================

        self.hardware_connected = False

        self.running = False

        self.monitor_process = None

        self.lock = threading.Lock()

        print("[INFO] Sensor Manager Ready")
        print("[INFO] Arduino UNO Q sensor integration enabled")


    # ==========================================
    # UPDATE ULTRASONIC
    # ==========================================

    def update_ultrasonic(
        self,
        front=None,
        back=None,
        left=None,
        right=None
    ):

        with self.lock:

            if front is not None:
                self.front = front

            if back is not None:
                self.back = back

            if left is not None:
                self.left = left

            if right is not None:
                self.right = right


    # ==========================================
    # UPDATE DHT11
    # ==========================================

    def update_dht(
        self,
        temperature=None,
        humidity=None
    ):

        with self.lock:

            if temperature is not None:
                self.temperature = temperature

            if humidity is not None:
                self.humidity = humidity


    # ==========================================
    # UPDATE MQ SENSOR
    # ==========================================

    def update_mq(
        self,
        analog=None,
        digital=None
    ):

        with self.lock:

            if analog is not None:
                self.mq_analog = analog

            if digital is not None:

                self.mq_digital = digital

                # Arduino MQ digital:
                # LOW = alcohol detected
                self.alcohol_detected = (digital == 0)


    # ==========================================
    # UPDATE HEAD STATUS
    # ==========================================

    def update_head(self, state):

        with self.lock:

            self.head_down = (
                state.upper() == "DOWN"
            )


    # ==========================================
    # SEND HEAD COMMAND TO ARDUINO
    # ==========================================

    def set_head_command(self, head_down):

        command = (
            "HEAD_DOWN\n"
            if head_down
            else
            "HEAD_UP\n"
        )

        with self.lock:

            if self.monitor_process is None:

                print(
                    "[WARNING] Arduino monitor not running"
                )

                return

            try:

                self.monitor_process.stdin.write(
                    command
                )

                self.monitor_process.stdin.flush()

                print(
                    f"[UNO Q COMMAND] "
                    f"{command.strip()}"
                )

            except Exception as e:

                print(
                    "[ERROR] Failed to send "
                    f"head command: {e}"
                )


    # ==========================================
    # CHECK OBSTACLE
    # ==========================================

    def obstacle_detected(self):

        distances = [
            self.front,
            self.back,
            self.left,
            self.right
        ]

        for distance in distances:

            if distance is not None:

                if 2 < distance < SAFE_DISTANCE:

                    return True

        return False


    # ==========================================
    # TEMPERATURE WARNING
    # ==========================================

    def temperature_warning(self):

        if self.temperature is None:

            return False

        return (
            self.temperature >= TEMP_WARNING
        )


    # ==========================================
    # FORMAT DISTANCE
    # ==========================================

    def format_distance(self, value):

        if value is None:

            return "--"

        return f"{value:.1f} cm"


    # ==========================================
    # DASHBOARD DATA
    # ==========================================

    def get_data(self):

        with self.lock:

            return {

                # Ultrasonic
                "front": self.front,
                "back": self.back,
                "left": self.left,
                "right": self.right,

                "front_display":
                    self.format_distance(
                        self.front
                    ),

                "back_display":
                    self.format_distance(
                        self.back
                    ),

                "left_display":
                    self.format_distance(
                        self.left
                    ),

                "right_display":
                    self.format_distance(
                        self.right
                    ),

                # DHT11
                "temperature":
                    self.temperature,

                "humidity":
                    self.humidity,

                # MQ
                "mq_analog":
                    self.mq_analog,

                "mq_digital":
                    self.mq_digital,

                "alcohol_detected":
                    self.alcohol_detected,

                # Head
                "head_down":
                    self.head_down,

                # Safety
                "obstacle":
                    self.obstacle_detected(),

                "temperature_warning":
                    self.temperature_warning(),

                # Hardware
                "hardware_connected":
                    self.hardware_connected
            }


    # ==========================================
    # PARSE ARDUINO SERIAL DATA
    # ==========================================

    def parse_line(self, line):

        line = line.strip()

        if not line:

            return


        # ======================================
        # MQ ANALOG
        # ======================================

        match = re.search(
            r"MQ Analog\s*:\s*(-?\d+)",
            line,
            re.IGNORECASE
        )

        if match:

            self.update_mq(
                analog=int(match.group(1))
            )

            self.hardware_connected = True

            return


        # ======================================
        # MQ DIGITAL
        # ======================================

        match = re.search(
            r"MQ Digital\s*:\s*(-?\d+)",
            line,
            re.IGNORECASE
        )

        if match:

            self.update_mq(
                digital=int(match.group(1))
            )

            self.hardware_connected = True

            return


        # ======================================
        # DHT TEMPERATURE
        # ======================================

        match = re.search(
            r"DHT Temp\s*:\s*(-?\d+(?:\.\d+)?)\s*C",
            line,
            re.IGNORECASE
        )

        if match:

            self.update_dht(
                temperature=float(
                    match.group(1)
                )
            )

            self.hardware_connected = True

            return


        # ======================================
        # DHT ERROR
        # ======================================

        if re.search(
            r"DHT Temp\s*:\s*ERROR",
            line,
            re.IGNORECASE
        ):

            return


        # ======================================
        # HUMIDITY
        # ======================================

        match = re.search(
            r"Humidity\s*:\s*(-?\d+(?:\.\d+)?)\s*%",
            line,
            re.IGNORECASE
        )

        if match:

            self.update_dht(
                humidity=float(
                    match.group(1)
                )
            )

            self.hardware_connected = True

            return


        # ======================================
        # FRONT ULTRASONIC
        # ======================================

        match = re.search(
            r"FRONT\s*:\s*(-?\d+)\s*cm",
            line,
            re.IGNORECASE
        )

        if match:

            self.update_ultrasonic(
                front=int(match.group(1))
            )

            self.hardware_connected = True

            return


        # ======================================
        # BACK ULTRASONIC
        # ======================================

        match = re.search(
            r"BACK\s*:\s*(-?\d+)\s*cm",
            line,
            re.IGNORECASE
        )

        if match:

            self.update_ultrasonic(
                back=int(match.group(1))
            )

            self.hardware_connected = True

            return


        # ======================================
        # LEFT ULTRASONIC
        # ======================================

        match = re.search(
            r"LEFT\s*:\s*(-?\d+)\s*cm",
            line,
            re.IGNORECASE
        )

        if match:

            self.update_ultrasonic(
                left=int(match.group(1))
            )

            self.hardware_connected = True

            return


        # ======================================
        # RIGHT ULTRASONIC
        # ======================================

        match = re.search(
            r"RIGHT\s*:\s*(-?\d+)\s*cm",
            line,
            re.IGNORECASE
        )

        if match:

            self.update_ultrasonic(
                right=int(match.group(1))
            )

            self.hardware_connected = True

            return


        # ======================================
        # NO ECHO
        # ======================================

        match = re.search(
            r"^(FRONT|BACK|LEFT|RIGHT)"
            r"\s*:\s*NO ECHO",
            line,
            re.IGNORECASE
        )

        if match:

            sensor = (
                match.group(1).lower()
            )

            with self.lock:

                if sensor == "front":
                    self.front = None

                elif sensor == "back":
                    self.back = None

                elif sensor == "left":
                    self.left = None

                elif sensor == "right":
                    self.right = None

            return


        # ======================================
        # HEAD STATUS
        # ======================================

        match = re.search(
            r"HEAD\s*:\s*(UP|DOWN)",
            line,
            re.IGNORECASE
        )

        if match:

            self.update_head(
                match.group(1)
            )

            self.hardware_connected = True

            return


    # ==========================================
    # ARDUINO UNO Q MONITOR
    # ==========================================

    def hardware_loop(self):

        print(
            "[INFO] Starting Arduino UNO Q monitor..."
        )

        command = [
            "arduino-app-cli",
            "monitor"
        ]

        try:

            self.monitor_process = (
                subprocess.Popen(
                    command,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    stdin=subprocess.PIPE,
                    text=True,
                    bufsize=1
                )
            )

            print(
                "[INFO] Arduino UNO Q monitor started"
            )


            while self.running:

                line = (
                    self.monitor_process
                    .stdout
                    .readline()
                )

                if not line:

                    if (
                        self.monitor_process.poll()
                        is not None
                    ):

                        break

                    time.sleep(0.05)

                    continue


                line = line.rstrip()

                print(
                    "[UNO Q]",
                    line
                )

                self.parse_line(line)


        except FileNotFoundError:

            print(
                "[ERROR] arduino-app-cli not found"
            )

            self.hardware_connected = False


        except Exception as e:

            print(
                "[ERROR] Arduino monitor error:",
                e
            )

            self.hardware_connected = False


        finally:

            if self.monitor_process is not None:

                try:

                    self.monitor_process.terminate()

                except Exception:

                    pass


            self.monitor_process = None

            self.hardware_connected = False

            print(
                "[INFO] Arduino UNO Q monitor stopped"
            )


    # ==========================================
    # START SENSOR THREAD
    # ==========================================

    def start(self):

        if self.running:

            return

        self.running = True

        thread = threading.Thread(
            target=self.hardware_loop,
            daemon=True
        )

        thread.start()

        print(
            "[INFO] Sensor thread started"
        )


    # ==========================================
    # STOP SENSOR
    # ==========================================

    def stop(self):

        self.running = False

        if self.monitor_process is not None:

            try:

                self.monitor_process.terminate()

            except Exception:

                pass

        print(
            "[INFO] Sensor Manager stopped"
        )


# ==============================================
# GLOBAL SENSOR MANAGER
# ==============================================

sensors = SensorManager()
