#!/usr/bin/python3

import sys
import time
import smtplib
import cv2
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from gpiozero import MotionSensor
from datetime import datetime

from twilio.rest import Client

import os
import pygame
import pygame.camera
from pygame.locals import *

# imports from external .py files
from extract_embeddings import extract
from train_model import train
from recognize_video import recognize_video

########### global variable declarations: ############

#yourEmail = "athit_vue@hotmail.com"

server = smtplib.SMTP()
pir = MotionSensor(4)

# set width and height of photo captured
width = 640
height = 480
######################################################

##
# setup_window
#
# Setup the window for pictures captured.
def setup_window(): 
    windowSurfaceObj = pygame.display.set_mode((width, height), 1, 16)
    pygame.display.set_caption('Front Door Camera')
    return windowSurfaceObj

##
# camera_init
#
# Initalize the camera.
# 
# @return cam The camera being used.
def camera_init():
    pygame.init()
    pygame.camera.init()
    cam = pygame.camera.Camera("/dev/video0",(width,height))
    return cam

##
# display_picture
#
# Displays the picture in the windowsurface created
def display_picture(image, windowSurfaceObj):
    catSurfaceObj = image
    windowSurfaceObj.blit(catSurfaceObj, (0,0))
    pygame.display.update()

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

##
# count_down_timer
#
# This timer is to allow the user some time for the 
# taking pictures.
def count_down_timer():
    from_secs = 5
    print("\n[INFO] Camera will start taking pictures in 5 seconds: ")
    while not from_secs == 0:
        mins, secs = divmod(from_secs, 60)
        timeformat = '{:02d}:{:02d}'.format(mins, secs)
        print(timeformat, end='\r')
        time.sleep(1)
        from_secs -= 1
    
    print("\n[INFO] Taking pictures now...")

##
# add_new_known
#
# This method created a new directory for new knowns in the
# asset directory. Then it saves the images that will be used
# for this known person in this directory. The directory's 
# name is the name of the known person for convenience.
def add_new_known():
    name = input("\nWhat is the new known person's name?\n")
    
    windowSurfaceObj = setup_window()
    
    dir_path = "dataset/"+name+"/"
    print("[INFO] Created path: ",dir_path)

    if not os.path.exists(dir_path):
        directory = os.makedirs(dir_path)
    else:
        print("\n[INFO] {} already exists.\n".format(name))
        return

    
    cam = camera_init()
    if not cam:
        print("\nError initializing camera\n")
    cam.start()

    count_down_timer()

    count = 0;
    while (count < 30):
        image = cam.get_image()
        display_picture(image, windowSurfaceObj)
        image_filename = '{}.jpg'.format(count)
        print("[INFO] Saving image: " + image_filename)
        pygame.image.save(windowSurfaceObj, os.path.join(dir_path, image_filename))#image_filename)
        #print("returns from save")
        count = count + 1

    cam.stop()

    pygame.display.quit()
    pygame.quit()

    print("\n[INFO] Done taking {}'s picture.".format(name) + " Extracting embeddings...\n")
    extract()

    print("\n[INFO] Done with embeddings. Training new embeddings...\n")
    train_count = 0
    while train_count < 30:
        train()
        train_count += 1

    print("\n[INFO] Done with training...\n")

##
# add_more_pictures
#
# This method is for adding pictures to a known person's directory.
# Each time this method is called it will save 30 pictures into the
# known person's directory. It checks to see how many images are in 
# the directory, then labels the new files incrementally. This is to
# insure that files do not get replaced.
def add_more_pictures(): 
    count = 0
    file_counter = 0
    name1 = input("\nWhat is the known person's name?\n")
    
    windowSurfaceObj = setup_window()

    dir_path = "dataset/"+name1+"/"
    print("\n[INFO] known person exist: " + dir_path)

    if not os.path.exists(dir_path):
        print("\n[INFO] Known person {}".format(name1) + " does not exists")
        option = input("[INFO] Would you like to add? ")
        
        if option == 'y' or option == 'Y' or option == "yes":
            add_new_person()
        return
    else:
        counter = len(os.listdir(dir_path))
        print("[INFO] number of files in directory is: ", counter)
        file_counter = counter;
    
    cam = camera_init()
    if not cam:
        print("\nError initializing camera\n")
    cam.start()

    count_down_timer()

    while (count < 30):
        image = cam.get_image()
        display_picture(image, windowSurfaceObj)
        file_counter = file_counter + 1
        image_filename = '{}.jpg'.format(file_counter)
        print("[INFO] Saving image: " + image_filename)
        pygame.image.save(windowSurfaceObj, os.path.join(dir_path, image_filename))#image_filename)
        #print("returns from save")
        count = count + 1

    cam.stop()
    
    pygame.display.quit()
    pygame.quit()

    print("\n[INFO] Done taking {}'s picture".format(name1) + ". Extracting embeddings...\n")
    extract()
    print("\n[INFO] Done with embeddings. Training new embeddings...\n")
    
    train_count = 0
    while (train_count < 30):
        train()
        train_count = train_count + 1
    
    print("\n[INFO] Done with training...\n")

##
# start_detection
# 
# This is the main method of this file. It contains a big while loop
# that will check for motion. If motion is detected, it calls the 
# external method recognize_video() from recognize_video.py to start
# the recognition AI. When the recognize_video method returns with 
# the known or unknown name, then it checks to see if the name is 
# unknown. If it is, then an alert is sent to the user's email 
# address with a picture, the frame used for detection. Then it 
# repeats the process.
#
# @param user_email The user's inputted email from main.
def start_detection(user_email):
    notified = 0
    while True:
        pir.wait_for_motion(1)
        if pir.motion_detected and notified == 0:
            time_tripped = datetime.now()
            formatted_date = format_date(time_tripped)
            print("\n[INFO] Motion detected")
            print("[INFO] " + str(formatted_date))
    
            print("\n[INFO] Starting Recognizer...\n")
            ret_name = recognize_video()
            
            if ret_name == "unknown" or ret_name == "":
                ########  This is for sending email  ########
                vistor=''
                if ret_name == "unknown":
                    print("\n[INFO] Unknown person. Sending email...\n") 
                    visitor="Unknown person"
                else:
                    print("\n[INFO] Somebody tripped the sensor, Could not detect.\n")
                    visitor="Somebody"
                # Create the root message and fill in the from, to, and subject headers
                msg = "{} is at the door on ".format(visitor) + str(formatted_date)
                msgRoot = MIMEMultipart('related')
                msgRoot['Subject'] = 'test message'
                msgRoot['From'] = "me"
                msgRoot['To'] = "you"
                msgRoot.preamble = 'This is a multi-part message in MIME format.'
                msgAlternative = MIMEMultipart('alternative')
                msgRoot.attach(msgAlternative)
                msgText = MIMEText(msg)
                msgAlternative.attach(msgText)
               
                for x in range(5):
                    x = x+1
                    fp = open('captured_images/captured_image.{}.jpg'.format(x), 'rb')
                    msgImage = MIMEImage(fp.read())
                    fp.close()
                
                    msgRoot.attach(msgImage)
                
                server.connect('smtp.gmail.com', 587)
                server.starttls()
                server.login("thebteam548@gmail.com", "Bpass548")
                server.sendmail("thebteam548@gmail.com", user_email, msgRoot.as_string())
                
                print("[INFO] Done sending email.\n")
                server.quit()
                #############################################
            else:
                print("\n[INFO] Known person <{}> tripped the sensor.".format(ret_name))
                print("")
            ######### This is for sending a text message ###########
            ## DISABLING FOR NOW
            # notify_thru_text(formatted_date)
            ########################################################
        
        pir.wait_for_no_motion(0)
        if not pir.motion_detected: 
            notified = 0
            print("No motion detected")
        
        
        key = cv2.waitKey(1) & 0xFF
        # if 'q' key is pressed then exit the program gracefully
        if key == ord("q"):
            print("[INFO] Q was pressed exiting...")
            break

##
# main
#
# This is the main method. It provides for a simple user interface so that
# the user can add a new known or add more pictures to a new known. Once 
# user has inputted his/her option, the program will invoke the method
# start_detection() to begin motion detection.
def main():
    print("\n ====== Hello, welcome to the B-Team's stranger detector! ======")
    
    user_email = "athit_vue@hotmail.com"
    #email_option = input("please enter your email address:\n")
    
    print("")
    option = input("Would you like to add a new known person (y/n)? ")
    
    while option == 'y' or option == 'Y' or option == 'Yes' or option == 'YES':
        add_new_known()
        
        option = input("\nWould you like to add another new known person (y/n)? ")
        
        if option == 'n' or option == 'N' or option == 'No' or option == 'NO':
            break;
    
    option1 = input("Would you like to add more pictures to known persons (y/n)? ")
    
    if option1 == 'y' or option1 == 'Y' or option1 == 'Yes' or option1 == 'YES':
        add_more_pictures()
        
    print("\n[INFO] Starting the stranger detection system...\n")
    start_detection(user_email)

main()


