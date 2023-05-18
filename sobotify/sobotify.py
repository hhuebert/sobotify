import os
import sys
import argparse
import subprocess
import time
import platform
import signal


mosquitto_ip_default     = '127.0.0.1'      # ip address of the mosquitto server'
mosquitto_path_default   = ''               # path to directory of the mosquitto executable')
robot_name_default       = 'stickman'       # name of the robot (stickman,pepper,nao)')
robot_ip_default         = '127.0.0.1'      # help='ip address of the robot')
robot_conda_env_default  = ""                # conda environment used for robot')
message_default          = '"Hello World"'    # message to be spoken by the robot')
video_file_default       = 'video.mp4'      # path to the video input file')
vosk_model_path_default  = os.path.join(os.path.expanduser("~"),".sobotify","vosk","models") # path to vosk_model')
keyword_default          = 'apple tree'     # key word to activate vosk listener')
data_path_default        = os.path.join(os.path.expanduser("~"),".sobotify","data") # 'path to movement/speech data')
language_default         = 'english'        # choose language (english,german)')
min_speech_speed_default = 70              # minimum speech speed of robot
max_speech_speed_default = 110             # maximum speech speed of robot')
ffmpeg_path_default      = os.path.join(os.path.expanduser("~"),".sobotify","ffmpeg","bin") # directory path to ffmpeg tools (bin directory)
sound_device_default     = 0               # number of sound device, can be found with: import sounddevice;sounddevice.query_devices()')
llm_model_default        = 'EleutherAI/llm-j-6B'  # name of the llm model (e.g. EleutherAI/llm-j-6B or bigscience/bloom-560m)')
llm_temperature_default  = 0.5             # temperature value for the llm model (between 0.0 and 1.0)')
llm_max_length_default   = 100             # maximum length of the generated text')


class sobotify (object) :

    def __init__(self,start_mqtt_server=True,app_name="app",start_mqtt_client=True,mosquitto_path=mosquitto_path_default,mosquitto_ip=mosquitto_ip_default,debug=False) :
        print ("init sobotify")
        self.debug=debug
        self.analyze_proc=0
        self.mosquitto_proc=0
        self.rocontrol_proc=0
        self.speech_recognition_proc=0
        self.llm_proc=0
        if start_mqtt_server==True:
            self.start_mosquitto(mosquitto_path)
        if start_mqtt_client==True :
            from sobotify.commons.mqttclient import mqttClient
            self.mqtt_client = mqttClient(mosquitto_ip,app_name)

    def subscribe_chatbot(self,callback):
         self.mqtt_client.subscribe("llm/reply",callback)

    def subscribe_listener(self,callback):
         self.mqtt_client.subscribe("speech-recognition/statement",callback)

    def speak(self,message):
         self.mqtt_client.publish("robot/speak-and-gesture",message)
    
    def chat(self,message):
         self.mqtt_client.publish("llm/query",message)

    def start_extract(self,video_file=video_file_default,data_path=data_path_default,robot_name=robot_name_default,
                      ffmpeg_path=ffmpeg_path_default,vosk_model_path=vosk_model_path_default,language=language_default):
        sobotify_path=os.path.dirname(os.path.abspath(__file__))
        arguments=[sys.executable,os.path.join(sobotify_path,'tools','extract','extract.py')]
        arguments.extend(('--video_file',video_file))
        arguments.extend(('--robot_name',robot_name))
        arguments.extend(('--ffmpeg_path',ffmpeg_path))
        arguments.extend(('--vosk_model_path',vosk_model_path))  
        arguments.extend(('--data_path',data_path))
        arguments.extend(('--language',language))
        if self.debug==True:
            print (*arguments)
        self.analyze_proc=subprocess.Popen(arguments)
        print ('started gesture/speech analysis, pid=',self.analyze_proc.pid)

    def start_mosquitto(self,mosquitto_path=mosquitto_path_default): 
        if platform.system()=="Windows": 
            if mosquitto_path=="":
                mosquitto_path="C:\Program Files\mosquitto"
            full_mosquitto_path=mosquitto_path+"\mosquitto.exe" 
        elif platform.system()=="Linux": 
            if mosquitto_path=="":
                full_mosquitto_path="mosquitto"
            else :
                full_mosquitto_path=mosquitto_path+"/mosquitto" 
        sobotify_path=os.path.dirname(os.path.abspath(__file__))
        arguments=[full_mosquitto_path]
        arguments.append("-v")
        arguments.extend(('-c',os.path.join(sobotify_path,'tools','mosquitto.conf')))
        if self.debug==True:
            print (*arguments)
        self.mosquitto_proc=subprocess.Popen(arguments,stdout=subprocess.PIPE, creationflags=subprocess.CREATE_NEW_CONSOLE)
        time.sleep(3)
        print ('started mosquitto, pid=',self.mosquitto_proc.pid)

    def start_robotcontroller(self,mqtt=True,mosquitto_ip=mosquitto_ip_default,robot_name=robot_name_default,robot_ip=robot_ip_default,
                           robot_conda_env=robot_conda_env_default,data_path=data_path_default,language=language_default,
                           min_speech_speed=min_speech_speed_default,max_speech_speed=max_speech_speed_default,message=message_default) :
        sobotify_path=os.path.dirname(os.path.abspath(__file__))
        script_path=os.path.join(sobotify_path,'robotcontrol','robotcontrol.py')
        if robot_conda_env == "" :
            if robot_name.lower() == "pepper" or robot_name.lower() == "nao" :
                robot_conda_env = "sobotify_naoqi"
        if not robot_conda_env == "" :
            arguments=[os.path.expanduser("~")+"\miniconda3\condabin\conda.bat"]
            arguments.append("run")
            arguments.extend(('-n',robot_conda_env))
            arguments.append("--no-capture-output")
            arguments.append("python")
            arguments.append(script_path)
        else :
            arguments=[sys.executable,script_path]
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
        if self.debug==True:
            print (*arguments)
        self.rocontrol_proc=subprocess.Popen(arguments,creationflags=subprocess.CREATE_NEW_CONSOLE)
        #rocontrol_proc=subprocess.Popen(arguments)
        print ('started robot controller, pid=',self.rocontrol_proc.pid)

    def start_listener(self,mqtt=True,mosquitto_ip=mosquitto_ip_default,vosk_model_path=vosk_model_path_default,language=language_default,
                                 keyword=keyword_default,sound_device=sound_device_default):
        sobotify_path=os.path.dirname(os.path.abspath(__file__))
        script_path=os.path.join(sobotify_path,'tools','speech_recognition.py')
        arguments=[sys.executable,script_path]
        if mqtt== True: 
            arguments.extend(('--mqtt',"on"))
        arguments.extend(('--mosquitto_ip',mosquitto_ip))
        arguments.extend(('--vosk_model_path',vosk_model_path))
        arguments.extend(('--language',language))
        arguments.extend(('--keyword',keyword))
        arguments.extend(('--sound_device',str(sound_device))) 
        if self.debug==True:
            print (*arguments)
        self.speech_recognition_proc=subprocess.Popen(arguments,creationflags=subprocess.CREATE_NEW_CONSOLE)
        print ('started speech recognition, pid=',self.speech_recognition_proc.pid)

    def start_chatbot(self,mqtt=True,mosquitto_ip=mosquitto_ip_default,llm_model=llm_model_default,
                      llm_temperature=llm_temperature_default,llm_max_length=llm_max_length_default):
        sobotify_path=os.path.dirname(os.path.abspath(__file__))
        script_path=os.path.join(sobotify_path,'tools','chatbot.py')
        arguments=[sys.executable,script_path]
        if mqtt== True: 
            arguments.extend(('--mqtt',"on"))
        arguments.extend(('--mosquitto_ip',mosquitto_ip))
        arguments.extend(('--llm_model',llm_model))
        arguments.extend(('--llm_temperature',str(llm_temperature)))
        arguments.extend(('--llm_max_length',str(llm_max_length)))  
        if self.debug==True:
            print (*arguments)
        self.llm_proc=subprocess.Popen(arguments,creationflags=subprocess.CREATE_NEW_CONSOLE)
        print ('started chatbot, pid=',self.llm_proc.pid)

    def terminate(self):
        if not self.analyze_proc==0: self.analyze_proc.kill()
        if not self.mosquitto_proc==0: self.mosquitto_proc.kill()
        if not self.speech_recognition_proc==0: self.speech_recognition_proc.kill()
        if not self.llm_proc==0: self.llm_proc.kill()
        if not self.rocontrol_proc==0: self.rocontrol_proc.kill()

def handler(signal_received, frame):
    # Handle cleanup here
    print('SIGINT or CTRL-C detected. Exiting gracefully')
    sobot.terminate()
    exit(0)


if __name__ == "__main__":
    signal.signal (signal.SIGINT,handler)
    
    parser=argparse.ArgumentParser(prog='sobotify',description='The Social Robot Framework')
    parser.add_argument('-e',default="false",action="store_true",help='start gesture/speech extract tool')
    parser.add_argument('-m',default="false",action="store_true",help='start mosquitto')
    parser.add_argument('-r',default="false",action="store_true",help='start robot controller')
    parser.add_argument('-l',default="false",action="store_true",help='start listener (speech recognition)')
    parser.add_argument('-c',default="false",action="store_true",help='start chatbot')
    parser.add_argument('--mosquitto_ip',default='127.0.0.1',help='ip address of the mosquitto server')
    parser.add_argument('--mosquitto_path',default='',help='path to directory of the mosquitto executable')
    parser.add_argument('--robot_name',default='stickman',help='name of the robot (stickman,pepper,nao)')
    parser.add_argument('--robot_ip',default='127.0.0.1',help='ip address of the robot')
    parser.add_argument('--robot_conda_env',default="",help='conda environment used for robot')
    parser.add_argument('--message',default='Hello World',help='message to be spoken by the robot')
    parser.add_argument('--video_file',default='video.mp4',help='path to the video input file')
    parser.add_argument('--vosk_model_path',default=os.path.join(os.path.expanduser("~"),".sobotify","vosk","models"),help='path to vosk_model')
    parser.add_argument('--keyword',default='apple tree',help='key word to activate speech recognition')
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


    sobot = sobotify(start_mqtt_server=args.m,start_mqtt_client=False, mosquitto_path=args.mosquitto_path)

    if args.e==True:
        sobot.start_extract(args.video_file,args.data_path,args.robot_name,args.ffmpeg_path,args.vosk_model_path,args.language)
    if args.r==True:
        sobot.start_robotcontroller(args.m,args.mosquitto_ip,args.robot_name,args.robot_ip,args.robot_conda_env,args.data_path,args.language,args.min_speech_speed,args.max_speech_speed, args.message)
    if args.l==True:
        sobot.start_listener(args.m,args.mosquitto_ip,args.vosk_model_path,args.language,args.keyword,args.sound_device)
    if args.c==True:
        sobot.start_chatbot(args.m,args.mosquitto_ip,args.llm_model,args.llm_temperature,args.llm_max_length)
 
    
    while(True):
        time.sleep(1000)