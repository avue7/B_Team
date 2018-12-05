#!/usr/bin/python3
'''
This code is meant to detect motion and, upon detecting motion, take a
picture and send it to the supplied email. In its current state, all it
will do is send an email. For whatever reason, Pi is having issues
taking a picture.
'''
from gpiozero import MotionSensor
import sys
import smtplib
import pygame
import pygame.camera
from pygame.locals import *

visitor = "unknown visitor"
yourEmail = "thebteam548@gmail.com"
server = smtplib.SMTP()
msg = "A(n) {} is at the door.".format(visitor) #currently, this is the message that will be sent.
pir = MotionSensor(4)
pygame.init()
pygame.camera.init()
#cam = pygame.camera.Camera("/dev/video0",(640,480))
'''
The above is the piece of code that Pi doesn't seem to like. We will
need to set cam and connect it to the camera we intend to use in the 
final project.
'''

yourEmail = input("What is your email address: ")
'''
Check your spam folder.
'''

while True:
	print("Waiting for motion.")
	#cam.start()
	#img = cam.get_image()
	'''
	Upon detecting motion (or at the press of a button in our case) the
	camera should start and take a picture, which will be called "img".
	'''
	print("Motion detected. Picture taken.")
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
	print("Motion detected. Email sent.")
	server.quit()
	pir.wait_for_no_motion()
	'''
	Currently this relies on motion, but our project idea calls for a button.
	We can decide whether we still want to use a button, switch to motion, or
	just use a keyboard key to activate it. We should consider what would be
	easiest to present to the rest of the class.
	'''