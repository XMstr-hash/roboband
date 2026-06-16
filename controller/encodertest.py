import RPi.GPIO as GPIO
import time

CLK = 17
DT  = 18
SW  = 27

GPIO.setmode(GPIO.BCM)

GPIO.setup(CLK, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(DT, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(SW, GPIO.IN, pull_up_down=GPIO.PUD_UP)

last_clk = GPIO.input(CLK)

while True:

    current_clk = GPIO.input(CLK)

    if current_clk != last_clk:

        if GPIO.input(DT) != current_clk:
            print("RIGHT")
        else:
            print("LEFT")

    last_clk = current_clk

    if GPIO.input(SW) == 0:
        print("BUTTON")
        time.sleep(0.2)

    time.sleep(0.01)