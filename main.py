import RPi.GPIO as GPIO
from time import sleep

relay_pins = [26, 19, 13, 6]
# led_pins = [21, 20, 16, 12]
GPIO.setmode(GPIO.BCM)
GPIO.setup(relay_pins, GPIO.OUT)
# GPIO.setup(led_pins, GPIO.OUT)
GPIO.output(relay_pins, 1)
# GPIO.output(led_pins, 1)
try:
    while True:
        for pin in relay_pins:
            GPIO.output(pin, 0)
            sleep(1)
        for pin in relay_pins:
            GPIO.output(pin, 1)
            sleep(1)
except KeyboardInterrupt:
    pass
GPIO.cleanup()
