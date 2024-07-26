#!/usr/bin/env python
# -*- coding: utf-8 -*-

import subprocess
import os
import sys
import cv2 as cv
import sounddevice as sd
if sys.version_info[0]==2 and sys.version_info[1]==7 :
    import Queue as queue
else:
    import queue
#import sobotify.commons.speak 
import ast
import platform

class robot(object): 

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
   
class motion(object): 

    def __init__(self):
        self.fileExtension = "_lmarks" 
        self.stop_motion=False
            
    def getFileExtension(self):
        return self.fileExtension

    def stop(self):
        self.stop_motion=True

    def move(self):
        pass

    def follow_head(self,data):
        head_data=ast.literal_eval(data)
        offset_x=head_data.get("offset_x",0)
        offset_y=head_data.get("offset_y",0)
        img_width=head_data.get("img_width",640)
        img_height=head_data.get("img_height",480)

        #angle_x,angle_y=angles(offset_x,offset_y)
        print ("offsetx="+str(offset_x))
        print ("offsety="+str(offset_y))

    def search_head(self):
        pass
        #print ("search head")

    def terminate(self):
        pass

class speech(object):

    def __init__(self):
        self.language="English"
        self.speed=100
        
    def setLanguage(self, language):
        self.language=language

    def setSpeed(self, speed):
        self.speed=speed
        
    def say(self, Text):
        sobotify_path=os.path.dirname(os.path.abspath(__file__))
        script_path=os.path.join(sobotify_path,'..','commons','speak.py')
        arguments=[sys.executable,script_path]
        #arguments=[sys.executable,sobotify.commons.speak.__file__]
        arguments.extend(('--language',self.language))
        arguments.extend(('--message',"\"" + Text +"\""))
        arguments.extend(('--speed',str(self.speed)))
        result=subprocess.call(arguments)    
        
    def terminate(self):
        # maybe check if say command terminated (or kill the process)
        pass

class vision(object):

    def __init__(self,device) : 
        if device.isnumeric():
            if platform.system()=="Windows":  
                self.cam = cv.VideoCapture(int(device),cv.CAP_DSHOW)
            else:
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

"""
Attribution: The following code is based on 
https://github.com/alphacep/vosk-api/blob/master/python/example/test_microphone.py
(Apache 2.0 Licensed)
"""    
class sound(object) :

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
            print (sys.version)
            if (sys.version_info[0]==2 and sys.version_info[1]==7) :
                print(status)
            else:
                #print(status, file=sys.stderr)
                print(status)
        self.audioqueue.put(bytes(indata))

    def get_audio_data(self) :
        try:
            return True,self.audioqueue.get()
        except:
            return False,None

    def get_samplerate(self) :
        return self.samplerate

    def terminate(self):
        self.stop_streaming()