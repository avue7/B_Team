# Athit Vue
#
# Description: a very simple motion detector program for 
# the raspberry pi 3.

import time

from datetime import datetime

from gpiozero import MotionSensor

pir = MotionSensor(4)

while True:
    pir.wait_for_motion(3)
    if pir.motion_detected:
        print("You Moved")
        print(datetime.now())
        #time.sleep(3)
    pir.wait_for_no_motion(0)
    if not pir.motion_detected:
        print("No motion detected")
