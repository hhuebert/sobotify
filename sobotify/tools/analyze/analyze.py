import argparse
import os
import sobotify.tools.analyze.video2landmarks as video2landmarks
import sobotify.tools.analyze.audio2srt as audio2srt
import sobotify.tools.analyze.video2timestamps as video2timestamps

def getRobot(name) :
    if name=='stickman' :
        return None
    elif name=='pepper' :
        import sobotify.robots.pepper.landmarks2angles as landmarks2angles
        return landmarks2angles.landmarks2angles
    elif name=='nao' :
        import sobotify.robots.nao.landmarks2angles as landmarks2angles
        return landmarks2angles.landmarks2angles
    else :
        print("unknow robot :" + str(name))
        return None


def analyze(video_file,data_path,robot_name,ffmpeg_path,vosk_model_path,language):
    #REM for recording on Android Phone with Bluetooth Headset/microphone use : https://play.google.com/store/apps/details?id=com.bedoig.BTmono&hl=de&gl=US
    print("extracting gesture and speech in video file ", video_file, "and store results to ", data_path)
    video2timestamps.video2timestamps(video_file,data_path,ffmpeg_path)    
    audio2srt.audio2srt(video_file,data_path,ffmpeg_path,vosk_model_path,language)
    video2landmarks.video2landmarks(video_file,data_path)
    landmarks2angles_converter=getRobot(robot_name)
    if not landmarks2angles_converter is None :
        fileName, ext = os.path.splitext(os.path.basename(video_file))
        world_landmarks_filename= os.path.join(data_path,fileName+"_wlmarks.csv")
        landmarks2angles_converter(world_landmarks_filename,data_path)

if __name__ == '__main__':
    parser=argparse.ArgumentParser(description='extract human gestures/poses from video file and store them as landmarks in csv text file')
    parser.add_argument('--video_file',default='video.mp4',help='path to the video input file')
    parser.add_argument('--robot_name',default='stickman',help='name of the robot (stickman,pepper)')
    parser.add_argument('--ffmpeg_path',default=os.path.join(os.path.expanduser("~"),".sobotify","ffmpeg","bin"),help='directory path to ffmpeg tools (bin directory)')
    parser.add_argument('--vosk_model_path',default=os.path.join(os.path.expanduser("~"),".sobotify","vosk","models"),help='path to vosk_model')
    parser.add_argument('--language',default="english",help='choose language (english,german)')
    parser.add_argument('--data_path',default=os.path.join(os.path.expanduser("~"),".sobotify","data"),help='path to movement/speech data')
    args=parser.parse_args()
    analyze(args.video_file,args.data_path,args.robot_name,args.ffmpeg_path,args.vosk_model_path,args.language)    