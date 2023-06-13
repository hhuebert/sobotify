#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Attribution: Part of this code is based on 
https://github.com/adanali3801/pycozmo
(MIT Licensed)
"""
import os
import threading
import time
from PIL import Image
import cv2 as cv
import numpy as np
import pycozmo
import pyttsx3
from signal import signal, SIGINT
from datetime import datetime

def text_to_audiofile(text:str, filename='temp_text_to_audio'):
    text_to_audio_engine = pyttsx3.init()
    text_to_audio_engine.setProperty('voice', "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\TTS_MS_EN-US_ZIRA_11.0")
    #text_to_audio_engine.setProperty('voice', "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\TTS_MS_DE-DE_HEDDA_11.0")      
    text_to_audio_engine.save_to_file(text, filename+'.wav')
    text_to_audio_engine.runAndWait()
    return filename+'.wav'

class cozmo:

    def __init__(self):
        self.fileExtension = "_cozmo" 
        # Initialize Cozmo with pycozmo
        self.tts_engine = pyttsx3.init()
        self.setLanguage("english")
        self.image_available=False

        self.stop_movement=threading.Event()
        self.stop_movement.clear()
        self.cli = pycozmo.Client()
        self.cli.start()
        self.cli.connect()
        self.cli.wait_for_robot()
        self.cli.set_head_angle(angle=0.6)
        # Enable camera
        self.cli.enable_camera(enable=True, color=False)
        # Set volume
        self.cli.set_volume(65535)
        self.img=None

    def getFileExtension(self):
        return self.fileExtension

    def setLanguage(self, language):
        pass
        if language.lower()=="english":
            self.tts_engine.setProperty('voice', "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\TTS_MS_EN-US_ZIRA_11.0")
        if language.lower()=="german":
            self.tts_engine.setProperty('voice', "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\TTS_MS_DE-DE_HEDDA_11.0")      

    def setSpeed(self, speed):
        pass
        #self.speed=speed
        #self.speech.setParameter("speed", self.speed)

    def move(self,line):
        print (line)
        if float(line[0])==1.0:
            print("MAX")
            self.cli.set_lift_height(pycozmo.MAX_LIFT_HEIGHT.mm)
        else:
            print("MIN")
            self.cli.set_lift_height(pycozmo.MIN_LIFT_HEIGHT.mm)

    def say(self,Text):
        filename="temp_text_to_audio.wav"
        self.tts_engine.save_to_file(Text, filename)
        self.tts_engine.runAndWait()
        self.cli.play_audio(filename)
        self.cli.wait_for(pycozmo.event.EvtAudioCompleted)
        if os.path.exists(filename):
            os.remove(filename)
        else:
            print("The file does not exist")

    def on_camera_image(self,cli, image):
        npa=np.array(image)
        self.img=cv.cvtColor(npa,cv.COLOR_RGB2BGR)
        self.image_available=True

    def get_image(self):
        self.image_available=False
        self.cli.add_handler(pycozmo.event.EvtNewRawCameraImage, self.on_camera_image, one_shot=True)
        while not self.image_available:
            time.sleep(0.1)
            print("waiting for image")
        return True,self.img

    def show_expression(self,expression: any):
        # Base face expression.
        base_face = pycozmo.expressions.Neutral()
        rate = pycozmo.robot.FRAME_RATE
        timer = pycozmo.util.FPSTimer(rate)
        # Transition from base face to expression and back.
        for from_face, to_face in ((base_face, expression), (expression, base_face)):

            if to_face != base_face:
                print(to_face.__class__.__name__)

            # Generate transition frames.
            face_generator = pycozmo.procedural_face.interpolate(from_face, to_face, rate // 3)
            for face in face_generator:

                # Render face image.
                im = face.render()

                # The Cozmo protocol expects a 128x32 image, so take only the even lines.
                np_im = np.array(im)
                np_im2 = np_im[::2]
                im2 = Image.fromarray(np_im2)

                # Display face image.
                self.cli.display_image(im2)

                # Maintain frame rate.
                timer.sleep()
                
            # Pause for X*s.
            for i in range(rate):
                timer.sleep()

    def terminate(self):
        self.cli.set_lift_height(pycozmo.MIN_LIFT_HEIGHT.mm)

    def terminate2(self):
        self.cli.set_lift_height(pycozmo.MIN_LIFT_HEIGHT.mm)
        time.sleep(2)
        self.cli.disconnect()
        self.cli.stop()
