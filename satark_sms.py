from twilio.rest import Client
import time
import os

# =========================
# TWILIO SETTINGS
# =========================

ACCOUNT_SID = os.getenv(
    "TWILIO_ACCOUNT_SID",
    "YOUR_TWILIO_ACCOUNT_SID"
)

AUTH_TOKEN = os.getenv(
    "TWILIO_AUTH_TOKEN",
    "YOUR_TWILIO_AUTH_TOKEN"
)

TWILIO_NUMBER = os.getenv(
    "TWILIO_NUMBER",
    "YOUR_TWILIO_NUMBER"
)

MY_NUMBER = os.getenv(
    "SATARK_TO_NUMBER",
    "YOUR_MOBILE_NUMBER"
)


# =========================
# SMS COOLDOWN
# =========================

COOLDOWN = 300  # 5 minutes

last_sms_time = 0


# =========================
# TWILIO CLIENT
# =========================

client = Client(
    ACCOUNT_SID,
    AUTH_TOKEN
)


# =========================
# SEND SATARK ALERT
# =========================

def send_satark_alert():

    global last_sms_time

    current_time = time.time()

    if current_time - last_sms_time < COOLDOWN:

        print(
            "SATARK: SMS cooldown active"
        )

        return

    try:

        message = client.messages.create(

            body="sms_appointment_reminders",

            from_=TWILIO_NUMBER,

            to=MY_NUMBER
        )

        last_sms_time = current_time

        print(
            "SATARK ALERT SMS SENT!"
        )

        print(
            "Message SID:",
            message.sid
        )

    except Exception as e:

        print(
            "SMS FAILED:"
        )

        print(e)


# =========================
# TEST
# =========================

if __name__ == "__main__":

    print(
        "SATARK SMS MODULE STARTED"
    )

    send_satark_alert()
