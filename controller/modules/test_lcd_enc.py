#!/usr/bin/env python3

import RPi.GPIO as GPIO
from time import sleep

# =====================
# LCD1602
# =====================

LCD_RS = 22
LCD_E  = 23

LCD_D4 = 24
LCD_D5 = 25
LCD_D6 = 5
LCD_D7 = 6

# =====================
# KY040
# =====================

ENC_CLK = 17
ENC_DT  = 18
ENC_SW  = 27

counter = 0
button_pressed = False

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

# LCD outputs
for pin in [LCD_RS, LCD_E, LCD_D4, LCD_D5, LCD_D6, LCD_D7]:
    GPIO.setup(pin, GPIO.OUT)

# Encoder inputs
GPIO.setup(ENC_CLK, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(ENC_DT, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(ENC_SW, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# =====================
# LCD functions
# =====================

def pulse():
    GPIO.output(LCD_E, True)
    sleep(0.001)
    GPIO.output(LCD_E, False)
    sleep(0.001)

def write4(bits):
    GPIO.output(LCD_D4, bits & 0x01)
    GPIO.output(LCD_D5, bits & 0x02)
    GPIO.output(LCD_D6, bits & 0x04)
    GPIO.output(LCD_D7, bits & 0x08)
    pulse()

def send(byte, mode):
    GPIO.output(LCD_RS, mode)

    write4((byte >> 4) & 0x0F)
    write4(byte & 0x0F)

def cmd(value):
    send(value, False)

def data(value):
    send(value, True)

def lcd_clear():
    cmd(0x01)
    sleep(0.005)

def lcd_line1():
    cmd(0x80)

def lcd_line2():
    cmd(0xC0)

def lcd_print(text):
    for ch in text.ljust(16)[:16]:
        data(ord(ch))

def lcd_init():

    sleep(0.05)

    write4(0x03)
    sleep(0.005)

    write4(0x03)
    sleep(0.005)

    write4(0x03)
    sleep(0.005)

    write4(0x02)

    cmd(0x28)
    cmd(0x0C)
    cmd(0x06)
    cmd(0x01)

# =====================
# Encoder
# =====================

last_clk = GPIO.input(ENC_CLK)

def encoder_callback(channel):
    global counter, last_clk

    clk_state = GPIO.input(ENC_CLK)
    dt_state = GPIO.input(ENC_DT)

    if clk_state != last_clk:

        if dt_state != clk_state:
            counter += 1
        else:
            counter -= 1

    last_clk = clk_state

def button_callback(channel):
    global button_pressed
    button_pressed = True

GPIO.add_event_detect(
    ENC_CLK,
    GPIO.BOTH,
    callback=encoder_callback,
    bouncetime=1
)

GPIO.add_event_detect(
    ENC_SW,
    GPIO.FALLING,
    callback=button_callback,
    bouncetime=250
)

# =====================
# Main
# =====================

try:

    lcd_init()

    while True:

        lcd_clear()

        lcd_line1()
        lcd_print(f"Value:{counter}")

        lcd_line2()

        if button_pressed:
            lcd_print("Button pressed")
            button_pressed = False
        else:
            lcd_print("KY040 test")

        sleep(0.1)

except KeyboardInterrupt:
    pass

finally:
    GPIO.cleanup()
