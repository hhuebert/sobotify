#!/usr/bin/env python3
import argparse
import os
import subprocess

def video2timestamps(video_file,data_path,ffmpeg_path):
    ffprobe_full_path=os.path.join(ffmpeg_path,"ffprobe")
    #if not os.path.exists(ffprobe_full_path) :
    #    print ("Error: Cannot find ffprobe ==> specify with command line argument");
    #    exit()
    fileName, ext = os.path.splitext(os.path.basename(video_file))
    arguments=[ffprobe_full_path]
    arguments.extend(('-v','error'))
    arguments.append('-hide_banner')
    arguments.extend(('-show_entries','packet=pts_time'))
    arguments.extend(('-of','default=noprint_wrappers=1'))
    arguments.extend(('-select_streams','v:0'))
    arguments.append(video_file)
    tsp_full_path= os.path.join(data_path,fileName+'.tsp')
    with open (tsp_full_path,"w") as timestamps:
        ffrpobe_proc=subprocess.run(arguments, stdout=timestamps)


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description='extract timestamps of frames in a video')
    parser.add_argument('--ffmpeg_path',default=os.path.join(os.path.expanduser("~"),".sobotify","ffmpeg","bin"),help='directory path to ffmpeg tools (bin directory)')
    parser.add_argument('--video_file',default='video.mp4',help='video input file')
    parser.add_argument('--data_path',default=os.path.expanduser("~")+"/.sobotify/data",help='path to movement/speech data')
    args=parser.parse_args()
    video2timestamps(args.video_file,args.data_path,args.ffmpeg_path)