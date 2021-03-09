import os
from time import sleep

import RPi.GPIO as GPIO

from util.logger import logger

blinkDuration = float(os.getenv('BLINK_DURATION', 0.03))

relay_pins = [26, 19, 13, 6, 5, 21, 20, 16]


def blink():
    GPIO.output(relay_pins, 0)
    sleep(blinkDuration)
    GPIO.output(relay_pins, 1)


def setup_blinkers():
    logger.info("▶ setup_blinkers")
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(relay_pins, GPIO.OUT)
    GPIO.output(relay_pins, 1)


def cleanup_blinkers():
    logger.info("❌ cleanup_blinkers")
    GPIO.cleanup()
