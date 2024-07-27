#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import argparse
import csv
import numpy as np
import sobotify.robots.robots as robots

def landmarks2angles(robot_name,world_landmarks_filename,data_path):

    gesture_converter=robots.get_gesture_converter(robot_name)
    if not gesture_converter is None :
        fileName, ext = os.path.splitext(os.path.basename(world_landmarks_filename))
        fileName=fileName[:-8]; # remove "_wlmarks" ending from file name
        angles_filename= os.path.join(data_path,fileName+"_"+robot_name+".csv")

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
            result,angles = gesture_converter(world_landmarks_array,time_stamp,angles_filename)
            if result == True:
                row = np.insert(angles,0,time_stamp)
                angles_writer.writerow(row)

if __name__ == '__main__':
    parser=argparse.ArgumentParser(description='convert landmarks into robot joint angles and store them in csv text file')
    parser.add_argument('--robot_name',default='all',help='name of the robot (all,stickman,pepper,nao,cozmo,mykeepon)')
    parser.add_argument('--world_landmarks_file',default='video_wlmarks.csv',help='path to the video input file')
    parser.add_argument('--data_path',default=os.path.expanduser("~")+"/.sobotify/data",help='path to movement/speech data')
    args=parser.parse_args()
    landmarks2angles(args.robot_name,args.world_landmarks_file,args.data_path)    
    print("Finished!")
    
