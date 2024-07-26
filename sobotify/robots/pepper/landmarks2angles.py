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
        print ("Error : LShoulderPitch value missing");
    elif LShoulderPitch < -2.0857:
        LShoulderPitch = -2.0857
    elif LShoulderPitch > 2.0857:
        LShoulderPitch = 2.0857
    
    # LShoulderRoll saturation
    if LShoulderRoll is None:
        print ("warning : LShoulderRoll value missing");
    elif LShoulderRoll < 0.0087:
        LShoulderRoll = 0.0087
    elif LShoulderRoll > 1.5620:
        LShoulderRoll = 1.5620
        
    # LElbowYaw saturation
    if LElbowYaw is None:
        print ("warning : LElbowYaw value missing");
    elif LElbowYaw < -2.0857*limit:
        LElbowYaw = -2.0857*limit
    elif LElbowYaw > 2.0857*limit:
        LElbowYaw = 2.0857*limit

    # LElbowRoll saturation
    if LElbowRoll is None:
        print ("warning : LElbowRoll value missing");
    elif LElbowRoll < -1.5620:
        LElbowRoll = -1.5620
    elif LElbowRoll > -0.0087:
        LElbowRoll = -0.0087


    ## RIGHT ##
    # RShoulderPitch saturation
    if RShoulderPitch is None:
        print ("warning : RShoulderPitch value missing");
    elif RShoulderPitch < -2.0857:
        RShoulderPitch = -2.0857
    elif RShoulderPitch > 2.0857:
        RShoulderPitch = 2.0857
    
    # RShoulderRoll saturation
    if RShoulderRoll is None:
        print ("warning : RShoulderPitch value missing");
    elif RShoulderRoll < -1.5620 :
        RShoulderRoll = -1.5620
    elif RShoulderRoll > -0.0087:
        RShoulderRoll = -0.0087
        
    # RElbowYaw saturation
    if RElbowYaw is None:
        print ("warning : RElbowYaw value missing");
    elif RElbowYaw < -2.0857*limit:
        RElbowYaw = -2.0857*limit
    elif RElbowYaw > 2.0857*limit:
        RElbowYaw = 2.0857*limit

    # RElbowRoll saturation
    if RElbowRoll is None:
        print ("warning : RElbowRoll value missing");
    elif RElbowRoll < 0.0087:
        RElbowRoll = 0.0087
    elif RElbowRoll > 1.5620:
        RElbowRoll = 1.5620

    # HipPitch saturation: -1.0385 to 1.0385
    if HipPitch is None:
        print ("warning : HipPitch value missing");
    elif HipPitch < -1.0385:
        HipPitch = -1.0385
    elif HipPitch > 1.0385:
        HipPitch = 1.0385
        
    angles = [LShoulderPitch,LShoulderRoll, LElbowYaw, LElbowRoll, RShoulderPitch,RShoulderRoll, RElbowYaw, RElbowRoll,HipPitch]
    return angles    


def convert(world_landmarks_array, time_stamp,angles_filename):
    visibility_threshold=0.5
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
        
    HipPitch = keypointsToAngles.obtain_HipPitch_angles(pMidHip, pNeck) # This is switched, why?

    HipPitch = 0
    
    angles=saturate_angles(LShoulderPitch, LShoulderRoll, LElbowYaw, LElbowRoll, RShoulderPitch, RShoulderRoll, RElbowYaw, RElbowRoll,HipPitch)
    return True, angles

