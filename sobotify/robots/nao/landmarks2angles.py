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

"""
Attribution: The following function is taken from (and modified) pepper_approach_control_thread.py 
from https://github.com/FraPorta/pepper_openpose_teleoperation/tree/main/pepper_teleoperation
(Apache 2.0 Licensed)
"""
##  function saturate_angles
#   Saturate angles before using them for controlling Pepper joints
def saturate_angles(LShoulderPitch, LShoulderRoll, LElbowYaw, LElbowRoll, RShoulderPitch, RShoulderRoll, RElbowYaw, RElbowRoll) :
    # global LShoulderPitch, LShoulderRoll, LElbowYaw, LElbowRoll, RShoulderPitch, RShoulderRoll, RElbowYaw, RElbowRoll
    # limit percentage for some angles 
    limit = 0.9
        
    ## LEFT ##
    # LShoulderPitch saturation
    if LShoulderPitch is None:
        print ("warning : LShoulderPitch value missing")
    elif LShoulderPitch < -2.0857:
        LShoulderPitch = -2.0857
    elif LShoulderPitch > 2.0857:
        LShoulderPitch = 2.0857
    
    # LShoulderRoll saturation
    if LShoulderRoll is None:
        print ("warning : LShoulderRoll value missing")
#    elif LShoulderRoll < -0.3142:
#        LShoulderRoll = -0.3142
    elif LShoulderRoll < 0:
        LShoulderRoll = 0
    elif LShoulderRoll > 1.3265:
        LShoulderRoll = 1.3265
        
    # LElbowYaw saturation
    if LElbowYaw is None:
        print ("warning : LElbowYaw value missing")
    elif LElbowYaw < -2.0857*limit:
        LElbowYaw = -2.0857*limit
    elif LElbowYaw > 2.0857*limit:
        LElbowYaw = 2.0857*limit

    # LElbowRoll saturation
    if LElbowRoll is None:
        print ("warning : LElbowRoll value missing")
    elif LElbowRoll < -1.5446:
        LElbowRoll = -1.5446
    elif LElbowRoll > -0.0349:
        LElbowRoll = -0.0349

    ## RIGHT ##
    # RShoulderPitch saturation
    if RShoulderPitch is None:
        print ("warning : RShoulderPitch value missing")
    elif RShoulderPitch < -2.0857:
        RShoulderPitch = -2.0857
    elif RShoulderPitch > 2.0857:
        RShoulderPitch = 2.0857
    
    # RShoulderRoll saturation
    if RShoulderRoll is None:
        print ("warning : RShoulderPitch value missing")
    elif RShoulderRoll < -1.3265 :
        RShoulderRoll = -1.3265
    #elif RShoulderRoll > 0.3142:
    #    RShoulderRoll = 0.3142
    elif RShoulderRoll > 0:
        RShoulderRoll = 0
        
    # RElbowYaw saturation
    if RElbowYaw is None:
        print ("warning : RElbowYaw value missing")
    elif RElbowYaw < -2.0857*limit:
        RElbowYaw = -2.0857*limit
    elif RElbowYaw > 2.0857*limit:
        RElbowYaw = 2.0857*limit

    # RElbowRoll saturation
    if RElbowRoll is None:
        print ("warning : RElbowRoll value missing")
    elif RElbowRoll < 0.0349:
        RElbowRoll = 0.0349
    elif RElbowRoll > 1.5446:
        RElbowRoll = 1.5446
  
    angles = [LShoulderPitch,LShoulderRoll, LElbowYaw, LElbowRoll, RShoulderPitch,RShoulderRoll, RElbowYaw, RElbowRoll]
    return angles    


"""
Attribution: The following function is taken from (and modified) teleop.py 
from https://github.com/elggem/naoqi-pose-retargeting
(Apache 2.0 Licensed)
"""

def store_angles(world_landmarks_array, time_stamp,angles_filename):

    visibility_threshold=0.5

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

    pNeck =   (0.5 * (np.array(world_landmarks_array[11]) + np.array(world_landmarks_array[12]))).tolist()
    pMidHip = (0.5 * (np.array(world_landmarks_array[23]) + np.array(world_landmarks_array[24]))).tolist()

    if ((world_landmarks_array[11][3]>visibility_threshold) and 
        (world_landmarks_array[12][3]>visibility_threshold) and
        (world_landmarks_array[13][3]>visibility_threshold)) :
        LShoulderPitch, LShoulderRoll = keypointsToAngles.obtain_LShoulderPitchRoll_angles(pNeck, world_landmarks_array[11], world_landmarks_array[13], pMidHip)
    else:
        LShoulderPitch=None
        LShoulderRoll=None

    if ((world_landmarks_array[11][3]>visibility_threshold) and 
        (world_landmarks_array[12][3]>visibility_threshold) and
        (world_landmarks_array[14][3]>visibility_threshold)) :
        RShoulderPitch, RShoulderRoll = keypointsToAngles.obtain_RShoulderPitchRoll_angles(pNeck, world_landmarks_array[12], world_landmarks_array[14], pMidHip)
    else:
        RShoulderPitch=None
        RShoulderRoll=None
    
    if ((world_landmarks_array[11][3]>visibility_threshold) and 
        (world_landmarks_array[12][3]>visibility_threshold) and
        (world_landmarks_array[13][3]>visibility_threshold) and
        (world_landmarks_array[15][3]>visibility_threshold)) :
        LElbowYaw, LElbowRoll = keypointsToAngles.obtain_LElbowYawRoll_angle(pNeck, world_landmarks_array[11], world_landmarks_array[13], world_landmarks_array[15])
    else:
        LElbowYaw=None
        LElbowRoll=None

    if ((world_landmarks_array[11][3]>visibility_threshold) and 
        (world_landmarks_array[12][3]>visibility_threshold) and
        (world_landmarks_array[14][3]>visibility_threshold) and
        (world_landmarks_array[16][3]>visibility_threshold)) :
        RElbowYaw, RElbowRoll = keypointsToAngles.obtain_RElbowYawRoll_angle(pNeck, world_landmarks_array[12], world_landmarks_array[14], world_landmarks_array[16])
    else:
        RElbowYaw=None
        RElbowRoll=None
    
    angles=saturate_angles(LShoulderPitch, LShoulderRoll, LElbowYaw, LElbowRoll, RShoulderPitch, RShoulderRoll, RElbowYaw, RElbowRoll)
    return True, angles

def landmarks2angles(world_landmarks_filename,data_path):

    fileName, ext = os.path.splitext(os.path.basename(world_landmarks_filename))
    fileName=fileName[:-8]; # remove "_wlmarks" ending from file name
    angles_filename= os.path.join(data_path,fileName+"_nao.csv")

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
    
