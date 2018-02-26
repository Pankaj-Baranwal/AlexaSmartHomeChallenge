import cv2
import sys
import imutils
import copy
import subprocess
import os
import time
import re
import requests
import json
import csv
import requests


object_color_class = []
objects_to_be_found = ["phone", "bottle"]
(major_ver, minor_ver, subminor_ver) = (cv2.__version__).split('.')

if __name__ == '__main__' :
 
    # Set up tracker.
    # Instead of MIL, you can also use
 
    tracker_types = ['BOOSTING', 'MIL','KCF', 'TLD', 'MEDIANFLOW', 'GOTURN']
    tracker_type = tracker_types[2]
 
    print ("Waiting for image")
    # os.popen("cat image%s.jpg | nc 192.168.1.112 3000"%counter)
    # subprocess.Popen(["nc", "-l",  "3000",  ">", "received.jpg"], cwd=os.getcwd(), stdout=subprocess.PIPE).wait()
    os.popen("nc -l 3000 > received.jpg")
    time.sleep(0.5)
    print ("Image received")

    frame = cv2.imread("received.jpg");

    cmd = "./darknet"

    p = subprocess.Popen([cmd, "detector",  "test",  "cfg/coco.data", "cfg/yolo.cfg", "yolo.weights", "received.jpg"], cwd=os.getcwd(), stdout=subprocess.PIPE).wait()
    if p != 0:
        print ('Couldn\'t run darknet')
        sys.exit()

    with open("program.txt") as f:
        content = f.readlines()
    # you may also want to remove whitespace characters like `\n` at the end of each line
    content = [x.strip() for x in content]
    a = []
    for i in content:
        indices = [s.start() for s in re.finditer(',', i)]
        if (i[:i.find(':')] in objects_to_be_found):
        	a.append([i[:i.find(':')], int(i[i.find(':')+2:indices[0]]), int(i[indices[0]+1:indices[1]]), int(i[indices[1]+1:indices[2]]), int(i[indices[2]+1:-1])])
        else:
            print (i[:i.find(':')])
    
    bbox = []
    tracker = []
    for i in range(len(a)):
        if int(minor_ver) < 3:
            tracker[i] = cv2.Tracker_create(tracker_type)
        else:
            if tracker_type == 'BOOSTING':
                tracker[i] = cv2.TrackerBoosting_create()
            if tracker_type == 'MIL':
                tracker[i] = cv2.TrackerMIL_create()
            if tracker_type == 'KCF':
                tracker.append(cv2.TrackerKCF_create())
            if tracker_type == 'TLD':
                tracker[i] = cv2.TrackerTLD_create()
            if tracker_type == 'MEDIANFLOW':
                tracker[i] = cv2.TrackerMedianFlow_create()
            if tracker_type == 'GOTURN':
                tracker[i] = cv2.TrackerGOTURN_create()
        bbox.append((a[i][1], a[i][2], a[i][3], a[i][4]))
        print ([(a[i][1], a[i][2], a[i][3], a[i][4])])
        # Initialize tracker with first frame and bounding box
        tracker[i].init(frame, bbox[i])

    while True:
        print ("Sending data")
        time.sleep(0.5)
        os.popen("cat send.txt | nc 192.168.0.109 3000")
        time.sleep(0.5)
        print ("Waiting for Image")
        os.popen("nc -l 3000 > received.jpg")
        print ("Image received")

        frame = cv2.imread("received.jpg")
         
        # Start timer
        timer = cv2.getTickCount()

        p1 = []
        p2 = []
        for i in range(len(a)):
            ok, bbox[i] = tracker[i].update(frame)
            if ok:
                print ("OBJECT ", i, ": ", a[i][0])
                print (bbox[i][0], " ", bbox[i][1], " ", bbox[i][2], " ", bbox[i][3])
                p1.append((int(bbox[i][0]), int(bbox[i][1])))
                p2.append((int(bbox[i][2]), int(bbox[i][3])))
                cv2.rectangle(frame, p1[i], p2[i], (255,0,0), 2, 1)
                r_mean_bottom = 0
                g_mean_bottom = 0
                b_mean_bottom = 0
                # print (len(frame), "  ", len(frame[0]))
                for k in range(int(bbox[i][0]), int(bbox[i][2])):
                    for j in range(int(bbox[i][3])+2, int(bbox[i][3])+10):
                        r_mean_bottom = r_mean_bottom + frame[j][k][0]
                        g_mean_bottom = g_mean_bottom + frame[j][k][1]
                        b_mean_bottom = b_mean_bottom + frame[j][k][2]
                r_mean_bottom = r_mean_bottom/((bbox[i][2]-bbox[i][0])*8)
                g_mean_bottom = g_mean_bottom/((bbox[i][3]-bbox[i][1])*8)
                b_mean_bottom = b_mean_bottom/((bbox[i][3]-bbox[i][1])*8)
                r_mean_right = 0
                g_mean_right = 0
                b_mean_right = 0
                for k in range(int(bbox[i][1]), int(bbox[i][3])):
                    for j in range(int(bbox[i][2])+2, int(bbox[i][2])+10):
                        r_mean_right = r_mean_right + frame[k][j][0]
                        g_mean_right = g_mean_right + frame[k][j][1]
                        b_mean_right = b_mean_right + frame[k][j][2]
                r_mean_right = r_mean_right/((bbox[i][2]-bbox[i][0])*8)
                g_mean_right = g_mean_right/((bbox[i][3]-bbox[i][1])*8)
                b_mean_right = b_mean_right/((bbox[i][3]-bbox[i][1])*8)
            else :
                # Tracking failure
                cv2.putText(frame, "Tracking failure detected", (100,80), cv2.FONT_HERSHEY_SIMPLEX, 0.75,(0,0,255),2)
 
        # Calculate Frames per second (FPS)
        fps = cv2.getTickFrequency() / (cv2.getTickCount() - timer);
 
        # Display tracker type on frame
        cv2.putText(frame, tracker_type + " Tracker", (100,20), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (50,170,50),2);
     
        # Display FPS on frame
        cv2.putText(frame, "FPS : " + str(int(fps)), (100,50), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (50,170,50), 2);
        
        # Display result
        cv2.imshow("Tracking", frame)
 
        # Exit if ESC pressed
        k = cv2.waitKey(1) & 0xff
        if k == 27 : break

def findLocation(rgb_bot_mean, rgb_right_mean):
    distance = []
    a = []
    for i in range(len(object_color_class)):
        a.append(i+1)
        a.append((abs(object_color_class[i,0]-rgb_bot_mean[i,0])+abs(object_color_class[i,1]-rgb_bot_mean[i,1])+abs(object_color_class[i,2]-rgb_bot_mean[i,2])/3)+(abs(object_color_class[i,0]-rgb_right_mean[i,0])+abs(object_color_class[i,1]-rgb_right_mean[i,1])+abs(object_color_class[i,2]-rgb_right_mean[i,2]))/3)
        distance.append(a)
