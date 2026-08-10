"""
SATARK v2.0
Central Logging System
"""

import logging
import os
from datetime import datetime


LOG_DIR = os.path.expanduser("~/Satark/logs")

os.makedirs(
    LOG_DIR,
    exist_ok=True
)


LOG_FILE = os.path.join(
    LOG_DIR,
    "satark.log"
)


logger = logging.getLogger(
    "SATARK"
)

logger.setLevel(
    logging.INFO
)


# Prevent duplicate handlers
if not logger.handlers:

    file_handler = logging.FileHandler(
        LOG_FILE
    )

    console_handler = logging.StreamHandler()


    formatter = logging.Formatter(
        "%(asctime)s | "
        "%(levelname)s | "
        "%(message)s"
    )


    file_handler.setFormatter(
        formatter
    )

    console_handler.setFormatter(
        formatter
    )


    logger.addHandler(
        file_handler
    )

    logger.addHandler(
        console_handler
    )


def info(message):

    logger.info(message)


def warning(message):

    logger.warning(message)


def error(message):

    logger.error(message)


def critical(message):

    logger.critical(message)


def event(event_type, message):

    logger.info(
        f"EVENT | {event_type} | {message}"
    )


def alert(message):

    logger.warning(
        f"ALERT | {message}"
    )


def startup():

    logger.info(
        "=" * 45
    )

    logger.info(
        "SATARK v2.0 STARTED"
    )

    logger.info(
        "Driver Monitoring & Safety System"
    )

    logger.info(
        "=" * 45
    )


def shutdown():

    logger.info(
        "SATARK system stopped"
    )
