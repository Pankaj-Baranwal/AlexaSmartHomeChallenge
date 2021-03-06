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
from  __builtin__ import any as b_any
import numpy as np


objects_superset = ["yellow bench", "red chair", "computer desk"]
color_objects_superset = [[[95, 168, 199], [95, 167, 201], [102, 164, 197], [90, 169, 209]], \
[[52, 33, 133], [40, 36, 134], [41, 33, 139], [45, 37, 137]], \
[[184, 200, 184], [177, 198, 186], [183, 200, 183], [185, 198, 184]]]
objects_to_be_found = ["cell phone", "bottle"]

def largest_indices(ary, n):
    """Returns the n largest indices from a numpy array."""
    flat = ary.flatten()
    indices = np.argpartition(flat, -n)[-n:]
    indices = indices[np.argsort(-flat[indices])]
    return np.unravel_index(indices, ary.shape)

def detect_objects(frame):
    cv2.imwrite('first_frame.jpg', frame)

    # Making sure that the file is now available on disk
    while(True):
        i=0
        for fname in os.listdir('.'):
            if fname == "first_frame.jpg":
                i = 1
                break
        if i == 1:
            break

    # Run darknet from python
    p = subprocess.Popen(["./darknet", "detector",  "test",  "cfg/coco.data", "cfg/yolo.cfg", "yolo.weights", "first_frame.jpg"], cwd=os.getcwd(), stdout=subprocess.PIPE).wait()
    
    # If couldn't run darknet, exit
    if p != 0:
        print ('Couldn\'t run darknet')
        sys.exit()

    # Our customized Darknet generates a file containing bounding box of recognized objects
    with open("program.txt") as f:
        content = f.readlines()
    
    content = [x.strip() for x in content]

    # Selecting desirable objects
    a = []
    for i in content:
        indices = [s.start() for s in re.finditer(',', i)]
        if (b_any(i[:i.find(':')] in x for x in objects_to_be_found)):
            a.append([i[:i.find(':')], int(i[i.find(':')+2:indices[0]]), int(i[indices[0]+1:indices[1]]), int(i[indices[1]+1:indices[2]]), int(i[indices[2]+1:-1])])
            print ("FOUND: ", i[:i.find(':')])
        else:
            print ("Also found: ", i[:i.find(':')])
    return a


if __name__ == '__main__' :

    while True:
        # Read a new frame
        video = cv2.VideoCapture(0)
        _, frame = video.read()
        video.release()

        # Start timer
        timer = cv2.getTickCount()

        p1 = []
        p2 = []
        # b contains bounding boxes of all desirable objects.
        b = detect_objects(frame)
        for j in range(len(b)):
            bbox = []
            bbox = (b[j][1], b[j][2], b[j][3]-b[j][1], b[j][4]-b[j][2])

            top_left_p = (int(bbox[0]), int(bbox[1]))
            bottom_right_p = (int(bbox[0] + bbox[2]), int(bbox[1] + bbox[3]))
            mean_bg_color_top = np.array([0, 0, 0])
            mean_bg_color_bottom = np.array([0, 0, 0])
            mean_bg_color_left = np.array([0, 0, 0])
            mean_bg_color_right = np.array([0, 0, 0])

            # Traversing over top edge and bottom edge.
            for i in range(top_left_p[0], bottom_right_p[0]):
                mean_bg_color_top = mean_bg_color_top + np.array(frame[top_left_p[1]-2][i])
                mean_bg_color_bottom = mean_bg_color_bottom + np.array(frame[top_left_p[1]+2][i])

            # Traversing over left edge and right edge.
            for i in range(top_left_p[1], bottom_right_p[1]):
                mean_bg_color_left = mean_bg_color_left + np.array(frame[i][top_left_p[0]-2])
                mean_bg_color_right = mean_bg_color_right + np.array(frame[i][bottom_right_p[0]+2])
            # Averaging summations over the entire edge
            mean_bg_color_top = mean_bg_color_top / (bottom_right_p[0] - top_left_p[0])
            mean_bg_color_bottom = mean_bg_color_bottom / (bottom_right_p[0] - top_left_p[0])
            mean_bg_color_left = mean_bg_color_left / (bottom_right_p[1] - top_left_p[1])
            mean_bg_color_right = mean_bg_color_right / (bottom_right_p[1] - top_left_p[1])
            mean_bg_color = [mean_bg_color_top, mean_bg_color_bottom, mean_bg_color_left, mean_bg_color_right]
            # print (GreenChair - np.array(mean_bg_color))
            minimum_differnce = [999999, 999999]
            closest_superobject = -1
            for i in range(len(objects_superset)):
                distance_from_big_class = np.square(color_objects_superset[i] - np.array(mean_bg_color))
                if (distance_from_big_class[largest_indices(distance_from_big_class, 2)] < minimum_differnce).all():
                    minimum_differnce = distance_from_big_class[largest_indices(distance_from_big_class, 2)]
                    closest_superobject = objects_superset[i]
            if closest_superobject == -1:
                print ("Couldn't figure the exact location of ", b[j][0])
            else:
                print (b[j][0], " is on ", closest_superobject)
                if b[j][0] == "cell phone":
                    b[j][0] = "phone"
                r = requests.post("https://www.lithics.in/apis/alexa/setObjectLocation.php", data={'location': closest_superobject, 'name': b[j][0]})
                print(r.text)
                if r.text == "SUCCESS!":
                    print ("All good! Saved loaction in database")
                else:
                    print ("Something went wrong. Couldn't save into database")

        print ("Will search again for objects in 5 seconds")
        time.sleep(5)