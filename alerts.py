"""
SATARK v2.0
Alert System
"""

import os
import time

# Force pygame to use PipeWire/PulseAudio
# IMPORTANT: this must be set BEFORE importing pygame
os.environ["SDL_AUDIODRIVER"] = "pulse"

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
        self.audio_ready = False

        # Get SATARK project directory
        self.base_dir = os.path.dirname(os.path.abspath(__file__))

        # Convert sound paths to absolute paths
        self.alert_sound = self.get_sound_path(ALERT_SOUND)
        self.wakeup_sound = self.get_sound_path(WAKEUP_SOUND)

        # --------------------------------
        # INITIALIZE AUDIO
        # --------------------------------

        try:

            print("[AUDIO] Initializing audio...")
            print("[AUDIO] Backend:", os.environ.get("SDL_AUDIODRIVER"))

            pygame.mixer.pre_init(
                frequency=44100,
                size=-16,
                channels=2,
                buffer=1024
            )

            pygame.mixer.init()

            pygame.mixer.music.set_volume(1.0)

            self.audio_ready = True

            print("[AUDIO] Audio initialized successfully")
            print("[AUDIO] Alert sound:", self.alert_sound)
            print("[AUDIO] Wakeup sound:", self.wakeup_sound)

        except Exception as e:

            self.audio_ready = False

            print("[WARNING] Audio initialization failed:")
            print("[WARNING]", e)


    # ==========================================
    # SOUND PATH
    # ==========================================

    def get_sound_path(self, sound_file):

        if os.path.isabs(sound_file):
            return sound_file

        return os.path.join(self.base_dir, sound_file)


    # ==========================================
    # PLAY SOUND
    # ==========================================

    def play_sound(self, sound_file):

        if not self.audio_ready:

            print("[WARNING] Audio is not ready")
            return False

        now = time.time()

        # Prevent repeated alerts too quickly
        if now - self.last_alert_time < ALERT_COOLDOWN:

            print("[AUDIO] Alert cooldown active")
            return False

        try:

            # Make absolute path
            sound_file = self.get_sound_path(sound_file)

            # Check file exists
            if not os.path.exists(sound_file):

                print("[WARNING] Sound file not found:")
                print(sound_file)

                return False

            print("[AUDIO] Playing:", sound_file)

            # Stop previous sound
            if pygame.mixer.music.get_busy():

                pygame.mixer.music.stop()

            # Load sound
            pygame.mixer.music.load(sound_file)

            # Maximum volume
            pygame.mixer.music.set_volume(1.0)

            # Play
            pygame.mixer.music.play()

            self.last_alert_time = now

            print("[AUDIO] PLAYING")

            return True

        except Exception as e:

            print("[WARNING] Sound error:", e)

            return False


    # ==========================================
    # GENERAL ALERT
    # ==========================================

    def trigger(self, alert_type="WARNING"):

        self.alert_active = True
        self.alert_type = alert_type

        print("[ALERT]", alert_type)

        self.play_sound(self.alert_sound)


    # ==========================================
    # DRIVER WAKE-UP ALERT
    # ==========================================

    def wakeup(self, reason="DROWSINESS"):

        self.alert_active = True
        self.alert_type = reason

        print("[DRIVER ALERT]", reason)

        self.play_sound(self.wakeup_sound)


    # ==========================================
    # CLEAR ALERT
    # ==========================================

    def clear(self):

        self.alert_active = False
        self.alert_type = "NONE"

        print("[ALERT] Cleared")


    # ==========================================
    # STATUS FOR WEB DASHBOARD
    # ==========================================

    def get_status(self):

        return {
            "active": self.alert_active,
            "type": self.alert_type,
            "audio_ready": self.audio_ready
        }


# ==========================================
# GLOBAL ALERT CONTROLLER
# ==========================================

alerts = AlertSystem()
