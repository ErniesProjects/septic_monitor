#Read pump AC current while pump is running
#Monitors 120VAC powering pump

import RPi.GPIO as GPIO

import signal  
import sys
import time

import board
import busio
import adafruit_ads1x15.ads1015 as ADS
from adafruit_ads1x15.analog_in import AnalogIn

PUMP_RUNNING_GPIO = 16
PUMP_AC_POWER_GPIO = 12
LED_GPIO = 20

i2c = busio.I2C(board.SCL, board.SDA)
ads = ADS.ADS1015(i2c)
chan = AnalogIn(ads, ADS.P0)

def signal_handler(sig, frame):
    GPIO.cleanup()
    sys.exit(0)

def pump_AC_callback(channel):
    print("Pump AC Fail")

def pump_current_callback(channel):
    print("Pump Running")
    print("{:>5}\t{:>5}".format("-Raw-", "AC Current"))
    
    PUMP_STATE = 1
    
    while PUMP_STATE == 1:
        PUMP_STATE = GPIO.input(PUMP_RUNNING_GPIO)
        print("{:>5}\t{:>5.3f}".format(chan.value, chan.voltage))
        time.sleep(2)

if __name__ == '__main__':
    GPIO.setmode(GPIO.BCM)
    
    GPIO.setup(PUMP_RUNNING_GPIO, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(PUMP_AC_POWER_GPIO, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(LED_GPIO, GPIO.OUT)
    
    GPIO.add_event_detect(PUMP_RUNNING_GPIO, GPIO.RISING, 
            callback=pump_current_callback, bouncetime=50)
    
    GPIO.add_event_detect(PUMP_AC_POWER_GPIO, GPIO.FALLING, 
            callback=pump_AC_callback, bouncetime=50)
    
    signal.signal(signal.SIGINT, signal_handler)

# Do something!

<<<<<<< HEAD
    while True:
        GPIO.output(LED_GPIO, GPIO.HIGH)
        time.sleep(0.5)
        GPIO.output(LED_GPIO, GPIO.LOW)
        time.sleep(0.5)
=======
while True:
    print("{:>5}\t{:>5.3f}".format(chan.value, chan.voltage))
    time.sleep(0.5)
>>>>>>> 25cf0810de7516d23d2847153b6c196d7a0cec6b
