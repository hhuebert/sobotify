#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Attribution: Part of this code is based on 
https://github.com/Kazuhito00/mediapipe-python-sample/blob/main/sample_pose.py
(Apache 2.0 Licensed)
"""
import os
import argparse
import csv
import numpy as np
from sobotify.commons.external.utils import KeypointsToAngles

keypointsToAngles = KeypointsToAngles()

def checkLim(val, limits):
    return val < limits[0] or val > limits[1]


"""
Attribution: The following function is taken from (and modified) pepper_approach_control_thread.py 
from https://github.com/FraPorta/pepper_openpose_teleoperation/tree/main/pepper_teleoperation
(Apache 2.0 Licensed)
"""
##  function saturate_angles
#   Saturate angles before using them for controlling Pepper joints
def saturate_angles(LShoulderPitch, LShoulderRoll, LElbowYaw, LElbowRoll, RShoulderPitch, RShoulderRoll, RElbowYaw, RElbowRoll, HipPitch) :
    # global LShoulderPitch, LShoulderRoll, LElbowYaw, LElbowRoll, RShoulderPitch, RShoulderRoll, RElbowYaw, RElbowRoll, HipPitch
    # limit percentage for some angles 
    limit = 0.9
    
    error = False
    
    ## LEFT ##
    # LShoulderPitch saturation
    if LShoulderPitch is None:
        # LShoulderPitch = mProxy.getData("Device/SubDeviceList/LShoulderPitch/Position/Actuator/Value")
        # self.LShoulderPitch = mProxy.getData("Device/SubDeviceList/LShoulderPitch/Position/Sensor/Value")
        print ("Error : LShoulderPitch value missing");
        error = True
    elif LShoulderPitch < -2.0857:
        LShoulderPitch = -2.0857
    elif LShoulderPitch > 2.0857:
        LShoulderPitch = 2.0857
    
    # LShoulderRoll saturation
    if LShoulderRoll is None:
        # LShoulderRoll = mProxy.getData("Device/SubDeviceList/LShoulderRoll/Position/Actuator/Value")
        # self.LShoulderRoll = mProxy.getData("Device/SubDeviceList/LShoulderRoll/Position/Sensor/Value")
        print ("Error : LShoulderRoll value missing");
        error = True
    elif LShoulderRoll < 0.0087:
        LShoulderRoll = 0.0087
    elif LShoulderRoll > 1.5620:
        LShoulderRoll = 1.5620
        
    # LElbowYaw saturation
    if LElbowYaw is None:
        # LElbowYaw = mProxy.getData("Device/SubDeviceList/LElbowYaw/Position/Actuator/Value")
        # self.LElbowYaw = mProxy.getData("Device/SubDeviceList/LElbowYaw/Position/Sensor/Value")
        print ("Error : LElbowYaw value missing");
        error = True
    elif LElbowYaw < -2.0857*limit:
        LElbowYaw = -2.0857*limit
    elif LElbowYaw > 2.0857*limit:
        LElbowYaw = 2.0857*limit

    # LElbowRoll saturation
    if LElbowRoll is None:
        # LElbowRoll = mProxy.getData("Device/SubDeviceList/LElbowRoll/Position/Actuator/Value")
        # self.LElbowRoll = mProxy.getData("Device/SubDeviceList/LElbowRoll/Position/Sensor/Value")
        print ("Error : LElbowRoll value missing");
        error = True
    elif LElbowRoll < -1.5620:
        LElbowRoll = -1.5620
    elif LElbowRoll > -0.0087:
        LElbowRoll = -0.0087


    ## RIGHT ##
    # RShoulderPitch saturation
    if RShoulderPitch is None:
        # RShoulderPitch = mProxy.getData("Device/SubDeviceList/RShoulderPitch/Position/Actuator/Value")
        # self.RShoulderPitch = mProxy.getData("Device/SubDeviceList/RShoulderPitch/Position/Sensor/Value")
        print ("Error : RShoulderPitch value missing");
        error = True
    elif RShoulderPitch < -2.0857:
        RShoulderPitch = -2.0857
    elif RShoulderPitch > 2.0857:
        RShoulderPitch = 2.0857
    
    # RShoulderRoll saturation
    if RShoulderRoll is None:
        # RShoulderRoll = mProxy.getData("Device/SubDeviceList/RShoulderRoll/Position/Actuator/Value")
        # self.RShoulderRoll = mProxy.getData("Device/SubDeviceList/RShoulderRoll/Position/Sensor/Value")
        print ("Error : RShoulderPitch value missing");
        error = True
    elif RShoulderRoll < -1.5620 :
        RShoulderRoll = -1.5620
    elif RShoulderRoll > -0.0087:
        RShoulderRoll = -0.0087
        
    # RElbowYaw saturation
    if RElbowYaw is None:
        # RElbowYaw = mProxy.getData("Device/SubDeviceList/RElbowYaw/Position/Actuator/Value")
        # self.RElbowYaw = mProxy.getData("Device/SubDeviceList/RElbowYaw/Position/Sensor/Value")
        print ("Error : RElbowYaw value missing");
        error = True
    elif RElbowYaw < -2.0857*limit:
        RElbowYaw = -2.0857*limit
    elif RElbowYaw > 2.0857*limit:
        RElbowYaw = 2.0857*limit

    # RElbowRoll saturation
    if RElbowRoll is None:
        # RElbowRoll = mProxy.getData("Device/SubDeviceList/RElbowRoll/Position/Actuator/Value")
        # self.RElbowRoll = mProxy.getData("Device/SubDeviceList/RElbowRoll/Position/Sensor/Value")
        print ("Error : RElbowRoll value missing");
        error = True
    elif RElbowRoll < 0.0087:
        RElbowRoll = 0.0087
    elif RElbowRoll > 1.5620:
        RElbowRoll = 1.5620

    # HipPitch saturation: -1.0385 to 1.0385
    if HipPitch is None:
        # HipPitch = mProxy.getData("Device/SubDeviceList/HipPitch/Position/Actuator/Value")
        # self.HipPitch = mProxy.getData("Device/SubDeviceList/HipPitch/Position/Sensor/Value")
        print ("Error : HipPitch value missing");
        error = True
    elif HipPitch < -1.0385:
        HipPitch = -1.0385
    elif HipPitch > 1.0385:
        HipPitch = 1.0385
        
    return error    


def store_angles(world_landmarks_array, time_stamp,angles_filename):
    limitsLShoulderPitch = [-2.0857, 2.0857]
    limitsLShoulderRoll  = [ 0.0087, 1.5620]
    limitsLElbowYaw      = [-2.0857, 2.0857]
    limitsLElbowRoll     = [-1.5620,-0.0087]

    limitsRShoulderPitch = [-2.0857, 2.0857]
    limitsRShoulderRoll  = [-1.5620,-0.0087]
    limitsRElbowYaw      = [-2.0857, 2.0857]
    limitsRElbowRoll     = [ 0.0087, 1.5620]

    limitsHipPitch       = [-1.0385, 1.0385]

    pNeck =   (0.5 * (np.array(world_landmarks_array[11]) + np.array(world_landmarks_array[12]))).tolist()
    pMidHip = (0.5 * (np.array(world_landmarks_array[23]) + np.array(world_landmarks_array[24]))).tolist()

    LShoulderPitch, LShoulderRoll = keypointsToAngles.obtain_LShoulderPitchRoll_angles(pNeck, world_landmarks_array[11], world_landmarks_array[13], pMidHip)
    RShoulderPitch, RShoulderRoll = keypointsToAngles.obtain_RShoulderPitchRoll_angles(pNeck, world_landmarks_array[12], world_landmarks_array[14], pMidHip)
    
    LElbowYaw, LElbowRoll = keypointsToAngles.obtain_LElbowYawRoll_angle(pNeck, world_landmarks_array[11], world_landmarks_array[13], world_landmarks_array[15])
    RElbowYaw, RElbowRoll = keypointsToAngles.obtain_RElbowYawRoll_angle(pNeck, world_landmarks_array[12], world_landmarks_array[14], world_landmarks_array[16])

    HipPitch = keypointsToAngles.obtain_HipPitch_angles(pMidHip, pNeck) # This is switched, why?

    HipPitch = 0
    
    saturate_angles(LShoulderPitch, LShoulderRoll, LElbowYaw, LElbowRoll, RShoulderPitch, RShoulderRoll, RElbowYaw, RElbowRoll, HipPitch)

    angles = [LShoulderPitch,LShoulderRoll, LElbowYaw, LElbowRoll, RShoulderPitch,RShoulderRoll, RElbowYaw, RElbowRoll, HipPitch]

    if (checkLim(LShoulderPitch, limitsLShoulderPitch) or 
        checkLim(RShoulderPitch, limitsRShoulderPitch) or
        checkLim(LShoulderRoll, limitsLShoulderRoll) or 
        checkLim(RShoulderRoll, limitsRShoulderRoll) or
        checkLim(LElbowYaw, limitsLElbowYaw) or 
        checkLim(RElbowYaw, limitsRElbowYaw) or
        checkLim(LElbowRoll, limitsLElbowRoll) or 
        checkLim(RElbowRoll, limitsRElbowRoll)):
        return False, angles
    else:     
        return True, angles

def landmarks2angles(world_landmarks_filename,data_path):

    fileName, ext = os.path.splitext(os.path.basename(world_landmarks_filename))
    fileName=fileName[:-8]; # remove "_wlmarks" ending from file name
    angles_filename= os.path.join(data_path,fileName+"_pepper.csv")

    try:
        world_landmarks_file   = open(world_landmarks_filename, "r", newline='')
    except Exception : 
        print ("Cannot open world landmarks file for reading: "+str(world_landmarks_filename))
        exit()      
    
    try:
        angles_file=open(angles_filename, "w", newline='')
    except Exception : 
        print ("Cannot open angles file for writing: "+str(world_landmarks_filename))
        exit()      

    world_landmarks_file_reader = csv.reader(world_landmarks_file)
    angles_writer = csv.writer(angles_file)
    
    for i,row in enumerate(world_landmarks_file_reader) :
        time_stamp= float(row[0])  # first column is time stamp
        row.pop(0)  # strip time stamp off ==> remaining columns are the flattened array of landmarks
        world_landmarks_array = np.array(row).astype(float)
        world_landmarks_array = np.reshape(world_landmarks_array,(-1,4))
        result,angles = store_angles(world_landmarks_array,time_stamp,angles_filename)
        if result == True:
            row = np.insert(angles,0,time_stamp)
            angles_writer.writerow(row)

if __name__ == '__main__':
    parser=argparse.ArgumentParser(description='convert landmarks into robot joint angles and store them in csv text file')
    parser.add_argument('--world_landmarks_file',default='video_wlmarks.csv',help='path to the video input file')
    parser.add_argument('--data_path',default=os.path.expanduser("~")+"/.sobotify/data",help='path to movement/speech data')
    args=parser.parse_args()
    landmarks2angles(args.world_landmarks_file,args.data_path)    
    print("Finished!")
    
