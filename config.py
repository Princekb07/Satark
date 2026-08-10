"""
SATARK v2.0 Configuration
"""

import cv2

# =========================
# CAMERA
# =========================
CAMERA_INDEX = 0
FRAME_WIDTH = 640
FRAME_HEIGHT = 480
FPS = 30

# =========================
# AI SETTINGS
# =========================
FACE_SCALE_FACTOR = 1.1
FACE_MIN_NEIGHBORS = 5
EYE_SCALE_FACTOR = 1.1
EYE_MIN_NEIGHBORS = 5

DROWSY_TIME = 2.0
HEAD_DOWN_TIME = 5.0

# =========================
# SENSOR LIMITS
# =========================
SAFE_DISTANCE = 15      # cm
TEMP_WARNING = 40       # °C
ALCOHOL_ACTIVE = 0      # MQ digital output (LOW = detected)

# =========================
# ALERTS
# =========================
ALERT_COOLDOWN = 2

ALERT_SOUND = "sounds/alert.mp3"
WAKEUP_SOUND = "sounds/wakeup.mp3"

# =========================
# GPIO PINS
# (Change these if needed)
# =========================

# Hazard LED
HAZARD_LED = 26

# Front Ultrasonic
FRONT_TRIG = 23
FRONT_ECHO = 24

# Back Ultrasonic
BACK_TRIG = 25
BACK_ECHO = 8

# Left Ultrasonic
LEFT_TRIG = 7
LEFT_ECHO = 1

# Right Ultrasonic
RIGHT_TRIG = 12
RIGHT_ECHO = 16

# MQ Alcohol Sensor
MQ_PIN = 21

# DHT11
DHT_PIN = 20

# =========================
# CASCADE FILES
# =========================
FACE_CASCADE = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
EYE_CASCADE = cv2.data.haarcascades + "haarcascade_eye.xml"

# =========================
# DASHBOARD
# =========================
HOST = "0.0.0.0"
PORT = 5000

TITLE = "SATARK v2.0 - Driver Monitoring System"
