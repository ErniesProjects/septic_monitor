import RPi.GPIO as GPIO
import time

# Import sleep library
from time import sleep

GPIO.setwarnings(False)  # Ignore warning for now
GPIO.setmode(GPIO.BCM)  # Use Broadcom channel numbering
PIN_TRIGGER = 14
PIN_ECHO = 15
GPIO.setup(PIN_TRIGGER, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(PIN_ECHO, GPIO.IN)
# constants to initialise the LCD
lcdmode = "i2c"
cols = 20
rows = 4
charmap = "A00"
i2c_expander = "PCF8574"
# Generally 27 is the address;Find yours using: i2cdetect -y 1
address = 0x27
port = 1  # 0 on an older Raspberry Pi
# Initialise the LCD
lcd = i2c.CharLCD(
    i2c_expander, address, port=port, charmap=charmap, cols=cols, rows=rows
)
# Clear the LCD screen
lcd.clear()
# Write a string on first line and move to next line
lcd.cursor_pos = (0, 0)
lcd.write_string("POWER OK")
lcd.cursor_pos = (0, 12)
lcd.write_string("PUMP OFF")
lcd.cursor_pos = (1, 0)
lcd.write_string("LEVEL OK")
lcd.cursor_pos = (1, 12)
lcd.write_string("Ip= 0.0A")
sleep(5)
while True:
    lcd.cursor_pos = (3, 0)
    lcd.write_string(time.strftime("%H:%M:%S"))

    lcd.cursor_pos = (3, 10)
    lcd.write_string(time.strftime("%m/%d/%Y"))

    print("Waiting for sensor to settle")
    sleep(0.2)
    print("Calculating distance")
    GPIO.output(PIN_TRIGGER, GPIO.HIGH)
    sleep(0.00002)
    GPIO.output(PIN_TRIGGER, GPIO.LOW)
    while GPIO.input(PIN_ECHO) == 0:
        pulse_start_time = time.time()
    while GPIO.input(PIN_ECHO) == 1:
        pulse_end_time = time.time()
    pulse_duration = pulse_end_time - pulse_start_time
    distance = round(pulse_duration * 17150, 1)
    print(("Distance:"), distance, ("cm"))

    Udist = str(distance)

    lcd.cursor_pos = (2, 0)
    lcd.write_string("Distance: ")
    lcd.write_string(Udist)
    lcd.write_string(" cm ")
