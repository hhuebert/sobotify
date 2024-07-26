#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Attribution: This code applies the draw_landmarks() function, which is based on the these codes and ideas 
https://github.com/Kazuhito00/mediapipe-python-sample/blob/main/sample_pose.py
https://github.com/elggem/naoqi-pose-retargeting/blob/main/teleop.py
(Apache 2.0 Licensed)
"""
import subprocess
import sys
import os
import numpy as np
import cv2 as cv
import sounddevice as sd
import queue
from sobotify.commons.external.utils import draw_landmarks
import sobotify.robots.robot as default_robot
import threading

class stickman(): 

    def __init__(self,cam_device,sound_device):
        self.motion=motion()
        self.speech=speech()
        self.vision=vision(cam_device)
        self.sound=sound(sound_device)

    def terminate(self):
        self.motion.terminate()
        self.speech.terminate()
        self.vision.terminate()
        self.sound.terminate()
   
class LandmarkItem:
    def __init__(self,x,y,z,visibility):
        self.x=x
        self.y=y
        self.z=z
        self.visibility=visibility

class LandmarkListType(): 
    def __init__(self):
        self.landmark_list=[]
    def add(self,x,y,z,visibility):
        new_item=LandmarkItem(x,y,z,visibility)
        self.landmark_list.append(new_item)
    def __iter__(self):
        return iter(self.landmark_list)

class LandmarkList:
    def __init__(self):
        self.landmark=LandmarkListType()
   
class motion(default_robot.motion): 

    def __init__(self):
        super().__init__()
        self.fileExtension = "_lmarks" 
        self.width  = 960
        self.height = 540
        self.name= "Virtual Robot (" + str(os.getpid()) + ")"
        thread_show = threading.Thread(target=self.showStickman)
        thread_show.start()
            
    def convert_landmarks(self,landmarks_list) :
        landmarks=LandmarkList()
        row = np.array(landmarks_list).astype(float)
        row=np.reshape(row,(-1,4))
        for landmark_element in row:
            landmarks.landmark.add(x=landmark_element[0],y=landmark_element[1],z=landmark_element[2],visibility=landmark_element[3])
        return landmarks 

    def showStickman(self):
        self.stickman_image = np.zeros((self.height,self.width,3),dtype='uint8')
        #self.stickman_image = self.stickman_image[0:self.height, int(self.width*0.2):int(self.width*0.8)]
        self.window= cv.namedWindow(self.name,flags=cv.WINDOW_NORMAL) 
        cv.moveWindow(self.name,0,0)
        cv.resizeWindow(self.name,self.width,self.height)
        while True and self.stop_motion==False:
            cv.imshow(self.name, self.stickman_image)
            #cv.setWindowProperty(self.name, cv.WND_PROP_TOPMOST,1)
            if cv.waitKey(40) == ord('q'):
                exit()

    def stop(self):
        self.stop_motion=True

    def move(self,pose_landmarks_list):
        pose_landmarks = self.convert_landmarks(pose_landmarks_list)
        self.stickman_image = np.zeros((self.height,self.width,3),dtype='uint8')
        self.stickman_image = draw_landmarks(self.stickman_image, pose_landmarks)
        #self.stickman_image = self.stickman_image[0:self.height, int(self.width*0.2):int(self.width*0.8)]

    def terminate(self):
        pass
        #cv.destroyAllWindows()

class speech(default_robot.speech):
    pass

class vision(default_robot.vision):
    pass

class sound(default_robot.sound) :
    pass
