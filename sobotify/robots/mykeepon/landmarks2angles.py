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

def store_angles(world_landmarks_array, time_stamp,angles_filename):
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

def landmarks2angles(world_landmarks_filename,data_path):

    fileName, ext = os.path.splitext(os.path.basename(world_landmarks_filename))
    fileName=fileName[:-8]; # remove "_wlmarks" ending from file name
    angles_filename= os.path.join(data_path,fileName+"_mykeepon.csv")

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
    
