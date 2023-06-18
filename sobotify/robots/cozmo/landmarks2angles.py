#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import argparse
import csv
import numpy as np

prev_angle_time=-1
curr_angle_high=True

#MAX_HEAD_ANGLE.radians =  0.7766715171374767
#MIN_HEAD_ANGLE.radians= -0.4363323129985824
#MAX_LIFT_HEIGHT.mm = 92.0
#MIN_LIFT_HEIGHT.mm = 32.0

def store_angles(world_landmarks_array, time_stamp,angles_filename):
    angles= [0.0]
    global prev_angle_time
    global curr_angle_high
    if (time_stamp-prev_angle_time)>1:
        prev_angle_time=time_stamp
        curr_angle_high = not curr_angle_high
        if curr_angle_high==True:
            angles = [30,0.5,"neutral"]
        else:
            angles = [90,0.5,"neutral"]
        return True, angles
    else:
        return False, angles


def landmarks2angles(world_landmarks_filename,data_path):

    fileName, ext = os.path.splitext(os.path.basename(world_landmarks_filename))
    fileName=fileName[:-8]; # remove "_wlmarks" ending from file name
    angles_filename= os.path.join(data_path,fileName+"_cozmo.csv")

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
    
