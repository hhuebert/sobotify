#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Attribution: Part of this code is based on 
https://github.com/Kazuhito00/mediapipe-python-sample/blob/main/sample_pose.py
https://github.com/elggem/naoqi-pose-retargeting/blob/main/teleop.py
(both Apache 2.0 Licensed)
"""

import csv
import cv2 as cv
import numpy as np
import mediapipe as mp
import argparse
import sys
import os
from datetime import datetime
import time

import sobotify.robots.stickman.stickman as stickman


def store_landmarks(landmarks,time_stamp,filename) :
    landmarks_array = []
    for index, landmark in enumerate(landmarks):
        landmarks_array.append([landmark.x, landmark.y, landmark.z,landmark.visibility])
    landmarks_array = np.array(landmarks_array)
    #np.savetxt(filename,landmarks_array);
    row = np.insert(landmarks_array.flatten(),0,time_stamp)
    #print (row)
    with open(filename, "a", newline='') as f:
        wr = csv.writer(f)
        wr.writerow(row)
    return landmarks_array


def video2landmarks(video_file,data_path,show_video):

    if (show_video=="on"):
        motion_visualizer=stickman.motion()

    cap_width  = 960 # default=960
    cap_height = 540 # default=540
    
    model_complexity         = 1   # model_complexity(0,1(default),2)
    min_detection_confidence = 0.5 #  default=0.5
    min_tracking_confidence  = 0.5 #  default=0.5

    fileName, ext = os.path.splitext(os.path.basename(video_file))

    landmarks_filename= os.path.join(data_path,fileName+"_lmarks.csv")
    world_landmarks_filename= os.path.join(data_path,fileName+"_wlmarks.csv")
    time_stamp_filename= os.path.join(data_path,fileName+".tsp")
    if os.path.exists(landmarks_filename):
        os.remove(landmarks_filename)
    if os.path.exists(world_landmarks_filename):
        os.remove(world_landmarks_filename)

    time_stamps = open(time_stamp_filename,'r')

    cap = cv.VideoCapture(video_file)
    cap.set(cv.CAP_PROP_FRAME_WIDTH, cap_width)
    cap.set(cv.CAP_PROP_FRAME_HEIGHT, cap_height)

    mp_pose = mp.solutions.pose
    pose = mp_pose.Pose(
        model_complexity=model_complexity,
        enable_segmentation=False,
        min_detection_confidence=min_detection_confidence,
        min_tracking_confidence=min_tracking_confidence,
    )
    
    ## read timestamps for each frame from file for exact synchronization
    
    while True:

        ret, image = cap.read()
        if not ret:
            break
        #image = cv.flip(image, 1)
        if (show_video=="on"):
            image_small=cv.resize(image,(0,0),fx=0.5,fy=0.5)
            cv.imshow("Image",image_small)
            if cv.waitKey(1) == ord("q"):
                break
        image = cv.cvtColor(image, cv.COLOR_BGR2RGB)
        results = pose.process(image)
        pts_string , time_stamp_string = time_stamps.readline().split('=')
        try:
            time_stamp=float(time_stamp_string)
            print (time_stamp)
            #print (results.pose_world_landmarks.landmark)

            if results.pose_landmarks is not None:
                landmarks_array=store_landmarks(results.pose_landmarks.landmark,time_stamp,landmarks_filename)
                if show_video=="on":
                    motion_visualizer.move(landmarks_array)
            if results.pose_world_landmarks is not None:
                world_landmarks_array = store_landmarks(results.pose_world_landmarks.landmark,time_stamp,world_landmarks_filename)            
        except:
            break
    cap.release()
    if (show_video=="on"):
        motion_visualizer.stop()
        time.sleep(0.2)
        cv.destroyAllWindows()
    
if __name__ == '__main__':
    parser=argparse.ArgumentParser(description='extract human gestures/poses from video file and store them as landmarks in csv text file')
    parser.add_argument('--video_file',default='video.mp4',help='path to the video input file')
    parser.add_argument('--data_path',default=os.path.expanduser("~")+"/.sobotify/data",help='path to movement/speech data')
    parser.add_argument('--show_video',default="on",help='enable/disable video output on screen')
    args=parser.parse_args()
    video2landmarks(args.video_file,args.data_path,args.show_video)
    
