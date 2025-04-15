import RPi.GPIO as GPIO
import time

# Ultrasonic sensor pins
TRIG = 23
ECHO = 24

# Relay control pins
PUMP = 17
VALVES = [27, 22, 5, 6]

BARREL_HEIGHT_CM = 100
THRESHOLD = 25  # minimum % water to use barrel

def setup():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(TRIG, GPIO.OUT)
    GPIO.setup(ECHO, GPIO.IN)
    for pin in [PUMP] + VALVES:
        GPIO.setup(pin, GPIO.OUT)

def get_distance_cm():
    GPIO.output(TRIG, False)
    time.sleep(0.5)
    GPIO.output(TRIG, True)
    time.sleep(0.00001)
    GPIO.output(TRIG, False)

    while GPIO.input(ECHO) == 0:
        start = time.time()
    while GPIO.input(ECHO) == 1:
        end = time.time()

    duration = end - start
    distance = duration * 34300 / 2
    return distance

def get_water_level_percent(distance_cm):
    return max(0, (BARREL_HEIGHT_CM - distance_cm) / BARREL_HEIGHT_CM * 100)

def activate_outputs(use_barrel=True):
    if use_barrel:
        GPIO.output(PUMP, GPIO.HIGH)
    else:
        GPIO.output(PUMP, GPIO.LOW)  # or switch to a network valve if you have one

    for pin in VALVES:
        GPIO.output(pin, GPIO.HIGH)  # open valves

def deactivate_outputs():
    GPIO.output(PUMP, GPIO.LOW)
    for pin in VALVES:
        GPIO.output(pin, GPIO.LOW)

try:
    setup()
    dist = get_distance_cm()
    level = get_water_level_percent(dist)
    print(f"Water Level: {level:.1f}%")

    if level >= THRESHOLD:
        print("Using barrel water")
        activate_outputs(use_barrel=True)
    else:
        print("Using network water")
        activate_outputs(use_barrel=False)

    time.sleep(10 * 60)  # run for 10 minutes
    deactivate_outputs()

except KeyboardInterrupt:
    deactivate_outputs()
    GPIO.cleanup()
