#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Attribution: Part of this code is based on 
https://github.com/Kazuhito00/mediapipe-python-sample/blob/main/sample_pose.py
https://github.com/elggem/naoqi-pose-retargeting/blob/main/teleop.py
(both Apache 2.0 Licensed)
"""

import cv2 as cv
import numpy as np
import mediapipe as mp
import argparse
from datetime import datetime
import time
from sobotify.commons.mqttclient import mqttClient
import sobotify.robots.stickman.stickman as stickman
import sobotify.robots.robots as robots
import threading
  

class TeleOperator:

    def __init__(self,mqtt,mosquitto_ip,robot_name,cam_device,frame_rate,show_video,show_stickman) :
        self.mqtt=mqtt
        self.robot_name=robot_name
        self.cam_device=cam_device
        self.show_video=show_video
        self.show_stickman=show_stickman
        self.frame_rate=frame_rate
        self.activated=False
        
        model_complexity         = 1   # model_complexity(0,1(default),2)
        min_detection_confidence = 0.5 #  default=0.5
        min_tracking_confidence  = 0.5 #  default=0.5
        mp_pose = mp.solutions.pose
        self.pose = mp_pose.Pose(
            model_complexity=model_complexity,
            enable_segmentation=False,
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence,
        )

        if self.show_stickman=="on" and not (self.mqtt=="on" and self.robot_name=="stickman") :
                self.motion_visualizer=stickman.motion()
        else:
            self.motion_visualizer=None
        ## currently use computer camera for teleoperation (which corresponds to "stickman" camera)
        self.camera=stickman.vision(cam_device) 

        #self.thread_video2landmarks = threading.Thread(target=self.video2landmarks)
        #self.thread_video2landmarks.start()

        if self.mqtt=="on" :
            self.mqtt_client = mqttClient(mosquitto_ip,"teleoperator")
            self.mqtt_client.subscribe("teleoperator/command/start",self.start)
            self.mqtt_client.subscribe("teleoperator/command/stop",self.stop)
        if self.mqtt=="on" :
            self.mqtt_client.publish("teleoperator/status/init-done")


        print (" finished")

    def get_landmarks(self,landmarks) :
        landmarks_array = []
        for index, landmark in enumerate(landmarks):
            landmarks_array.append([landmark.x, landmark.y, landmark.z,landmark.visibility])
        landmarks_array = np.array(landmarks_array)
        return landmarks_array

    def landmarks2angles(self,landmarks,robot_name) :
        landmarks_array = self.get_landmarks(landmarks)
        gesture_conversion=robots.get_angles(robot_name)
        if not gesture_conversion is None :
            result,angles = gesture_conversion(landmarks_array,"","")
            return result,angles
        else:
            return False, ""

    def video2landmarks(self):
        start_time=datetime.now()
        while True:
            if self.activated==True:
                ret, image=self.camera.get_image()
                #print (str(datetime.now())+": got image :"+str(ret))
                if ret:
                    #image = cv.flip(image, 1)
                    if (self.show_video=="on"):
                        #image_small=cv.resize(image,(0,0),fx=0.5,fy=0.5)
                        cv.imshow("Image",image)
                        if cv.waitKey(1) == ord("q"):
                            break
                    image = cv.cvtColor(image, cv.COLOR_BGR2RGB)
                    results = self.pose.process(image)
                    if results.pose_landmarks is not None:
                        landmarks_array=self.get_landmarks(results.pose_landmarks.landmark)
                        if not self.motion_visualizer==None:
                            self.motion_visualizer.move(landmarks_array)
                        if self.robot_name=="stickman":
                            if self.mqtt=="on" :
                                self.mqtt_client.publish("robot_control/command/move",str(landmarks_array.tolist()))                            
                    if results.pose_world_landmarks is not None:
                        time_stamp=(datetime.now()-start_time).total_seconds()
                        result,angles = self.landmarks2angles(results.pose_world_landmarks.landmark,self.robot_name,time_stamp)
                        if result==True:
                            #print (str(datetime.now())+": send angles :"+str(angles))
                            if not self.robot_name=="stickman":
                                if self.mqtt=="on" :
                                    #print (str(datetime.now())+": send angles :"+str(angles))
                                    self.mqtt_client.publish("robot_control/command/move",str(angles))
                        #else:
                        #    print (str(datetime.now())+": angles error xxxxxxxxxxxxxxxxxxxxxxx")
                else:
                    print ("no frame to be read")
            else:
                start_time=datetime.now()

            time.sleep(0.01)
        if (self.show_video=="on"):
            self.motion_visualizer.stop()
            time.sleep(0.2)
            cv.destroyAllWindows()

    def start(self,message) :
        print("teleoperation started")
        print ("Press key 'q' in camera window to stop teleoperation")
        self.activated=True

    def stop(self,message) :
        print("teleoperation stopped")
        #blank=np.zeros((self.cap.get(cv.CAP_PROP_FRAME_WIDTH),self.cap.get(cv.CAP_PROP_FRAME_WIDTH)),)
        #cv.imshow("Image",image_small)
        self.activated=False

def teleoperator(mqtt,mosquitto_ip,robot_name,cam_device,frame_rate,show_video,show_stickman) :
    tele_operator = TeleOperator(mqtt,mosquitto_ip,robot_name,cam_device,frame_rate,show_video,show_stickman)
    if mqtt=="on" :
        tele_operator.video2landmarks()
        pass
    else :
        tele_operator.start("")
        tele_operator.video2landmarks()


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description='teleoperation of robot')
    parser.add_argument('--mqtt',default="off",help='enable/disable mqtt client (on/off)')
    parser.add_argument('--mosquitto_ip',default='127.0.0.1',help='ip address of the mosquitto server')
    parser.add_argument('--robot_name',default='stickman',help='name of the robot (stickman,pepper)')
    parser.add_argument('--cam_device',default='0',help='camera device name or number')
    parser.add_argument('--frame_rate',default=1,type=float,help='frame rate')
    parser.add_argument('--show_video',default="on",help='enable/disable video output on screen')
    parser.add_argument('--show_stickman',default="on",help='enable/disable video output on screen')
    args=parser.parse_args()
    teleoperator(args.mqtt,args.mosquitto_ip,args.robot_name,args.cam_device,args.frame_rate,args.show_video,args.show_stickman)
    
