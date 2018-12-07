#!/usr/bin/python3
'''
This code is meant to detect motion and, upon detecting motion, take a
picture and send it to the supplied email. In its current state, all it
will do is send an email. For whatever reason, Pi is having issues
taking a picture.
'''
import sys
import smtplib

from gpiozero import MotionSensor
from datetime import datetime

from twilio.rest import Client

#webcam
import os
import pygame, sys
import pygame.camera
from pygame.locals import *

#variable declarations:
notified = 0
visitor = "unknown visitor"

#yourEmail = "thebteam548@gmail.com"
##Testing with my email....change this to yours for testing...the input does not work.
yourEmail = "athit_vue@hotmail.com"

server = smtplib.SMTP()
msg = "A(n) {} is at the door.".format(visitor) #currently, this is the message that will be sent.
pir = MotionSensor(4)

#set width and height of photo captured
width = 640
height = 480

#setup window 
windowSurfaceObj = pygame.display.set_mode((width, height), 1, 16)
pygame.display.set_caption('Front Door Camera')

#initialise pygame 
def camera_init():
    pygame.init()
    pygame.camera.init()
    cam = pygame.camera.Camera("/dev/video0",(width,height))
    cam.start()
    return cam

#display the picture (may not need only for debugging)
def display_picture(image):
    catSurfaceObj = image
    windowSurfaceObj.blit(catSurfaceObj, (0,0))
    pygame.display.update()

'''
The above is the piece of code that Pi doesn't seem to like. We will
need to set cam and connect it to the camera we intend to use in the 
final project.
'''

#yourEmail = input("What is your email address: ")
'''
Check your spam folder.
'''

##
# format_date
# 
# This method formats the time object passed to it in the following 
# format: xx/xx/xxxx @ xx:xx:xx am/pm. This is for debugging purposes
#
# @param time_tripped The date-time object. 
# @return formatted_date The date-time object that has been formatted. 
def format_date(time_tripped):
    formatted_date = time_tripped.strftime('%m/%d/%Y @ %I:%M:%S %p')
    return formatted_date

##
# notify_thru_text
#
# When sensor is tripped, this method will be invoked and make an 
# api call that will send a text message to the "to" phone number. 
# 
# @param time_tripped The time that the motion was detected. 
def notify_thru_text(time_tripped):
    account_sid = "AC0c8a9a36ec0ce06faee25529cd2e76a2"
    auth_token = "47f6321d24610826fecef68747cbf81e"

    client = Client(account_sid, auth_token)
    message = client.messages.create(
        to="+15304888429", 
        ## Number registered to Athit's twilio account
        from_="+15304045494", 
        body="\nSomeone is at the door!\n" + time_tripped
    )
    print("Text message sent!")
    return

while True:
	#print("Waiting for motion.")
	#cam.start()
	#img = cam.get_image()
	'''
	Upon detecting motion (or at the press of a button in our case) the
	camera should start and take a picture, which will be called "img".
	'''
	#print("Motion detected. Picture taken.")
	pir.wait_for_motion(1)
        if pir.motion_detected and notified == 0:
            time_tripped = datetime.now()
            formatted_date = format_date(time_tripped)
            print("Motion detected")
            print(str(formatted_date))

            ########  Taking a picture  #########
            cam = camera_init()
            image = cam.get_image()
            cam.stop()

            #display the picture (optional for debugging only)
            display_picture(image)

            #save picture
            pygame.image.save(windowSurfaceObj, 'capture_pic.jpg')
            #####################################

            ########  This is for sending email  ########
            print("Sending email...")
            server.connect('smtp.gmail.com', 587)
    	    server.starttls()
	    server.login("thebteam548@gmail.com", "Bpass548") #This is the email address we're using to send the email.
	    server.sendmail("thebteam548@gmail.com", yourEmail, msg) #Right now, we're just sending an email to ourselves.
	    #msg.attach(img)
	    '''
	    At this point, img should be attached to our email. In addition, face
	    recognition should be used to identify if the img is recognized or not.
	    If the image is not recognized, visitor should be changed to "stranger"
	    or, if the face is recognized, visitor could be set to acquaintance.
	
	    If, for whatever reason, we cannot detect their face (i.e. back is turned),
	    the visitor variable will stay at the default "unknown visitor" with the
	    attached image. If we want to go further, we can have the face recognition
	    seperate known faces into a category of "friends", "family", and "acquaintances".
	    '''
            print("Done sending email.")
	    server.quit()
	    #############################################

            ######### This is for sending a text message ###########
            ## DISABLING FOR NOW
            # notify_thru_text(formatted_date)
            ########################################################
        
        pir.wait_for_no_motion(0)
        if not pir.motion_detected: 
            notified = 0
            print("No motion detected")
	    '''
	    Currently this relies on motion, but our project idea calls for a button.
	    We can decide whether we still want to use a button, switch to motion, or
	    just use a keyboard key to activate it. We should consider what would be
	    easiest to present to the rest of the class.
	    '''
