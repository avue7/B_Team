##
# @file trip_then_text.py
#
# @author Athit Vue
# @date 9/10/2018
#
# @brief 
#    A simple program with PIR. When motion is detected it sends 
#    a text message to a phone number using twilio's Rest api. The 
#    message will include: sensor number, date, and time. 

from datetime import datetime
from gpiozero import MotionSensor
from twilio.rest import Client

pir = MotionSensor(4)
notified = 0

##
# format_date
#
# This method formats the time object passed to it in the following 
# format: xx/xx/xxxx @ xx:xx:xx am/pm.
#
# @param time_tripped The date-time object.
# @return formatted_date The date-time object that has been formmated
def format_date(time_tripped):
    formatted_date = time_tripped.strftime('%m/%d/%Y @ %I:%M:%S %p')
    return formatted_date

##
# notify
# 
# When sensor is triggered, this method will be invoked and make 
# an api call that will send a text message to the "to" phone number
# 
# @param time_tripped The time that the motion detected was triggered
def notify(time_tripped):
    account_sid = "AC0c8a9a36ec0ce06faee25529cd2e76a2"
    auth_token = "47f6321d24610826fecef68747cbf81e"
    
    client = Client(account_sid, auth_token)
    message = client.messages.create(
            to="+15304888429",
            # Number registered to my twilio account
            from_="+15304045494",
            body="\nSensor one was " + "tripped on:\n" + 
            time_tripped
    )
    print("Message sent!")
    return

# While loop to run the program indefinitely. First it will wait for
# one second to see if motion is detected (you can set this number
# in the parameter to wait longer) before moving on to the next line.
# If motion is detected then there is a logic that will check to 
# see if that trigger has been already notified. If not the n it will
# invoke the notify method to send a text message to the "to" phone
# number. When there is no motion detected the program prints 
# "no motion detected" to standard output and the notified flag gets 
# set back to 0. 
while True:
    pir.wait_for_motion(1)
    if pir.motion_detected and notified == 0:
        time_tripped = datetime.now()
        formatted_date = format_date(time_tripped)
        print("Motion detected")
        print(str(formatted_date))
        notify(formatted_date);
        notified = 1
    pir.wait_for_no_motion(0)
    if not pir.motion_detected:
        notified = 0
        print("No motion detected")

