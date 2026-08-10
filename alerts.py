"""
SATARK v2.0
Alert System
"""

import time
import threading
import pygame

from config import (
    ALERT_COOLDOWN,
    ALERT_SOUND,
    WAKEUP_SOUND
)


class AlertSystem:

    def __init__(self):

        self.last_alert_time = 0
        self.alert_active = False
        self.alert_type = "NONE"

        # Initialize audio
        try:
            pygame.mixer.init()
            self.audio_ready = True
            print("[INFO] Alert audio ready")

        except Exception as e:
            self.audio_ready = False
            print("[WARNING] Audio unavailable:", e)


    # ==============================
    # PLAY SOUND
    # ==============================

    def play_sound(self, sound_file):

        if not self.audio_ready:
            return

        now = time.time()

        if now - self.last_alert_time < ALERT_COOLDOWN:
            return

        try:
            pygame.mixer.music.load(sound_file)
            pygame.mixer.music.play()

            self.last_alert_time = now

        except Exception as e:
            print("[WARNING] Sound error:", e)


    # ==============================
    # GENERAL ALERT
    # ==============================

    def trigger(self, alert_type="WARNING"):

        self.alert_active = True
        self.alert_type = alert_type

        print("[ALERT]", alert_type)

        self.play_sound(ALERT_SOUND)


    # ==============================
    # DRIVER WAKE-UP ALERT
    # ==============================

    def wakeup(self, reason="DROWSINESS"):

        self.alert_active = True
        self.alert_type = reason

        print("[DRIVER ALERT]", reason)

        self.play_sound(WAKEUP_SOUND)


    # ==============================
    # CLEAR ALERT
    # ==============================

    def clear(self):

        self.alert_active = False
        self.alert_type = "NONE"


    # ==============================
    # STATUS FOR WEB DASHBOARD
    # ==============================

    def get_status(self):

        return {
            "active": self.alert_active,
            "type": self.alert_type
        }


# Global alert controller
alerts = AlertSystem()
