#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Attribution: Part of this code is based on 
https://github.com/Kazuhito00/mediapipe-python-sample/blob/main/sample_pose.py
https://github.com/elggem/naoqi-pose-retargeting/blob/main/teleop.py
(Apache 2.0 Licensed)
"""
from naoqi import ALProxy
#from ALProxy_dummy import ALProxy

limitsLShoulderPitch = [-2.0857, 2.0857]
#limitsLShoulderRoll  = [-0.3142, 1.3265]  
limitsLShoulderRoll  = [0, 1.3265]  
limitsLElbowYaw      = [-2.0857, 2.0857]
limitsLElbowRoll     = [-1.5446, -0.0349]

limitsRShoulderPitch = [-2.0857, 2.0857]
#limitsRShoulderRoll  = [-1.3265, 0.3142]
limitsRShoulderRoll  = [-1.3265, 0]
limitsRElbowYaw      = [-2.0857, 2.0857]
limitsRElbowRoll     = [ 0.0349, 1.5446]

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


class motion(): 

    def __init__(self,robot_ip):
        self.fileExtension = "_nao" 
        try: 
            self.motion =  ALProxy("ALMotion", robot_ip, 9559)
            self.posture = ALProxy("ALRobotPosture", robot_ip, 9559)
        except Exception : 
            print ("Cannot connect to Nao robot at IP address: "+str(robot_ip))
            exit()  
        
        # Wake up robot
        self.motion.wakeUp()
        
        self.posture.goToPosture("Stand", 0.5)

        self.motion.setStiffnesses("Head", 1.0)
        
        # Speed limits for the joints
        self.fractionMaxSpeed = 0.15  # 0.15 was
        
        # move hands
        #self.motion.setStiffnesses("LWristYaw", 1.0)
        #self.motion.setStiffnesses("RWristYaw", 1.0)
        #names  = ["LWristYaw","RWristYaw"]
        #angles  = [1.8,-1.8]
        #self.motion.setAngles(names, angles, self.fractionMaxSpeed)
        
        # Set stiffness of the interested joint
        stiffness = 1
        self.motion.setStiffnesses("LShoulderPitch", stiffness)
        self.motion.setStiffnesses("LShoulderRoll",  stiffness)
        self.motion.setStiffnesses("LElbowYaw", stiffness)
        self.motion.setStiffnesses("LElbowRoll", stiffness)
        self.motion.setStiffnesses("RShoulderPitch", stiffness)
        self.motion.setStiffnesses("RShoulderRoll", stiffness)
        self.motion.setStiffnesses("RElbowYaw", stiffness)
        self.motion.setStiffnesses("RElbowRoll", stiffness)
        #self.motion.setStiffnesses("HipPitch", stiffness)
        
        # Example showing how to activate "Arms" anticollision
        chainName = "Arms"
        enable  = True
        isSuccess = self.motion.setCollisionProtectionEnabled(chainName, enable)
        print ("Anticollision activation on arms: " + str(isSuccess))
        
    def getFileExtension(self):
        return self.fileExtension
        
    def move(self,line):
        names = ["LShoulderPitch","LShoulderRoll", "LElbowYaw", "LElbowRoll", \
                 "RShoulderPitch","RShoulderRoll", "RElbowYaw", "RElbowRoll"]
        
        angles = [float(line[0]), float(line[1]), float(line[2]), float(line[3]), \
                float(line[4]), float(line[5]), float(line[6]), float(line[7])]
        if angles_in_range(angles) :
            self.motion.setAngles(names, angles, self.fractionMaxSpeed)
            
    def terminate(self):
        self.posture.goToPosture("Stand", 0.5)

def convert_to_ascii(text):
    text=text.decode("utf-8","ignore")
    text=text.replace(U"\u00E4","ae")
    text=text.replace(U"\u00C4","Ae")
    text=text.replace(U"\u00F6","oe")
    text=text.replace(U"\u00D6","Oe")
    text=text.replace(U"\u00FC","ue")
    text=text.replace(U"\u00DC","Ue")
    text=text.replace(U"\u00DF","ss")
    text= text.encode(encoding="ASCII",errors="ignore")
    return text

class speech():

    def __init__(self,robot_ip):
        self.language="English"
        self.speed=100
        try: 
            self.speech = ALProxy("ALTextToSpeech", robot_ip, 9559)
        except Exception : 
            print ("Cannot connect to Nao robot at IP address: "+str(robot_ip))
            exit() 
        self.speech.setLanguage(self.language)
        self.speech.setParameter("speed", self.speed)
        
    def setLanguage(self, language):
        self.language=language.capitalize()
        self.speech.setLanguage(self.language)

    def setSpeed(self, speed):
        self.speed=speed
        self.speech.setParameter("speed", self.speed)

    def say(self, Text):
        self.text=convert_to_ascii(Text)
        print("Nao says:" + self.text)
        self.speech.say(str(self.text))		    
        
    def terminate(self):
        # maybe check if say command terminated (or kill the process)
        pass
