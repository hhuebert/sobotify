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
from sobotify.commons.external.utils import draw_landmarks
import sobotify.commons.speak 

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
   
class motion(): 

    def __init__(self):
        self.fileExtension = "_lmarks" 
        self.width  = 960
        self.height = 540
        self.name= "Virtual Robot (" + str(os.getpid()) + ")"
            
    def getFileExtension(self):
        return self.fileExtension

    def convert_landmarks(self,landmarks_list) :
        landmarks=LandmarkList()
        row = np.array(landmarks_list).astype(float)
        row=np.reshape(row,(-1,4))
        for landmark_element in row:
            landmarks.landmark.add(x=landmark_element[0],y=landmark_element[1],z=landmark_element[2],visibility=landmark_element[3])
        return landmarks 

    def move(self,pose_landmarks_list):
        pose_landmarks = self.convert_landmarks(pose_landmarks_list)
        stickman_image = np.zeros((self.height,self.width,3),dtype='uint8')
        stickman_image = draw_landmarks(stickman_image, pose_landmarks)
        stickman_image = stickman_image[0:self.height, int(self.width*0.2):int(self.width*0.8)]
        cv.imshow(self.name, stickman_image)
        cv.setWindowProperty(self.name, cv.WND_PROP_TOPMOST,1)
        if cv.waitKey(1) == ord('q'):
            exit()
            
    def terminate(self):
       cv.destroyAllWindows()

class speech():

    def __init__(self):
        self.language="German"
        self.speed=100
        
    def setLanguage(self, language):
        self.language=language

    def setSpeed(self, speed):
        self.speed=speed
        
    def say(self, Text):
        
        arguments=[sys.executable,sobotify.commons.speak.__file__]
        arguments.extend(('--language',self.language))
        arguments.extend(('--message',"\"" + Text +"\""))
        arguments.extend(('--speed',str(self.speed)))
        result=subprocess.call(arguments)    
        
    def terminate(self):
        # maybe check if say command terminated (or kill the process)
        pass

class vision():

    def __init__(self,device) : 
        if device.isnumeric():
            self.cam = cv.VideoCapture(int(device))
        else:
            self.cam = cv.VideoCapture(device)
        if not self.cam.isOpened():
            print ("Error opening Camera")

    def get_image(self) : 
        if self.cam.isOpened():
            ret,img=self.cam.read()
            if not ret:
                print ("Couldn't get image")

        return ret,img
    
    def terminate(self):
        self.cam.release()
        pass    