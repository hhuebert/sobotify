#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Attribution: Part of this code is based on 
https://github.com/Kazuhito00/mediapipe-python-sample/blob/main/sample_pose.py
(Apache 2.0 Licensed)
"""
import pybullet as p
from qibullet import SimulationManager
import sobotify.robots.robot as default_robot

class PepperSim(): 

    def __init__(self,robot_ip,cam_device,sound_device):
        self.motion=motion()
        self.speech=speech()
        self.vision=vision(cam_device)
        self.sound=sound(sound_device)

    def terminate(self):
        self.motion.terminate()
        self.speech.terminate()
        self.vision.terminate()
        self.sound.terminate()

limitsLShoulderPitch = [-2.0857, 2.0857]
limitsLShoulderRoll  = [ 0.0087, 1.5620]
limitsLElbowYaw      = [-2.0857, 2.0857]
limitsLElbowRoll     = [-1.5620,-0.0087]

limitsRShoulderPitch = [-2.0857, 2.0857]
limitsRShoulderRoll  = [-1.5620,-0.0087]
limitsRElbowYaw      = [-2.0857, 2.0857]
limitsRElbowRoll     = [ 0.0087, 1.5620]
limitsHipPitch       = [-1.0385, 1.0385]

def out_of_limit(val, limits):
    return val < limits[0] or val > limits[1]

def angles_in_range(angles) :
    angles_ok=True
    if (out_of_limit(angles[0], limitsLShoulderPitch) or 
        out_of_limit(angles[1], limitsLShoulderRoll) or
        out_of_limit(angles[2], limitsLElbowYaw) or 
        out_of_limit(angles[3], limitsLElbowRoll) or
        out_of_limit(angles[4], limitsRShoulderPitch) or 
        out_of_limit(angles[5], limitsRShoulderRoll) or
        out_of_limit(angles[6], limitsRElbowYaw) or 
        out_of_limit(angles[7], limitsRElbowRoll)):
        print ("error: angle out of limit")
        angles_ok=False
    return angles_ok


class motion(default_robot.motion): 

    def __init__(self):
        super().__init__()
        self.fileExtension = "_pepper" 
        # Auto stepping set to False, the user has to manually step the simulation
        self.simulation_manager = SimulationManager()
        self.client = self.simulation_manager.launchSimulation(gui=True, auto_step=False)
        p.resetDebugVisualizerCamera( cameraDistance=0.8, cameraYaw=90, cameraPitch=-20, cameraTargetPosition=[0,0,0.7])
        p.configureDebugVisualizer(p.COV_ENABLE_GUI,0)
        p.configureDebugVisualizer(p.COV_ENABLE_WIREFRAME,0)
        p.configureDebugVisualizer(p.COV_ENABLE_SHADOWS,0)
        self.motion = self.simulation_manager.spawnPepper(self.client, spawn_ground_plane=True)  
        self.posture = self.motion		
        self.posture.goToPosture("StandInit", 0.5)     
        # Speed limits for the joints
        self.fractionMaxSpeed = 0.15  # 0.15 was
            
    def getFileExtension(self):
        return self.fileExtension

    def move(self,line):
        names = ["LShoulderPitch","LShoulderRoll", "LElbowYaw", "LElbowRoll", \
                 "RShoulderPitch","RShoulderRoll", "RElbowYaw", "RElbowRoll", \
                 "HipPitch"]
        angles = [float(line[0]), float(line[1]), float(line[2]), float(line[3]), \
                float(line[4]), float(line[5]), float(line[6]), float(line[7]), float(0)]
        if angles_in_range(angles) :
            # time.sleep did't not work, therefore for loop as a simple replacement
            # should be fixed  
            #for i in range(50) :
            #    print (i)
            self.motion.setAngles(names, angles, self.fractionMaxSpeed)
            # Step the simulation
            self.simulation_manager.stepSimulation(self.client)            

    def terminate(self):
        pass


class speech(default_robot.vision):
        
    def say(self, Text):
        arg1 = self.language
        arg2 = str(self.speed) 
        arg3 = "\"" + Text +"\""
        DisplayText=Text
        DisplayText= ' '.join(DisplayText.splitlines())
        #DisplayText=DisplayText.replace('\n',' ')
        #DisplayText=DisplayText.replace('\r',' ')
        #DisplayText=DisplayText.replace('\t',' ')
        #DisplayText=DisplayText.replace('\"',' ')
        #id1 = p.addUserDebugText(text=Text[0:100], textSize=1.4, lifeTime=30, textPosition=[0.2,-0.54,1.15])
        #id2 = p.addUserDebugText(text=Text[100:200], textSize=1.4, lifeTime=30, textPosition=[0.2,-0.56,1.1])
        #id3 = p.addUserDebugText(text=Text[200:300], textSize=1.4, lifeTime=30, textPosition=[0.2,-0.58,1.05])
        #id4 = p.addUserDebugText(text=Text[300:400], textSize=1.4, lifeTime=30, textPosition=[0.2,-0.60,1])
        #id5 = p.addUserDebugText(text=Text[400:500], textSize=1.4, lifeTime=30, textPosition=[0.2,-0.62,0.95])
        #id6 = p.addUserDebugText(text=Text[500:600], textSize=1.4, lifeTime=30, textPosition=[0.2,-0.64,0.90])
        offset=0.05
        id1 = p.addUserDebugText(text=DisplayText[0:100], textColorRGB=[1,0,0], textSize=1.4, lifeTime=30, textPosition=[0.2,-0.95+offset,0.48])
        id2 = p.addUserDebugText(text=DisplayText[100:200], textColorRGB=[1,0,0], textSize=1.4, lifeTime=30, textPosition=[0.2,-0.99+offset,0.40])
        id3 = p.addUserDebugText(text=DisplayText[200:300], textColorRGB=[1,0,0], textSize=1.4, lifeTime=30, textPosition=[0.2,-1.03+offset,0.32])
        id4 = p.addUserDebugText(text=DisplayText[300:400], textColorRGB=[1,0,0], textSize=1.4, lifeTime=30, textPosition=[0.2,-1.07+offset,0.24])
        id5 = p.addUserDebugText(text=DisplayText[400:500], textColorRGB=[1,0,0], textSize=1.4, lifeTime=30, textPosition=[0.2,-1.11+offset,0.16])
        id6 = p.addUserDebugText(text=DisplayText[500:600], textColorRGB=[1,0,0], textSize=1.4, lifeTime=30, textPosition=[0.2,-1.15+offset,0.08])

        super().say(Text) 

        p.removeUserDebugItem(id1)
        p.removeUserDebugItem(id2)
        p.removeUserDebugItem(id3)
        p.removeUserDebugItem(id4)
        p.removeUserDebugItem(id5)
        p.removeUserDebugItem(id6)
        #result=subprocess.call("start python.exe speak.py "+arg1+" "+arg2+" "+arg3, shell=True)
        print (DisplayText)

class PepperSpeech_new():

    def __init__(self):
        self.engine = pyttsx3.init()
        self.engine.setProperty('voice', "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\TTS_MS_DE-DE_HEDDA_11.0")
        self.engine.setProperty('rate',100);
        self.voices = self.engine.getProperty('voices')
        
        self.language="German"
        self.speed=100
        
    def setLanguage(self, language):
        if language.lower()=="german":
            self.engine.setProperty('voice', "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\TTS_MS_DE-DE_HEDDA_11.0")
            #print ("set language to : " + language_string)     


    def setSpeed(self, speed):
        speed=2*speed;
        self.engine.setProperty('rate',speed);
        #print ("set speed to : " + str(speed))    
        
    def say(self, Text):
        #arg1 = self.language
        #arg2 = str(self.speed) 
        #arg3 = "\"" + Text +"\""
        
        #print ("say : "+Text)
        self.engine.say(Text)
        self.engine.runAndWait()
        #print ("done: "+Text)
        
    def terminate(self):
        # maybe check if say command terminated (or kill the process)
        pass


class vision(default_robot.vision):
    pass

class sound(default_robot.sound):
    pass