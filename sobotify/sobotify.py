import os
import sys
import argparse
import subprocess
import time
import platform

def start_analyze(video_file,data_path,robot_name,ffmpeg_path,vosk_model_path,language):
    sobotify_path=os.path.dirname(os.path.abspath(__file__))
    arguments=[sys.executable,os.path.join(sobotify_path,'tools','analyze','analyze.py')]
    arguments.extend(('--video_file',video_file))
    arguments.extend(('--robot_name',robot_name))
    arguments.extend(('--ffmpeg_path',ffmpeg_path))
    arguments.extend(('--vosk_model_path',vosk_model_path))  
    arguments.extend(('--data_path',data_path))
    arguments.extend(('--language',language))
    #analyze_proc=subprocess.Popen(arguments,creationflags=subprocess.CREATE_NEW_CONSOLE)
    print (arguments);
    analyze_proc=subprocess.Popen(arguments,stdout=subprocess.PIPE)
    print ('started gesture/speech analysis, pid=',analyze_proc.pid)

def start_mosquitto(mosquitto_path): 
    sobotify_path=os.path.dirname(os.path.abspath(__file__))
    #"C:\Program Files\mosquitto\mosquitto.exe" -v -c rocontrol\mosquitto.conf
    mosquitto_proc=subprocess.Popen([mosquitto_path,'-v',"-c",os.path.join(sobotify_path,'tools','mosquitto.conf')],stdout=subprocess.PIPE, creationflags=subprocess.CREATE_NEW_CONSOLE)
    time.sleep(3)
    print ('started mosquitto, pid=',mosquitto_proc.pid)

def start_robotcontrol(mqtt,mosquitto_ip,robot_name,robot_ip,robot_conda_environment,data_path,language,min_speech_speed,max_speech_speed,message) :
    arguments=[os.path.expanduser("~")+"\miniconda3\condabin\conda.bat"]
    arguments.append("run")
    arguments.extend(('-n',robot_conda_environment))
    arguments.append("python")
    sobotify_path=os.path.dirname(os.path.abspath(__file__))
    arguments.append(os.path.join(sobotify_path,'robotcontrol','robotcontrol.py'))
    if mqtt== True: 
       arguments.extend(('--mqtt',"on"))
    arguments.extend(('--mosquitto_ip',mosquitto_ip))
    arguments.extend(('--robot_name',robot_name))
    arguments.extend(('--message',message))
    arguments.extend(('--robot_ip',robot_ip))
    arguments.extend(('--data_path',data_path))
    arguments.extend(('--language',language))
    arguments.extend(('--min_speech_speed',str(min_speech_speed)))
    arguments.extend(('--max_speech_speed',str(max_speech_speed)))
    print (arguments);
    rocontrol_proc=subprocess.Popen(arguments,creationflags=subprocess.CREATE_NEW_CONSOLE)
    #rocontrol_proc=subprocess.Popen(arguments)
    print ('started robot controller, pid=',rocontrol_proc.pid)

def start_speech_recognition(mqtt,mosquitto_ip,vosk_model_path,language,vosk_keyword,sound_device):
    sobotify_path=os.path.dirname(os.path.abspath(__file__))
    arguments=[sys.executable,os.path.join(sobotify_path,'tools','speech_recognition.py')]
    if mqtt== True: 
       arguments.extend(('--mqtt',"on"))
    arguments.extend(('--mosquitto_ip',mosquitto_ip))
    arguments.extend(('--vosk_model_path',vosk_model_path))
    arguments.extend(('--language',language))
    arguments.extend(('--vosk_keyword',vosk_keyword))
    arguments.extend(('--sound_device',str(sound_device))) 
    print (arguments);
    speech_recognition_proc=subprocess.Popen(arguments,creationflags=subprocess.CREATE_NEW_CONSOLE)
    print ('started speech recognition, pid=',speech_recognition_proc.pid)

def start_llm_processor(mqtt,mosquitto_ip,llm_model,llm_temperature,llm_max_length):
    sobotify_path=os.path.dirname(os.path.abspath(__file__))
    arguments=[sys.executable,os.path.join(sobotify_path,'tools','llm_processor.py')]
    if mqtt== True: 
       arguments.extend(('--mqtt',"on"))
    arguments.extend(('--mosquitto_ip',mosquitto_ip))
    arguments.extend(('--llm_model',llm_model))
    arguments.extend(('--llm_temperature',str(llm_temperature)))
    arguments.extend(('--llm_max_length',str(llm_max_length)))  
    print (arguments);
    llm_proc=subprocess.Popen(arguments,creationflags=subprocess.CREATE_NEW_CONSOLE)
    print ('started llm processor, pid=',llm_proc.pid)

if __name__ == "__main__":
    parser=argparse.ArgumentParser(prog='sobotify',description='The Social Robot Framework')
    parser.add_argument('-a',default="false",action="store_true",help='start analyze tool')
    parser.add_argument('-m',default="false",action="store_true",help='start mosquitto')
    parser.add_argument('-r',default="false",action="store_true",help='start robot controller')
    parser.add_argument('-v',default="false",action="store_true",help='start speech recognition')
    parser.add_argument('-l',default="false",action="store_true",help='start llm processor')
    parser.add_argument('--mosquitto_ip',default='127.0.0.1',help='ip address of the mosquitto server')
    parser.add_argument('--mosquitto_path',default='',help='path to directory of the mosquitto executable')
    parser.add_argument('--robot_name',default='stickman',help='name of the robot (stickman,pepper,nao)')
    parser.add_argument('--robot_ip',default='127.0.0.1',help='ip address of the robot')
    parser.add_argument('--robot_conda_environment',default="sobotify",help='conda environment used for robot')
    parser.add_argument('--message',default='Hello World',help='message to be spoken by the robot')
    parser.add_argument('--video_file',default='video.mp4',help='path to the video input file')
    parser.add_argument('--vosk_model_path',default=os.path.join(os.path.expanduser("~"),".sobotify","vosk","models"),help='path to vosk_model')
    parser.add_argument('--vosk_keyword',default='apple tree',help='key word to activate vosk listener')
    parser.add_argument('--data_path',default=os.path.join(os.path.expanduser("~"),".sobotify","data"),help='path to movement/speech data')
    parser.add_argument('--language',default="english",help='choose language (english,german)')
    parser.add_argument('--min_speech_speed',default=70,help='minimum speech speed of robot')
    parser.add_argument('--max_speech_speed',default=110,help='maximum speech speed of robot')
    parser.add_argument('--ffmpeg_path',default=os.path.join(os.path.expanduser("~"),".sobotify","ffmpeg","bin"),help='directory path to ffmpeg tools (bin directory)')
    parser.add_argument('--sound_device',default=0,type=int,help='number of sound device, can be found with: import sounddevice;sounddevice.query_devices()')
    parser.add_argument('--llm_model',default='EleutherAI/llm-j-6B',help='name of the llm model (e.g. EleutherAI/llm-j-6B or bigscience/bloom-560m)')
    parser.add_argument('--llm_temperature',default=0.5,type=float,help='temperature value for the llm model (between 0.0 and 1.0)')
    parser.add_argument('--llm_max_length',default=100,type=int,help='maximum length of the generated text')
    args=parser.parse_args()


    if platform.system()=="Windows": 
        if args.mosquitto_path=="":
            args.mosquitto_path="C:\Program Files\mosquitto"
        full_mosquitto_path=args.mosquitto_path+"\mosquitto.exe" 
    elif platform.system()=="Linux": 
        if args.mosquitto_path=="":
            full_mosquitto_path="mosquitto"
        else :
            full_mosquitto_path=args.mosquitto_path+"/mosquitto" 

    if args.a==True:
       start_analyze(args.video_file,args.data_path,args.robot_name,args.ffmpeg_path,args.vosk_model_path,args.language)
    if args.m==True:
       start_mosquitto(full_mosquitto_path)
    if args.r==True:
        start_robotcontrol(args.m,args.mosquitto_ip,args.robot_name,args.robot_ip,args.robot_conda_environment,args.data_path,args.language,args.min_speech_speed,args.max_speech_speed, args.message)
    if args.v==True:
        start_speech_recognition(args.m,args.mosquitto_ip,args.vosk_model_path,args.language,args.vosk_keyword,args.sound_device)
    if args.l==True:
        start_llm_processor(args.m,args.mosquitto_ip,args.llm_model,args.llm_temperature,args.llm_max_length)
 