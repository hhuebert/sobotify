#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Attribution: Part of this code is based on 
https://github.com/adanali3801/pycozmo
(MIT Licensed)
and the examples from here:
https://github.com/zayfod/pycozmo
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
import threading
import ast

min_offset_x=0.2
min_offset_y=0.2

temp_audio_file=os.path.join(os.path.expanduser("~"),".sobotify","temp_audio_file.wav")

class cozmo:

    def __init__(self):
        self.fileExtension = "_cozmo" 
        # Initialize Cozmo with pycozmo
        self.tts_engine = pyttsx3.init()
        self.setLanguage("english")
        self.image_available=False
        self.update_robot_state=False
        self.lift_angle=pycozmo.MIN_HEAD_ANGLE.radians
        self.head_angle=pycozmo.MIN_LIFT_HEIGHT.mm
        self.next_face="neutral"
        self.last_face="neutral"
        self.step = 1
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
        self.drive(duration=3)
        self.img=None
        print (f"battery voltage = {self.get_battery_state()}")

    def on_robot_state(self,cli, pkt: pycozmo.protocol_encoder.RobotState):
        self.update_robot_state=True
        self.current_head_angle = pkt.head_angle_rad
        self.current_battery_voltage = pkt.battery_voltage
        #print (f"current angle={pkt.head_angle_rad}")

    def get_head_angle(self):
        self.update_robot_state=False
        self.cli.add_handler(pycozmo.protocol_encoder.RobotState, self.on_robot_state, one_shot=True)
        while not self.update_robot_state == True:
            time.sleep(0.1)
            print("waiting for angle update")
        return self.current_head_angle

    def get_battery_state(self):
        self.update_robot_state=False
        self.cli.add_handler(pycozmo.protocol_encoder.RobotState, self.on_robot_state, one_shot=True)
        while not self.update_robot_state == True:
            time.sleep(0.1)
            print("waiting for batery voltage state update")
        return self.current_battery_voltage

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
        
    def set_head_angle(self, angle):
        self.cli.set_head_angle(angle=angle)

    def drive(self, duration:float, speed:float = 50) -> None:
        self.cli.drive_wheels(lwheel_speed=speed, rwheel_speed=speed, duration=duration)
        
    def turn_right(self, duration:float, speed:float = 50) -> None:
        self.cli.drive_wheels(lwheel_speed=speed, rwheel_speed=-speed, duration=duration)
    
    def turn_left(self, duration:float, speed:float = 50) -> None:
        self.cli.drive_wheels(lwheel_speed=-speed, rwheel_speed=speed, duration=duration)

    def follow_head(self,data):
        self.step = 1
        head_data=ast.literal_eval(data)
        offset_x=head_data.get("offset_x",0)
        offset_y=head_data.get("offset_y",0)
        #img_width=head_data.get("img_width",640)
        #img_height=head_data.get("img_height",480)
        if offset_x>min_offset_x :
            self.turn_right(0.1)
        elif offset_x<-min_offset_x :
            self.turn_left(0.1)

        if offset_y>min_offset_y :
            self.set_head_angle(self.get_head_angle()-0.1)
        elif offset_y<-min_offset_y :
            self.set_head_angle(self.get_head_angle()+0.1)

    def search_head(self):
        if self.step == 1:
            print("Cozmo: Searching for a face.")
            self.turn_right(1.5, speed=20)
            time.sleep(1.2)
            self.step += 1
        elif self.step == 2:
            self.set_head_angle(0.4)
            time.sleep(1.2)
            self.step += 1
        elif self.step == 3:
            self.set_head_angle(0.8)
            time.sleep(1.2)
            self.step += 1
        elif self.step == 4:
            self.turn_left(1.5, speed=20)
            time.sleep(1.2)
            self.step += 1
        elif self.step == 5:
            self.set_head_angle(0.4)
            time.sleep(1.2)
            self.step += 1
        elif self.step == 6:
            self.set_head_angle(0.8)
            self.step += 1
        elif self.step == 7:
            self.turn_left(1.5, speed=20)
            time.sleep(1.2)
            self.step += 1
        elif self.step == 8:
            self.set_head_angle(0.4)
            time.sleep(1.2)
            self.step += 1
        elif self.step == 9:
            self.set_head_angle(0.8)
            self.step += 1
        elif self.step == 10:
            self.step += 1
            self.turn_right(1.5, speed=20)
            time.sleep(1.2)
        elif self.step == 11:
            self.set_head_angle(0.4)
            time.sleep(1.2)
            self.step += 1
        elif self.step == 12:
            self.set_head_angle(0.8)
            time.sleep(1.2)
            self.step = 1

    def move_head(self):
        self.cli.set_head_angle(self.head_angle)

    def move_lift(self):
        self.cli.set_lift_height(self.lift_angle)

    def move_wheels(self):
        if self.wheel_angle<0:
            self.turn_right(abs(self.wheel_angle))
        else:
            self.turn_left(abs(self.wheel_angle))

    def move(self,line):     
        self.lift_angle=float(line[0])
        self.head_angle=float(line[1])
        self.wheel_angle=float(line[2])
        self.next_face=line[3].strip()
        #self.move_head()
        #self.move_lift()
        thread_move_head = threading.Thread(target=self.move_head)
        thread_move_lift = threading.Thread(target=self.move_lift)
        thread_move_wheels = threading.Thread(target=self.move_wheels)
        thread_show_expression = threading.Thread(target=self.show_expression)
        thread_move_head.start()
        thread_move_lift.start()
        thread_move_wheels.start()
        thread_show_expression.start()
        thread_move_head.join()
        thread_move_lift.join()
        thread_move_wheels.join()
        thread_show_expression.join()

    def say(self,Text):
        self.tts_engine.save_to_file(Text, temp_audio_file)
        self.tts_engine.runAndWait()
        self.cli.play_audio(temp_audio_file)
        self.cli.wait_for(pycozmo.event.EvtAudioCompleted)
        if os.path.exists(temp_audio_file):
            os.remove(temp_audio_file)
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

    def show_expression(self):
        if not self.next_face or self.next_face==self.last_face:
            return
        print (f"change expression to {self.next_face}")
        # List of face expressions.
        expressions = {
            "neutral"        : pycozmo.expressions.Neutral(),
            "anger"          : pycozmo.expressions.Anger(),
            "sadness"        : pycozmo.expressions.Sadness(),
            "happiness"      : pycozmo.expressions.Happiness(),
            "surprise"       : pycozmo.expressions.Surprise(),
            "disgust"        : pycozmo.expressions.Disgust(),
            "fear"           : pycozmo.expressions.Fear(),
            "pleading"       : pycozmo.expressions.Pleading(),
            "vulnerability"  : pycozmo.expressions.Vulnerability(),
            "despair"        : pycozmo.expressions.Despair(),
            "guilt"          : pycozmo.expressions.Guilt(),
            "disappointment" : pycozmo.expressions.Disappointment(),
            "embarrassment"  : pycozmo.expressions.Embarrassment(),
            "horror"         : pycozmo.expressions.Horror(),
            "skepticism"     : pycozmo.expressions.Skepticism(),
            "annoyance"      : pycozmo.expressions.Annoyance(),
            "fury"           : pycozmo.expressions.Fury(),
            "suspicion"      : pycozmo.expressions.Suspicion(),
            "rejection"      : pycozmo.expressions.Rejection(),
            "boredom"        : pycozmo.expressions.Boredom(),
            "tiredness"      : pycozmo.expressions.Tiredness(),
            "asleep"         : pycozmo.expressions.Asleep(),
            "confusion"      : pycozmo.expressions.Confusion(),
            "amazement"      : pycozmo.expressions.Amazement(),
            "excitement"     : pycozmo.expressions.Excitement(),
        }

        rate = pycozmo.robot.FRAME_RATE
        timer = pycozmo.util.FPSTimer(rate)
        last_expression=expressions.get(self.last_face.lower(),pycozmo.expressions.Neutral())
        next_expression=expressions.get(self.next_face.lower(),pycozmo.expressions.Neutral())

        # Generate transition frames.
        face_generator = pycozmo.procedural_face.interpolate(last_expression, next_expression, rate // 3)
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

        self.last_face=self.next_face

    def terminate(self):
        self.cli.set_lift_height(pycozmo.MIN_LIFT_HEIGHT.mm)
        if os.path.exists(temp_audio_file):
            os.remove(temp_audio_file)
        else:
            print("The file does not exist")

    def terminate2(self):
        self.cli.set_lift_height(pycozmo.MIN_LIFT_HEIGHT.mm)
        time.sleep(2)
        self.cli.disconnect()
        self.cli.stop()
        if os.path.exists(temp_audio_file):
            os.remove(temp_audio_file)
        else:
            print("The file does not exist")
