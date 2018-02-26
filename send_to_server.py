import os

import picamera
from time import sleep, time

camera = picamera.PiCamera()
camera.resolution = (640, 480)
camera.framerate = 15
camera.vflip = True
camera.hflip = True
camera.brightness = 50
counter = 0
camera.start_preview()
sleep(0.5)

def click_picture():
    global camera
    camera.capture('image.jpg')
    print ("Clicked Image")
    sleep(0.5)
    os.popen("cat image.jpg | nc 192.168.0.110 2999")
    print ("Image sent")
    os.popen("nc -l 2999")

while True:
	click_picture()