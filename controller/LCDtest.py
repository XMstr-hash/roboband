from RPLCD.gpio import CharLCD
from RPi.GPIO import BCM

lcd = CharLCD(
    pin_rs=22,
    pin_e=23,
    pins_data=[24,25,5,6],
    numbering_mode=BCM,
    cols=16,
    rows=2
)

lcd.clear()
lcd.write_string("ROBOBAND")
lcd.cursor_pos = (1, 0)
lcd.write_string("LCD TEST")