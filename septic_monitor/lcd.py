import time

from RPLCD.i2c import CharLCD


from time import sleep

LCD = CharLCD(
    i2c_expander="PCF8574",
    address=0x27,  # i2cdetect -y 1
    port=1,
    charmap="A00",
    cols=20,
    rows=4
)


LCD.clear()

class Cursor:
    time = (3, 0)
    date = (3, 10)
    distance = (2, 0)
    
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
    lcd.cursor_pos = Cursor.time
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

    lcd.cursor_pos = 
    lcd.write_string("Distance: ")
    lcd.write_string(Udist)
    lcd.write_string(" cm ")
