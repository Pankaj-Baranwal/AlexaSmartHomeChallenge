import cv2
import sys
import imutils
import numpy as np

if __name__ == '__main__' :
 
    # Read video
    video = cv2.VideoCapture(0)
 
    # Exit if video not opened.
    if not video.isOpened():
        print ("Could not open video")
        sys.exit()
 
    # Read first frame.
    # Frame = 480x640 or heightxwidth
    _, frame = video.read()

    while True:
        # Define an initial bounding box representing the following: (top_x, top_y, distance_between_top_and_bottom_x, distance_between_top_and_bottom_y)
        bbox = (182, 274, 209-182, 340-274)
        # bbox = (373, 264, 418-373, 368-264)
        bbox = cv2.selectROI(frame, False)

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
        mean_bg_color_top = mean_bg_color_top / (bottom_right_p[0] - top_left_p[0])
        mean_bg_color_bottom = mean_bg_color_bottom / (bottom_right_p[0] - top_left_p[0])
        mean_bg_color_left = mean_bg_color_left / (bottom_right_p[1] - top_left_p[1])
        mean_bg_color_right = mean_bg_color_right / (bottom_right_p[1] - top_left_p[1])
        mean_bg_color = [list(mean_bg_color_top), list(mean_bg_color_bottom), list(mean_bg_color_left), list(mean_bg_color_right)]
        print (mean_bg_color)