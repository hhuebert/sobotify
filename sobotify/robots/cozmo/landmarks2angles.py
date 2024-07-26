#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import argparse
import csv
import numpy as np

# currently only using random list of values,
# should be replaced with real mapping of human gestures to robot movements
angle_list=[
[45.0,0.6,0,"neutral"],
[35.0,0.6,0,"neutral"]
]    

prev_angle_time=-1
curr_angle_high=True

#MAX_HEAD_ANGLE.radians =  0.7766715171374767
#MIN_HEAD_ANGLE.radians= -0.4363323129985824
#MAX_LIFT_HEIGHT.mm = 92.0
#MIN_LIFT_HEIGHT.mm = 32.0

def convert(world_landmarks_array, time_stamp,angles_filename):
    angles= [0.0]
    global prev_angle_time
    global curr_angle_high
    if (time_stamp-prev_angle_time)>1:
        prev_angle_time=time_stamp
        curr_angle_high = not curr_angle_high
        if curr_angle_high==True:
            angles = angle_list[0]
        else:
            angles = angle_list[1]
        return True, angles
    else:
        return False, angles


