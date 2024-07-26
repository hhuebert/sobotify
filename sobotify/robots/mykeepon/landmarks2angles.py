#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import argparse
import csv
import numpy as np

# currently only using random list of values,
# should be replaced with real mapping of human gestures to robot movements
angle_list=[
[None,None,"RIGHT",None],
[None, +10,None,None],
[None,None,"CENTERFROMRIGHT"," "],
[None, -10,None,None],
[None, -20,None,None],
[None,None,"LEFT",None],
[None,   0,None,None],
[None,None,"CENTERFROMLEFT",None],
[None,  30,None,None],
[None,   5,None,None],
[None,  -5,None,None],
[None,None,"RIGHT",None],
[None,None,"CENTERFROMRIGHT",None],
[None, -10,None,None],
[None,  10,None,None],
[None,   5,None,None]
]

prev_angle_time=-1.0
angle_it=0

def convert(world_landmarks_array, time_stamp,angles_filename):
    global prev_angle_time
    global angles
    global angle_it
    if (time_stamp-prev_angle_time)>0.5:
        prev_angle_time=time_stamp
        if angle_it>len(angle_list)-1 : angle_it=0
        angles = angle_list[angle_it]
        angle_it+=1
        return True, angles
    else:
        return False, angles
