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
import cv2 as cv
import vision_definitions
import numpy as np
from datetime import datetime
import random
import ast
import math
import time
from animations import NAO_animations,NAO_animation_tags

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

limitsRElbowYaw      = [-2.0857, 2.0857]
limitsRElbowRoll     = [ 0.0349, 1.5446]

# LShoulderPitch, LShoulderRoll, LElbowYaw, LElbowRoll, LWristYaw, LHand
LArms_crouch_angles= [1.4342480897903442, 0.14722204208374023, -0.8115279674530029, -1.0430779457092285, 0.13341593742370605, 0.01639997959136963]
# RShoulderPitch, RShoulderRoll, RElbowYaw, RElbowRoll, RWristYaw, RHand
RArms_crouch_angles= [1.4281959533691406, -0.14117002487182617, 0.8114440441131592, 1.0400938987731934, -0.12122797966003418, 0.016000032424926758]

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


#min_angle_Yaw=-2.0857
#max_angle_Yaw=2.0857
min_angle_Yaw=-1.0
max_angle_Yaw=1.0

min_angle_Pitch=-0.330041
max_angle_Pitch=0.200015

min_offset_x=0.2
min_offset_y=0.2

search_x=0.05


# according to camera specification
#hor_fov=56.3
#ver_fov=43.7
# according to measurments of the angles
hor_fov=45.0
ver_fov=33.0

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

    def __init__(self,robot_ip,robot_options):
        self.robot_options=robot_options
        print("robot options :"+str(self.robot_options)) 
        if "posture=crouch" in self.robot_options :
            self.posture_crouch=True
        else:
            self.posture_crouch=False
        self.fileExtension = "_nao" 
        self.last_extended_motion=datetime.now()
        self.search_angle_diff_x=search_x
        try: 
            self.motion =  ALProxy("ALMotion", robot_ip, 9559)
            self.posture = ALProxy("ALRobotPosture", robot_ip, 9559)
            self.naoqi_version=self.get_naoqi_version(robot_ip)
            if self.naoqi_version>=2.3:
                self.animation = ALProxy("ALAnimationPlayer", robot_ip, 9559)
            else :
                self.animation = None
        except Exception : 
            print ("Cannot connect to Nao robot at IP address: "+str(robot_ip))
            exit()  

        if self.posture_crouch==True:
            self.posture.goToPosture("Crouch", 0.5)
            self.motion.setStiffnesses("Body", 0.0)
            #self.motion.setStiffnesses("LLeg", 0.25)
            #self.motion.setStiffnesses("RLeg", 0.25)
            self.motion.setStiffnesses("LHipYawPitch", 0.25)
            self.motion.setStiffnesses("RHipYawPitch", 0.25)
            self.motion.setStiffnesses("LHipPitch", 0.25)
            self.motion.setStiffnesses("RHipPitch", 0.25)
        else:
            # Wake up robot
            self.motion.wakeUp()
            self.posture.goToPosture("Stand", 0.5)

        self.motion.setStiffnesses("Head", 1.0)

        self.last_found_head_angles=self.motion.getAngles("Head",True)

        # Speed limits for the joints
        self.fractionMaxSpeed = 0.15  # 0.15 was
                
        # Set stiffness of the interested joint
        self.set_arm_stiffness(1)
        
        # Example showing how to activate "Arms" anticollision
        chainName = "Arms"
        enable  = True
        isSuccess = self.motion.setCollisionProtectionEnabled(chainName, enable)
        print ("Anticollision activation on arms: " + str(isSuccess))
        
    def get_naoqi_version(self,robot_ip):
        system = ALProxy("ALSystem", robot_ip, 9559)
        version=system.systemVersion()
        print("robot's naoqi version = "+version)
        major_version= version.split(".")[0]
        minor_version=str("".join(version.split(".")[1:]))
        version_float=float(major_version+"."+minor_version)
        return version_float

    def set_arm_stiffness(self,stiffness):
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
        self.motion.setStiffnesses("LWristYaw", stiffness)
        self.motion.setStiffnesses("RWristYaw", stiffness)

    def getFileExtension(self):
        return self.fileExtension
        
    def follow_head(self,data):
        head_data=ast.literal_eval(data)
        offset_x=head_data.get("offset_x",0)
        offset_y=head_data.get("offset_y",0)
        if abs(offset_x)>min_offset_x or abs(offset_y)>min_offset_y:
            img_width=head_data.get("img_width",640)
            img_height=head_data.get("img_height",480)

            angle_diff_x,angle_diff_y=get_angles(offset_x,offset_y)
            print (angle_diff_x)
            print (angle_diff_y)
            current_angles=self.motion.getAngles("Head",True)
            current_angles_yaw=current_angles[0]
            current_angles_pitch=current_angles[1]
            print (current_angles)
            angle_Yaw=current_angles_yaw-angle_diff_x
            angle_Pitch=current_angles_pitch+angle_diff_y
            if head_angles_in_range(angle_Yaw,angle_Pitch):
                print ("angle ok")
                fractionMaxSpeed  = 0.1
                names  = ["HeadYaw", "HeadPitch"]
                angles = [angle_Yaw,angle_Pitch]
                self.motion.setAngles(names, angles, fractionMaxSpeed)
                self.last_found_head_angles=self.motion.getAngles("Head",True)
            else:    
                print ("angle out of range")


    def search_head(self):
        current_angles=self.motion.getAngles("Head",True)
        current_angles_yaw=current_angles[0]
        current_angles_pitch=current_angles[1]
        print (current_angles)
        angle_Yaw=current_angles_yaw-self.search_angle_diff_x
        if head_angles_in_range(angle_Yaw,current_angles_pitch):
            print ("angle ok")
            fractionMaxSpeed  = 0.1
            names  = ["HeadYaw", "HeadPitch"]
            angles = [angle_Yaw,current_angles_pitch]
            self.motion.setAngles(names, angles, fractionMaxSpeed)
        else:    
            self.search_angle_diff_x=-self.search_angle_diff_x
            print ("angle out of range")

    def play_animation(self, animation_tag):
        # Play an animation.
        if self.animation==None:
            print("animations not supported (robot's naoqi version = " + str(self.naoqi_version)+")")
        else:
            animation_list=NAO_animation_tags.get(animation_tag,"")
            if animation_list:
                animation=random.choice(animation_list)
                animation_path=NAO_animations.get(animation,"")
                # Send robot to Stand
                self.posture.goToPosture("Stand", 0.2)
                #time.sleep(1.0)
                print(animation_path)
                try:
                    print ("tag: " + animation_tag+", animation "+animation+",path:"+animation_path+",started")
                    self.animation.run(animation_path)        
                except:
                    print ("tag: " + animation_tag+", animation "+animation+",path:"+animation_path+",not working")
                #time.sleep(1.0)
                # Send robot to Stand
                self.posture.goToPosture("Stand", 0.2)
                print ("play animation done")
            else :
                print ("WARNING: unknown animation tag "+animation_tag) 

    def extended_movement(self):
        curr_time=datetime.now()
        delta_time=(curr_time-self.last_extended_motion).total_seconds()
        if delta_time>0.5:
            self.last_extended_motion=curr_time
            print ("wrist movement")
            angle_RWristYaw = random.uniform(-0.5,0.5)
            angle_LWristYaw = random.uniform(-0.5,0.5)
            fractionMaxSpeed  = random.uniform(0.05,0.08)
            names  = ["RWristYaw", "LWristYaw"]
            angles = [angle_RWristYaw,angle_LWristYaw]
            self.motion.setAngles(names, angles, fractionMaxSpeed)
            print ("head movement")
            last_found_head_angles_yaw=self.last_found_head_angles[0]
            last_found_head_angles_pitch=self.last_found_head_angles[1]
            angle_random_offset_Yaw   = random.uniform(-0.05,0.05)
            angle_random_offset_Pitch = random.uniform(-0.05,0.05)
            angle_Yaw=last_found_head_angles_yaw+angle_random_offset_Yaw
            angle_Pitch=last_found_head_angles_pitch+angle_random_offset_Pitch
            if head_angles_in_range(angle_Yaw,angle_Pitch):
                print ("angle ok")
                fractionMaxSpeed  = 0.1
                names  = ["HeadYaw", "HeadPitch"]
                angles = [angle_Yaw,angle_Pitch]
                self.motion.setAngles(names, angles, fractionMaxSpeed)
            else:    
                print ("angle out of range")

    def move(self,line):
        if len(line)>=9 and line[8].strip() :
            animation=line[8].strip()
            self.play_animation(animation)
        else : 
            self.set_arm_stiffness(1)
            self.extended_movement()
            names = ["LShoulderPitch","LShoulderRoll", "LElbowYaw", "LElbowRoll", \
                    "RShoulderPitch","RShoulderRoll", "RElbowYaw", "RElbowRoll"]
            angles = [float(line[0]), float(line[1]), float(line[2]), float(line[3]), \
                    float(line[4]), float(line[5]), float(line[6]), float(line[7])]
            if angles_in_range(angles) :
                self.motion.setAngles(names, angles, self.fractionMaxSpeed)
            
    def terminate(self):
        if self.posture_crouch==True:
            #self.posture.goToPosture("Crouch", 0.5)
            #self.motion.setStiffnesses("Body", 0.0)
            self.motion.setAngles("LArm",LArms_crouch_angles,self.fractionMaxSpeed)
            self.motion.setAngles("RArm",RArms_crouch_angles,self.fractionMaxSpeed)
            self.set_arm_stiffness(0.0)
            pass
        else:
            self.posture.goToPosture("Stand", 0.5)

def convert_to_ascii(text):
    if not isinstance(text,unicode):
        print ("not unicode")
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

class vision():

    def __init__(self,robot_ip,device) : 
        if unicode(device).isnumeric():
            self.vid_module_name="sobotify"
            self.video_service =  ALProxy("ALVideoDevice", robot_ip, 9559)
            #resolution = vision_definitions.kQVGA
            resolution = vision_definitions.kVGA
            color_space = vision_definitions.kBGRColorSpace
            framerate = 10
            list_subs= self.video_service.getSubscribers()
            for sub in list_subs:
                if self.vid_module_name in sub:
                    print ("unsubscribe " + sub)
                    self.video_service.unsubscribe(sub)
            self.nameId = self.video_service.subscribeCamera("sobotify", int(device),resolution, color_space, framerate)
        else:
            print ("Wrong camera device, please use 0 or 1")


    def get_image(self) : 
        image=self.video_service.getImageRemote(self.nameId)
        image_width=image[0]
        image_height=image[1]
        image_data=image[6]
        image_byte_array=bytearray(image_data);
        image_np_array_1d=np.asarray(image_byte_array,dtype=np.uint8)
        image_np_array_3d=image_np_array_1d.reshape(image_height,image_width,3)
        return True,image_np_array_3d
    
    def terminate(self):
        self.video_service.unsubscribe(self.nameId)
        pass   