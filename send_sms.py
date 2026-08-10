from twilio.rest import Client
import os


# ==============================
# TWILIO SETTINGS
# ==============================

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


# ==============================
# SEND SMS
# ==============================

client = Client(
    ACCOUNT_SID,
    AUTH_TOKEN
)


try:

    message = client.messages.create(

        body="sms_appointment_reminders",

        from_=TWILIO_NUMBER,

        to=MY_NUMBER
    )

    print(
        "SMS SENT SUCCESSFULLY!"
    )

    print(
        "Message SID:",
        message.sid
    )


except Exception as e:

    print(
        "SMS SEND FAILED!"
    )

    print(e)
