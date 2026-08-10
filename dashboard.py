"""
SATARK v2.0
Web Dashboard
"""

from flask import (
    Flask,
    render_template,
    Response,
    jsonify
)

from ai_engine import ai
from sensors import sensors
from alerts import alerts
from rpc_bridge import rpc
from config import HOST, PORT, TITLE


app = Flask(__name__)


# ==========================================
# MAIN DASHBOARD
# ==========================================

@app.route("/")
def index():

    return render_template(
        "index.html",
        title=TITLE
    )


# ==========================================
# LIVE CAMERA
# ==========================================

@app.route("/video")
def video():

    return Response(
        ai.generate_frames(),
        mimetype=(
            "multipart/x-mixed-replace;"
            " boundary=frame"
        )
    )


# ==========================================
# SYSTEM STATUS API
# ==========================================

@app.route("/status")
def status():

    ai_data = ai.get_status()
    sensor_data = sensors.get_data()
    alert_data = alerts.get_status()
    rpc_data = rpc.get_data()

    return jsonify({

        "ai": ai_data,

        "sensors": sensor_data,

        "rpc": rpc_data,

        "alert": alert_data,

        "system": {
            "name": "SATARK",
            "version": "2.0",
            "online": True
        }
    })


# ==========================================
# START DASHBOARD
# ==========================================

def start():

    print("[INFO] =================================")
    print("[INFO] SATARK v2.0")
    print("[INFO] Driver Monitoring System")
    print("[INFO] Starting Web Dashboard...")
    print("[INFO] =================================")

    # ======================================
    # START UNO Q RPC BRIDGE
    # ======================================

    rpc.start()

    # ======================================
    # START SENSOR BACKGROUND THREAD
    # ======================================

    sensors.start()

    # ======================================
    # START FLASK
    # ======================================

    app.run(
        host=HOST,
        port=PORT,
        debug=False,
        threaded=True,
        use_reloader=False
    )


# ==========================================
# CLEAN SHUTDOWN
# ==========================================

def shutdown():

    print("[INFO] Shutting down SATARK...")

    # Stop RPC bridge
    rpc.stop()

    # Stop sensors
    sensors.stop()

    # Release camera / AI
    ai.release()

    print("[INFO] SATARK stopped")
