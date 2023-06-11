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
