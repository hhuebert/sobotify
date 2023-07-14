#!/usr/bin/env python
# -*- coding: utf-8 -*-


import subprocess
import serial
import sys
import os
import numpy as np
import cv2 as cv
import sobotify.commons.speak 
import time
import ast
import math

min_angle_Yaw=-2.0857
max_angle_Yaw=2.0857

min_angle_Pitch=-0.330041
max_angle_Pitch=0.200015

min_offset_x=0.1
min_offset_y=0.1

hor_fov=57.2
ver_fov=44.3

def head_angles_in_range(angle_Yaw,angle_Pitch):
    # add code here
    if (angle_Yaw<min_angle_Yaw) or angle_Yaw>max_angle_Yaw:
        return False
    if (angle_Pitch<min_angle_Pitch) or angle_Pitch>max_angle_Pitch:
        return False    
    return True

r_hor=1/math.sin(hor_fov/2/180*math.pi)
r_ver=1/math.sin(ver_fov/2/180*math.pi)

def get_angles(offset_x,offset_y):
    angle_x=round(math.asin(offset_x/r_hor),2)
    angle_y=round(math.asin(offset_y/r_ver),2)
    return angle_x,angle_y


class motion(): 

    def __init__(self):
        self.fileExtension = "_mykeepon" 
        self.myKeepOn=serial.Serial('COM10',115200,timeout=1)
        message=self.myKeepOn.readline()
        print(message)
        message=self.myKeepOn.readline()
        print(message)
        message=self.myKeepOn.readline()
        print(message)
        message=self.myKeepOn.readline()
        print(message)
        message=self.myKeepOn.readline()
        print(message)
        message=self.myKeepOn.readline()
        print(message)
        message=self.myKeepOn.readline()
        print(message)
        message=self.myKeepOn.readline()
        print(message)
        message=self.myKeepOn.readline()
        print(message)
        message=self.myKeepOn.readline()
        print(message)
        message=self.myKeepOn.readline()
        print(message)
        self.myKeepOn.write(b"d")
        time.sleep(0.5)
        self.myKeepOn.write(b"e")
        time.sleep(0.5)
            
    def follow_head(self,data):
        head_data=ast.literal_eval(data)
        offset_x=head_data.get("offset_x",0)
        offset_y=head_data.get("offset_y",0)
        if offset_x>min_offset_x or offset_y>min_offset_y:
            img_width=head_data.get("img_width",640)
            img_height=head_data.get("img_height",480)

            angle_diff_x,angle_diff_y=get_angles(offset_x,offset_y)
            if angle_diff_x<0 :
                #pan_left()
                pass
            else :
                #pan_right()
               pass
            if angle_diff_y<0 :
                #pan_down()
                pass
            else :
                #pan_up()
               pass

    def search_head(self):
        print ("search head")


    def getFileExtension(self):
        return self.fileExtension

    def move(self,line):
        self.myKeepOn.write(bytes(line[0],"ascii"))
            
    def terminate(self):
        pass
        #self.myKeepOn.close()

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