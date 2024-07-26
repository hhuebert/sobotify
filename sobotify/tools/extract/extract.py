import argparse
import os
import sobotify.tools.extract.video2landmarks as video2landmarks
import sobotify.tools.extract.audio2srt as audio2srt
import sobotify.tools.extract.video2timestamps as video2timestamps
import sobotify.tools.extract.landmarks2angles as converter
import sobotify.robots.robots as robots

def extract(video_file,data_path,robot_name,ffmpeg_path,vosk_model_path,language,show_video):
    #REM for recording on Android Phone with Bluetooth Headset/microphone use : https://play.google.com/store/apps/details?id=com.bedoig.BTmono&hl=de&gl=US
    print("extracting gesture and speech in video file ", video_file, "and store results to ", data_path)
    print("extract time stamps")
    video2timestamps.video2timestamps(video_file,data_path,ffmpeg_path)    
    print("speech recognition")
    audio2srt.audio2srt(video_file,data_path,ffmpeg_path,vosk_model_path,language)
    print("extract landmarks")
    video2landmarks.video2landmarks(video_file,data_path,show_video)
    robot_names=[]
    if robot_name=="all": robot_names=robots.get_names()
    else : robot_names.append(robot_name)
    for robot in robot_names :
        fileName, ext = os.path.splitext(os.path.basename(video_file))
        world_landmarks_filename= os.path.join(data_path,fileName+"_wlmarks.csv")
        print("convert landmarks to robot movement data for " + robot)
        converter.landmarks2angles(robot,world_landmarks_filename,data_path)
    print("... done extracting gesture and speech!")

if __name__ == '__main__':
    parser=argparse.ArgumentParser(description='extract human gestures/poses from video file and store them as landmarks in csv text file')
    parser.add_argument('--video_file',default='video.mp4',help='path to the video input file')
    parser.add_argument('--robot_name',default='all',help='name of the robot (all,stickman,pepper,nao,cozmo,mykeepon)')
    parser.add_argument('--ffmpeg_path',default=os.path.join(os.path.expanduser("~"),".sobotify","ffmpeg","bin"),help='directory path to ffmpeg tools (bin directory)')
    parser.add_argument('--vosk_model_path',default=os.path.join(os.path.expanduser("~"),".sobotify","vosk","models"),help='path to vosk_model')
    parser.add_argument('--language',default="english",help='choose language (english,german)')
    parser.add_argument('--data_path',default=os.path.join(os.path.expanduser("~"),".sobotify","data"),help='path to movement/speech data')
    parser.add_argument('--show_video',default="on",help='enable/disable video output on screen')
    args=parser.parse_args()
    extract(args.video_file,args.data_path,args.robot_name,args.ffmpeg_path,args.vosk_model_path,args.language,args.show_video)    