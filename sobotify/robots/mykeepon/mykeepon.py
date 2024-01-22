#!/usr/bin/env python
# -*- coding: utf-8 -*-


import subprocess
import serial
import sys
import os
import numpy as np
import cv2 as cv
import sounddevice as sd
import queue
import sobotify.commons.speak 
import time
import ast
import math
import platform

min_angle_Yaw=-2.0857
max_angle_Yaw=2.0857

min_angle_Pitch=-0.330041
max_angle_Pitch=0.200015

min_offset_x=0.1
min_offset_y=0.1

hor_fov=57.2
ver_fov=44.3

min_pan=-100
max_pan=+100
min_tilt=-100
max_tilt=+100
SIDE_COMMANDS=["LEFT","CENTERFROMLEFT","RIGHT","CENTERFROMRIGHT"];
PON_COMMANDS=["UP","HALFUP","HALFDOWN","DOWN"];

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

    def __init__(self,PORT):
        self.fileExtension = "_mykeepon" 
        self.myKeepOn=serial.Serial(PORT,115200,timeout=1)
        self.pan_pos=0
        self.tilt_pos=0
        self.side_pos="CENTERFROMLEFT"       
        self.pon_pos="DOWN"

    def follow_head(self,data):
        # skip head following for now (to be implemented later)
        pass
        """
        head_data=ast.literal_eval(data)
        offset_x=head_data.get("offset_x",0)
        offset_y=head_data.get("offset_y",0)
        if offset_x>min_offset_x or offset_y>min_offset_y:

            ## with camera on robot head
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
                self.tilt(self.tilt_pos-10)
                pass
            else :
                self.tilt(self.tilt_pos+10)
                pass

            ## with fixed camera behind robot
            if offset_x<0 :
                #self.pan(int(+30*offset_x))
                pass
            else :
                #self.pan(int(-30*offset_x))
                pass
            if offset_y<0 :
                #self.tilt(int(+50*offset_y))
                pass
            else :
                #self.tilt(int(-50*offset_y))
                pass                
        """

    def search_head(self):
        print ("search head")


    def getFileExtension(self):
        return self.fileExtension

    def pan(self,val):
        command=("MOVE PAN "+str(val)+";").encode("ascii")
        if val>=min_pan and val<=max_pan:
            print (command)
            self.myKeepOn.write(command)
            print (command,"done")
            self.pan_pos=val
        else:
            print("ERROR:", command," invalid")
                
    def tilt(self,val):
        command=("MOVE TILT "+str(val)+";").encode("ascii")
        if val>=min_tilt and val<=max_tilt:
            print (command)
            self.myKeepOn.write(command)
            print (command,"done")
            self.tilt_pos=val
        else:
            print("ERROR:", command," invalid")

    def side(self,val):
        command=("MOVE SIDE "+val+";").encode("ascii")
        if val in SIDE_COMMANDS:
            print (command)
            self.myKeepOn.write(command)
            print (command,"done")
            self.side_pos=val
        else:
            print("ERROR:", command," invalid")

    def pon(self,val):
        command=("MOVE PON "+val+";").encode("ascii")
        if val in PON_COMMANDS:
            print (command)
            self.myKeepOn.write(command)
            print (command,"done")
            self.pon_pos=val
        else:
            print("ERROR:", command," invalid")

    def read_output(self):
        self.message=self.myKeepOn.readlines()
        print(self.message)
        

    def move(self,line):
        if line[0].strip():
            self.pan(float(line[0]))
            time.sleep(0.3)
        if line[1].strip():
            self.tilt(float(line[1]))
            time.sleep(0.4)
        if line[2].strip():
            self.side(line[2].strip().upper())
            time.sleep(0.3)
        if line[3].strip():
            self.pon(line[3].strip().upper())
            time.sleep(0.3)
            
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
            if platform.system()=="Windows":  
                self.cam = cv.VideoCapture(int(device),cv.CAP_DSHOW)
            else:
                self.cam = cv.VideoCapture(int(device))
        else:
            #self.cam = cv.VideoCapture("http://192.168.0.100:8080/video/mjpeg")
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

"""
Attribution: The following code is based on 
https://github.com/alphacep/vosk-api/blob/master/python/example/test_microphone.py
(Apache 2.0 Licensed)
"""    
## currently using computer/external microphone
class sound :

    def __init__(self,device=0) :
        self.device=int(device)
        try:
            device_info = sd.query_devices(self.device, "input")
        except ValueError:
            print(sd.query_devices())
            print("==========================================================")
            print ("Error: Could not open the selected input sound device : " +  str(self.device))
            print ("Choose a different device from the list above (must have inputs)")
        # get samplerate from audiodevice
        self.samplerate = int(device_info["default_samplerate"])
        #create queue for storing audio samples
        self.audioqueue = queue.Queue()
        self.streamer=None

    def start_streaming(self) :
        self.streamer=sd.RawInputStream(samplerate=self.samplerate, blocksize = 8000, device=self.device,
                dtype="int16", channels=1, callback=self.audio_callback)
        self.streamer.__enter__()
        return self.samplerate

    def stop_streaming(self) :
        if self.streamer is not None:
            self.streamer.__exit__()

    # this function is called from the sound device handler to store the audio block in the queue
    def audio_callback(self,indata, frames, time, status):
        """This is called (from a separate thread) for each audio block."""
        if status:
            print(status, file=sys.stderr)
        self.audioqueue.put(bytes(indata))

    def get_audio_data(self) :
        try:
            return True,self.audioqueue.get()
        except:
            return False,None

    def get_samplerate(self) :
        return self.samplerate    