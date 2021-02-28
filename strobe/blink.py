import os
from time import sleep

import RPi.GPIO as GPIO

blinkDuration = float(os.getenv('BLINK_DURATION', 0.03))

relay_pins = [26, 19, 13, 6, 5, 21, 20, 16]


def blink():
    GPIO.output(relay_pins, 0)
    sleep(blinkDuration)
    GPIO.output(relay_pins, 1)


def setup_blinkers():
    print("▶ setup_blinkers")
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(relay_pins, GPIO.OUT)
    GPIO.output(relay_pins, 1)


def cleanup_blinkers():
    print("❌ cleanup_blinkers")
    GPIO.cleanup()


# setup_blinkers()
#
# try:
#     while True:
#         blink()
#         sleep(1)
# except KeyboardInterrupt:
#     pass
# cleanup_blinkers()
