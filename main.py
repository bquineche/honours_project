import time
from picamera import PiCamera
import datetime as dt
import datetime
import pigpio
import RPi.GPIO as GPIO
from random import randrange


def feeder_activate(rand_number):
    """ " " 
    takes as input a random int either 0 or 1
    depending on that, it will activate either feeder 1 or 2
    0 corresponds to feeder 1
    1 corresponds to feeder 2
    " " """
    if rand_number == 0:
        feeder_pin = 16
        print('Activating Feeder #1')
    elif rand_number == 1:
        feeder_pin = 37
        print('Activating Feeder #2')
    else:
        feeder_pin = 0
        print("Invalid option.")
        return 0
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(feeder_pin, GPIO.OUT)
    servo1 = GPIO.PWM(feeder_pin, 50)
    servo1.start(0)
    print('Waiting for 1 second')
    time.sleep(1)
    # Moving the servo
    duty = 2
    while duty <= 4:
        servo1.ChangeDutyCycle(duty)
        time.sleep(0.1)  # just enough time for the wing to get there
        servo1.ChangeDutyCycle(0)  # then we set it to 0 so it stops
        time.sleep(0.1)  # time we want it to stop for
        duty = duty + 1  # then continue to next iteration
    # Wait one second
    time.sleep(1)
    # Turn back to 0 degrees
    print('Turning back to 0 degrees!')
    servo1.ChangeDutyCycle(2)
    time.sleep(0.5)
    servo1.ChangeDutyCycle(0)
    servo1.stop()
    print('Cleaning up...')
    GPIO.cleanup()
    print('All done!')

print("Welcome to the automated chamber!")
camera = PiCamera()
print("Passed PiCamera() line")
camera.resolution = (1640, 1232)
camera.rotation = 0
camera.iso = 800
print("Starting up the camera...")
# Waiting for automatic gain control to settle
time.sleep(2)
# Making camera values fixed
camera.shutter_speed = camera.exposure_speed
camera.exposure_mode = 'off'
g = camera.awb_gains
camera.awb_mode = 'off'
camera.awb_gains = g
camera.start_preview()
print('Previewing Now')
now = datetime.datetime.now()
dt_string = now.strftime('/home/pi/automated_chamber/training_videos/train%d%m%Y_%H%M%S.h264')
print('Date and time: ', dt_string)

camera.start_recording(dt_string)
print('Recording first 3 minutes: baseline before we trigger the lights')
for x in range(0, 180):
    camera.annotate_background = True
    camera.annotate_text = dt.datetime.now().strftime('%m-%d %H: %M: %S:')
    time.sleep(1)
# trigger lights 5 seconds BEFORE feeder
rand_Number = randrange(2)
pi = pigpio.pi()
print('Turning lights ON...')
if rand_Number == 0:
    pi.set_PWM_dutycycle(22, 75)
else:
    pi.set_PWM_dutycycle(6, 75)
time.sleep(5)
# trigger feeder now!
print('Activating Feeder...')
#feeder_activate(rand_Number)
# turn off light
print('Turning lights OFF...')
pi.set_PWM_dutycycle(22, 0)
pi.set_PWM_dutycycle(24, 0)
pi.set_PWM_dutycycle(17, 0)
pi.set_PWM_dutycycle(5, 0)
pi.set_PWM_dutycycle(6, 0)
pi.set_PWM_dutycycle(16, 0)
pi.stop()

print('Recording last 3 minutes: after light stimulus')
for x in range(0, 180): 
    camera.annotate_background = True
    camera.annotate_text = dt.datetime.now().strftime('%m-%d %H: %M: %S:')
    time.sleep(1)
print('Terminating program...')
camera.stop_recording()
camera.stop_preview()
camera.close()
