"""
SATARK v2.0
AI Driver Monitoring Engine

Features:
- USB Camera
- Face Detection
- Eye Detection
- Drowsiness Detection
- Head-Down Detection
- Arduino UNO Q Head LED Control
- Live Web Camera Stream
"""

import cv2
import time
import threading

from config import (
    CAMERA_INDEX,
    FRAME_WIDTH,
    FRAME_HEIGHT,
    FPS,
    FACE_SCALE_FACTOR,
    FACE_MIN_NEIGHBORS,
    EYE_SCALE_FACTOR,
    EYE_MIN_NEIGHBORS,
    DROWSY_TIME,
    HEAD_DOWN_TIME,
    FACE_CASCADE,
    EYE_CASCADE
)

from alerts import alerts
from sensors import sensors


class AIEngine:

    def __init__(self):

        print(
            "[INFO] Starting SATARK AI Engine..."
        )


        # =========================
        # CAMERA
        # =========================

        self.cap = cv2.VideoCapture(
            CAMERA_INDEX,
            cv2.CAP_V4L2
        )

        self.cap.set(
            cv2.CAP_PROP_FRAME_WIDTH,
            FRAME_WIDTH
        )

        self.cap.set(
            cv2.CAP_PROP_FRAME_HEIGHT,
            FRAME_HEIGHT
        )

        self.cap.set(
            cv2.CAP_PROP_FPS,
            FPS
        )


        if not self.cap.isOpened():

            raise RuntimeError(
                f"Camera {CAMERA_INDEX} "
                "could not be opened"
            )


        print(
            f"[INFO] Camera {CAMERA_INDEX} opened"
        )


        # =========================
        # HAAR CASCADES
        # =========================

        self.face_cascade = (
            cv2.CascadeClassifier(
                FACE_CASCADE
            )
        )

        self.eye_cascade = (
            cv2.CascadeClassifier(
                EYE_CASCADE
            )
        )


        if self.face_cascade.empty():

            raise RuntimeError(
                "Face cascade could not be loaded"
            )


        if self.eye_cascade.empty():

            raise RuntimeError(
                "Eye cascade could not be loaded"
            )


        print(
            "[INFO] Face/Eye detectors ready"
        )


        # =========================
        # DRIVER STATE
        # =========================

        self.driver_present = False

        self.eyes_detected = False

        self.drowsy = False

        self.head_down = False

        self.status = "INITIALIZING"


        # =========================
        # TIMERS
        # =========================

        self.eye_closed_start = None

        self.head_down_start = None


        # =========================
        # LATEST FRAME
        # =========================

        self.frame = None


        # =========================
        # THREAD SAFETY
        # =========================

        self.lock = threading.Lock()


        # =========================
        # FPS
        # =========================

        self.current_fps = 0

        self.last_frame_time = (
            time.time()
        )


        print(
            "[INFO] AI Engine Ready"
        )


    # ==========================================
    # PROCESS CAMERA FRAME
    # ==========================================

    def process_frame(self):

        ret, frame = self.cap.read()


        if not ret:

            self.status = "CAMERA ERROR"

            return None


        # =========================
        # MIRROR IMAGE
        # =========================

        frame = cv2.flip(
            frame,
            1
        )


        # =========================
        # GRAYSCALE
        # =========================

        gray = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2GRAY
        )

        gray = cv2.equalizeHist(
            gray
        )


        # ======================================
        # FACE DETECTION
        # ======================================

        faces = (
            self.face_cascade
            .detectMultiScale(
                gray,
                scaleFactor=FACE_SCALE_FACTOR,
                minNeighbors=FACE_MIN_NEIGHBORS,
                minSize=(60, 60)
            )
        )


        self.driver_present = (
            len(faces) > 0
        )

        self.eyes_detected = False


        now = time.time()


        # ======================================
        # DRIVER FOUND
        # ======================================

        if self.driver_present:

            # Use largest detected face

            x, y, w, h = max(
                faces,
                key=lambda f: f[2] * f[3]
            )


            # ==================================
            # FACE BOX
            # ==================================

            cv2.rectangle(
                frame,
                (x, y),
                (x + w, y + h),
                (0, 255, 0),
                2
            )


            # ==================================
            # EYE DETECTION
            # ==================================

            eye_roi_gray = gray[
                y:y + int(h * 0.65),
                x:x + w
            ]


            eyes = (
                self.eye_cascade
                .detectMultiScale(
                    eye_roi_gray,
                    scaleFactor=EYE_SCALE_FACTOR,
                    minNeighbors=EYE_MIN_NEIGHBORS,
                    minSize=(15, 15)
                )
            )


            self.eyes_detected = (
                len(eyes) > 0
            )


            for (
                ex,
                ey,
                ew,
                eh
            ) in eyes[:2]:

                cv2.rectangle(
                    frame,
                    (x + ex, y + ey),
                    (
                        x + ex + ew,
                        y + ey + eh
                    ),
                    (255, 255, 0),
                    1
                )


            # ==================================
            # DROWSINESS TIMER
            # ==================================

            if not self.eyes_detected:

                if (
                    self.eye_closed_start
                    is None
                ):

                    self.eye_closed_start = now


                elif (
                    now
                    - self.eye_closed_start
                    >= DROWSY_TIME
                ):

                    self.drowsy = True

                    self.status = (
                        "DROWSINESS DETECTED"
                    )

                    alerts.wakeup(
                        "DROWSINESS"
                    )


            else:

                self.eye_closed_start = None

                self.drowsy = False


            # ==================================
            # STABLE HEAD-DOWN CHECK
            # ==================================

            frame_h = frame.shape[0]

            face_bottom = y + h

            face_center_y = (
                y + (h // 2)
            )


            # Head down only when
            # face moves very low

            head_low = (
                face_center_y
                > frame_h * 0.78

                and

                face_bottom
                > frame_h * 0.90
            )


            # ==================================
            # HEAD DOWN
            # ==================================

            if head_low:

                if (
                    self.head_down_start
                    is None
                ):

                    self.head_down_start = now


                elapsed_head_down = (
                    now
                    - self.head_down_start
                )


                if (
                    elapsed_head_down
                    >= HEAD_DOWN_TIME
                ):

                    # IMPORTANT:
                    # Send command only once

                    if not self.head_down:

                        self.head_down = True

                        # ==========================
                        # ARDUINO UNO Q
                        # D12 RED LED BLINK
                        # ==========================

                        sensors.set_head_command(
                            True
                        )

                        self.status = (
                            "HEAD DOWN"
                        )

                        alerts.wakeup(
                            "HEAD DOWN"
                        )


            else:

                # ==================================
                # DRIVER RETURNED TO NORMAL
                # ==================================

                self.head_down_start = None


                if self.head_down:

                    self.head_down = False

                    # ==========================
                    # ARDUINO UNO Q
                    # D12 RED LED OFF
                    # ==========================

                    sensors.set_head_command(
                        False
                    )


                # Remove old HEAD DOWN status

                if (
                    self.status
                    == "HEAD DOWN"
                ):

                    self.status = (
                        "DRIVER NORMAL"
                    )


            alerts.clear()


            # ==================================
            # NORMAL CONDITION
            # ==================================

            if (
                not self.drowsy

                and

                not self.head_down
            ):

                self.status = (
                    "DRIVER NORMAL"
                )


        # ======================================
        # NO FACE / POSSIBLE HEAD DOWN
        # ======================================

        else:

            self.eye_closed_start = None

            self.drowsy = False


            if (
                self.head_down_start
                is None
            ):

                self.head_down_start = now


            elif (
                now
                - self.head_down_start
                >= HEAD_DOWN_TIME
            ):

                # IMPORTANT:
                # Send command only once

                if not self.head_down:

                    self.head_down = True

                    # ==========================
                    # ARDUINO UNO Q
                    # D12 RED LED BLINK
                    # ==========================

                    sensors.set_head_command(
                        True
                    )


                self.status = (
                    "HEAD DOWN / NO DRIVER"
                )


                alerts.wakeup(
                    "HEAD DOWN"
                )


            else:

                self.status = (
                    "SEARCHING DRIVER"
                )


        # ======================================
        # STATUS ON CAMERA
        # ======================================

        cv2.putText(
            frame,
            self.status,
            (20, 35),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 255, 255),
            2
        )


        # ======================================
        # FPS
        # ======================================

        elapsed = (
            now
            - self.last_frame_time
        )


        if elapsed > 0:

            self.current_fps = (
                1.0 / elapsed
            )


        self.last_frame_time = now


        cv2.putText(
            frame,
            f"FPS: {self.current_fps:.1f}",
            (20, 70),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (255, 255, 255),
            2
        )


        # ======================================
        # SAVE LATEST FRAME
        # ======================================

        with self.lock:

            self.frame = frame.copy()


        return frame


    # ==========================================
    # LIVE VIDEO STREAM FOR FLASK
    # ==========================================

    def generate_frames(self):

        while True:

            frame = self.process_frame()


            if frame is None:

                time.sleep(0.05)

                continue


            success, buffer = (
                cv2.imencode(
                    ".jpg",
                    frame,
                    [
                        cv2.IMWRITE_JPEG_QUALITY,
                        75
                    ]
                )
            )


            if not success:

                continue


            frame_bytes = (
                buffer.tobytes()
            )


            yield (
                b"--frame\r\n"
                b"Content-Type: "
                b"image/jpeg\r\n\r\n"
                + frame_bytes
                + b"\r\n"
            )


    # ==========================================
    # AI STATUS FOR DASHBOARD
    # ==========================================

    def get_status(self):

        eye_closed_seconds = 0

        head_down_seconds = 0


        now = time.time()


        if (
            self.eye_closed_start
            is not None
        ):

            eye_closed_seconds = (
                now
                - self.eye_closed_start
            )


        if (
            self.head_down_start
            is not None
        ):

            head_down_seconds = (
                now
                - self.head_down_start
            )


        return {

            "status":
                self.status,

            "driver_present":
                self.driver_present,

            "eyes_detected":
                self.eyes_detected,

            "drowsy":
                self.drowsy,

            "head_down":
                self.head_down,

            "eye_closed_seconds":
                round(
                    eye_closed_seconds,
                    1
                ),

            "head_down_seconds":
                round(
                    head_down_seconds,
                    1
                ),

            "fps":
                round(
                    self.current_fps,
                    1
                ),

            "camera":
                self.cap.isOpened()
        }


    # ==========================================
    # GET LATEST FRAME
    # ==========================================

    def get_frame(self):

        with self.lock:

            if self.frame is None:

                return None

            return self.frame.copy()


    # ==========================================
    # STOP / CLEANUP
    # ==========================================

    def release(self):

        print(
            "[INFO] Stopping AI Engine..."
        )


        if self.cap is not None:

            if self.cap.isOpened():

                self.cap.release()


        cv2.destroyAllWindows()


        print(
            "[INFO] Camera released"
        )


# ==============================================
# GLOBAL AI ENGINE
# ==============================================

ai = AIEngine()
