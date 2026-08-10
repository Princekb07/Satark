"""
SATARK v2.0
Utility Functions
"""

import time
import socket
from datetime import datetime


# ==========================================
# TIME
# ==========================================

def current_time():
    return datetime.now().strftime(
        "%H:%M:%S"
    )


def current_date():
    return datetime.now().strftime(
        "%d-%m-%Y"
    )


def timestamp():
    return time.time()


# ==========================================
# SAFE NUMBER
# ==========================================

def safe_float(value, default=0.0):

    try:
        return float(value)

    except (TypeError, ValueError):
        return default


# ==========================================
# DISTANCE DISPLAY
# ==========================================

def distance_display(value):

    if value is None:
        return "-- cm"

    try:

        value = float(value)

        if value <= 0:
            return "-- cm"

        return f"{value:.1f} cm"

    except (TypeError, ValueError):

        return "-- cm"


# ==========================================
# VALUE LIMIT
# ==========================================

def clamp(value, minimum, maximum):

    return max(
        minimum,
        min(value, maximum)
    )


# ==========================================
# BOOLEAN CONVERSION
# ==========================================

def as_bool(value):

    if isinstance(value, bool):
        return value

    if isinstance(value, str):

        return value.lower() in (
            "true",
            "1",
            "yes",
            "on"
        )

    return bool(value)


# ==========================================
# DEVICE IP ADDRESS
# ==========================================

def get_ip():

    sock = socket.socket(
        socket.AF_INET,
        socket.SOCK_DGRAM
    )

    try:

        sock.connect(
            ("8.8.8.8", 80)
        )

        ip = sock.getsockname()[0]

    except Exception:

        ip = "127.0.0.1"

    finally:

        sock.close()

    return ip


# ==========================================
# SIMPLE TIMER
# ==========================================

class Timer:

    def __init__(self):

        self.start_time = None


    def start(self):

        if self.start_time is None:
            self.start_time = time.time()


    def reset(self):

        self.start_time = None


    def elapsed(self):

        if self.start_time is None:
            return 0

        return time.time() - self.start_time


    def active(self):

        return self.start_time is not None


    def reached(self, seconds):

        return (
            self.start_time is not None
            and self.elapsed() >= seconds
        )

