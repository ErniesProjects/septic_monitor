#Monitors 120VAC powering pump

import signal
import sys
import time

import RPi.GPIO as GPIO

from septic_monitor import storage

PUMP_AC_POWER_GPIO = 17

def signal_handler(sig, frame):
    GPIO.cleanup()
    sys.exit(0)

if __name__ == '__main__':
    
    GPIO.setmode(GPIO.BCM)

    GPIO.setup(PUMP_AC_POWER_GPIO, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

    signal.signal(signal.SIGINT, signal_handler)

    
    while True:
        
        PUMP_AC_STATE = GPIO.input(PUMP_AC_POWER_GPIO)
        
        if PUMP_AC_STATE == 1:
            print("Pump AC OK")
            
        else:
            print("Pump AC Fail")
            storage.set_pump_ac_fail()
            
        time.sleep(60)