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
show_video_default       = "on"            # show video during emotion detection
frame_rate_default       = 1               # frame rate for emotion detection
cam_device_default       = "0"             # camera device for emotion detection
text_default             = ""              # text to checked for grammar
URL_default              = "http://localhost:8081/v2/check" # LanguageTool server URL
languagetool_path_default = os.path.join(os.path.expanduser("~"),".sobotify","languagetool")
java_path_default         = os.path.join(os.environ["JAVA_HOME"],"bin")


if os.path.isfile(os.path.join(os.path.expanduser("~"),"miniconda3","condabin","conda.bat")):
	conda_exe=os.path.join(os.path.expanduser("~"),"miniconda3","condabin","conda.bat")
elif os.path.isfile(os.path.join(os.path.expanduser("~"),"AppData","Local","miniconda3","condabin","conda.bat")):
	conda_exe=os.path.join(os.path.expanduser("~"),"AppData","Local","miniconda3","condabin","conda.bat")
else :
	print ("Cannot find Conda executable path. Abort")
	exit()

class sobotify (object) :

    def __init__(self,start_mqtt_server=True,app_name="app",start_mqtt_client=True,mosquitto_path=mosquitto_path_default,mosquitto_ip=mosquitto_ip_default,debug=False) :
        print ("init sobotify")
        self.debug=debug
        self.analyze_proc=0
        self.mosquitto_proc=0
        self.rocontrol_proc=0
        self.speech_recognition_proc=0
        self.llm_proc=0
        self.robot_done_flag=False
        self.statement_pending=False
        self.statement = ""
        self.dominant_emotion_available=False
        self.dominant_emotion = ""
        self.grammar_checking_result_available=False
        self.grammar_checking_result = ""
        self.start_mqtt_client=start_mqtt_client
        self.init_speech_recognition_done_flag = False
        self.init_chatbot_done_flag = False
        self.init_robot_done_flag = False
        self.init_emotion_detection_done_flag = False 
        self.init_grammar_checking_done_flag =True

        if start_mqtt_server==True:
            self.start_mosquitto(mosquitto_path)
        if self.start_mqtt_client==True :
            from sobotify.commons.mqttclient import mqttClient
            self.mqtt_client = mqttClient(mosquitto_ip,app_name)

    def subscribe_chatbot(self,callback):
         self.mqtt_client.subscribe("llm/reply",callback)

    def subscribe_listener(self,callback):
         self.mqtt_client.subscribe("speech-recognition/statement",callback)

    def store_statement(self,statement) :
        self.statement = statement
        print("got statement from human: "+ self.statement)
        self.statement_pending=True

    def robot_done(self,message) :
        print("got info robot is done: "+ message)
        self.robot_done_flag=True

    def wait_for_robot(self):
        self.mqtt_client.subscribe("robot/done",self.robot_done)
        print("waiting for robot to finish ...")             
        while not self.robot_done_flag==True:
            time.sleep(1)   
        self.robot_done_flag=False
        print(" ... done")             

    def listen(self,listen_to_keyword=False,keyword=keyword_default,detect_emotion=False):
        if (listen_to_keyword==True) :
            self.mqtt_client.publish("speech-recognition/control/record/listen_to_keyword",keyword)
        else :
            if detect_emotion:
                self.detect(command="start")
            self.mqtt_client.subscribe("speech-recognition/statement",self.store_statement)
            self.mqtt_client.publish("speech-recognition/control/record/start","")
            while not self.statement_pending:
                time.sleep(1)    
            self.statement_pending=False
            if detect_emotion:
                emotion=self.detect(command="stop")
                return self.statement, emotion
            else:
                return self.statement

    def speak(self,message,speed=0,detect_emotion=False):
        if detect_emotion:
            self.detect(command="start")
        if  (speed==0) :
            self.mqtt_client.publish("robot/control/set-min-speed",min_speech_speed_default)
            self.mqtt_client.publish("robot/control/set-max-speed",max_speech_speed_default)
        else :
            self.mqtt_client.publish("robot/control/set-speed",speed)
        self.mqtt_client.publish("robot/speak-and-gesture",message)
        self.wait_for_robot()
        if detect_emotion:
            emotion=self.detect(command="stop")
            return emotion
    
    def chat(self,message):
         self.mqtt_client.publish("llm/query",message)

    def store_dominant_emotion(self,dominant_emotion) :
        self.dominant_emotion = dominant_emotion
        print("got dominant_emotion: "+ self.dominant_emotion)
        self.dominant_emotion_available=True

    def detect(self,command,type="emotion"):
        if command=="start":
            if type=="emotion":
                self.mqtt_client.publish("emotion_detection/start")
        elif command=="stop":
            if type=="emotion":
                self.mqtt_client.publish("emotion_detection/stop")
                self.mqtt_client.subscribe("emotion_detection/dominant_emotion",self.store_dominant_emotion)
                while not self.dominant_emotion_available:
                    time.sleep(1)    
                self.dominant_emotion_available=False
                return self.dominant_emotion

    def store_grammar_check_result(self,result) :
        self.grammar_checking_result = result
        print("got grammar check result: "+ self.grammar_checking_result)
        self.grammar_checking_result_available=True

    def grammar_check(self,text):
        self.mqtt_client.publish("grammar_checking/text",text)
        self.mqtt_client.subscribe("grammar_checking/result",self.store_grammar_check_result)
        while not self.grammar_checking_result_available:
            time.sleep(1)    
        self.grammar_checking_result_available=False
        return self.grammar_checking_result

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


    ########################################################################################################
    def init_robot_done(self,message) :
        print("got init done: "+ message)
        self.init_robot_done_flag =True

    def wait_for_init_robot_done(self):
        self.mqtt_client.subscribe("robot/status/init-done",self.init_robot_done)
        print("waiting for robot to finish initalization ...")             
        while not self.init_robot_done_flag==True:
            time.sleep(1)   
        print(" ... done")  

    def start_robotcontroller(self,mqtt=True,mosquitto_ip=mosquitto_ip_default,robot_name=robot_name_default,robot_ip=robot_ip_default,
                           robot_conda_env=robot_conda_env_default,data_path=data_path_default,language=language_default,
                           min_speech_speed=min_speech_speed_default,max_speech_speed=max_speech_speed_default,message=message_default) :
        sobotify_path=os.path.dirname(os.path.abspath(__file__))
        script_path=os.path.join(sobotify_path,'robotcontrol','robotcontrol.py')
        if robot_conda_env == "" :
            if robot_name.lower() == "pepper" or robot_name.lower() == "nao" :
                robot_conda_env = "sobotify_naoqi"
        if not robot_conda_env == "" :
            arguments=[conda_exe]
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
        if mqtt== True: 
            self.wait_for_init_robot_done()

    ########################################################################################################
    def init_speech_recognition_done(self,message) :
        print("got init done: "+ message)
        self.init_speech_recognition_done_flag =True

    def wait_for_init_speech_recognition_done(self):
        self.mqtt_client.subscribe("speech-recognition/status/init-done",self.init_speech_recognition_done)
        print("waiting for speech recognition to finish initalization ...")             
        while not self.init_speech_recognition_done_flag==True:
            time.sleep(1)   
        print(" ... done")           

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
        if mqtt== True: 
            self.wait_for_init_speech_recognition_done()

    ########################################################################################################
    def init_chatbot_done(self,message) :
        print("got init done: "+ message)
        self.init_chatbot_done_flag =True

    def wait_for_init_chatbot_done(self):
        self.mqtt_client.subscribe("llm/status/init-done",self.init_chatbot_done)
        print("waiting for chatbot to finish initalization ...")             
        while not self.init_chatbot_done_flag==True:
            time.sleep(1)   
        print(" ... done")  
    
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
        if mqtt== True: 
            self.wait_for_init_chatbot_done()

    ########################################################################################################
    def init_emotion_detection_done(self,message) :
        print("got init done: "+ message)
        self.init_emotion_detection_done_flag =True

    def wait_for_init_emotion_detection_done(self):
        self.mqtt_client.subscribe("emotion_detection/status/init-done",self.init_emotion_detection_done)
        print("waiting for emotion_detection to finish initalization ...")             
        while not self.init_emotion_detection_done_flag==True:
            time.sleep(1)   
        print(" ... done")  
    
    def start_emotion_detection(self,mqtt=True,mosquitto_ip=mosquitto_ip_default,robot_name=robot_name_default,robot_ip=robot_ip_default,cam_device=cam_device_default,frame_rate=frame_rate_default,show_video=show_video_default):
        sobotify_path=os.path.dirname(os.path.abspath(__file__))
        script_path=os.path.join(sobotify_path,'tools','emotion_detection.py')
        arguments=[sys.executable,script_path]
        if mqtt== True: 
            arguments.extend(('--mqtt',"on"))
        arguments.extend(('--mosquitto_ip',mosquitto_ip))
        arguments.extend(('--robot_name',robot_name))
        arguments.extend(('--robot_ip',robot_ip))
        arguments.extend(('--cam_device',cam_device))
        arguments.extend(('--frame_rate',str(frame_rate)))
        arguments.extend(('--show_video',show_video))
        if self.debug==True:
            print (*arguments)
        self.emotion_detection_proc=subprocess.Popen(arguments,creationflags=subprocess.CREATE_NEW_CONSOLE)
        print ('started emotion detection, pid=',self.emotion_detection_proc.pid)
        if mqtt== True: 
            self.wait_for_init_emotion_detection_done()

    ########################################################################################################
    def init_grammar_checking_done(self,message) :
        print("got init done: "+ message)
        self.init_grammar_checking_done_flag =True

    def wait_for_init_grammar_checking_done(self):
        self.mqtt_client.subscribe("grammar_checking/status/init-done",self.init_grammar_checking_done)
        print("waiting for grammar_checking to finish initalization ...")             
        while not self.init_grammar_checking_done_flag==True:
            time.sleep(1)   
        print(" ... done")  
    
    def start_grammar_checking(self,mqtt=True,mosquitto_ip=mosquitto_ip_default,languagetool_path=languagetool_path_default,java_path=java_path_default,language=language_default,URL=URL_default,text=text_default):
        sobotify_path=os.path.dirname(os.path.abspath(__file__))
        script_path=os.path.join(sobotify_path,'tools','grammar_checking.py')
        arguments=[sys.executable,script_path]
        if mqtt== True: 
            arguments.extend(('--mqtt',"on"))
        arguments.extend(('--mosquitto_ip',mosquitto_ip))
        arguments.extend(('--language',language))
        arguments.extend(('--languagetool_path',languagetool_path))
        arguments.extend(('--java_path',java_path))
        arguments.extend(('--languagetool_url',URL))
        arguments.extend(('--text',text))
        if self.debug==True:
            print (*arguments)
        self.grammar_checking_proc=subprocess.Popen(arguments,creationflags=subprocess.CREATE_NEW_CONSOLE)
        print ('started grammar checking, pid=',self.grammar_checking_proc.pid)
        if mqtt== True: 
            self.wait_for_init_grammar_checking_done()
    ########################################################################################################

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

def handler2(signal_received, frame):
    # Handle cleanup here
    print('SIGINT or CTRL-C detected. Exiting gracefully')
    sobot.terminate()
    exit(0)

if __name__ == "__main__":
    signal.signal (signal.SIGINT,handler)
    signal.signal (signal.SIGTERM,handler2)
    
    parser=argparse.ArgumentParser(prog='sobotify',description='The Social Robot Framework')
    parser.add_argument('-d',default="false",action="store_true",help='debug')
    parser.add_argument('-e',default="false",action="store_true",help='start gesture/speech extract tool')
    parser.add_argument('-m',default="false",action="store_true",help='start mosquitto')
    parser.add_argument('-r',default="false",action="store_true",help='start robot controller')
    parser.add_argument('-l',default="false",action="store_true",help='start listener (speech recognition)')
    parser.add_argument('-c',default="false",action="store_true",help='start chatbot')
    parser.add_argument('-f',default="false",action="store_true",help='start emotion detection')
    parser.add_argument('-g',default="false",action="store_true",help='start grammar checker')
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
    parser.add_argument('--text',default='',help='Text to be checked by the grammar checker')
    parser.add_argument('--languagetool_path',default=os.path.join(os.path.expanduser("~"),".sobotify","languagetool"),help='directory path to LanguageTool')
    parser.add_argument('--java_path',default=os.path.join(os.environ["JAVA_HOME"],"bin"),help='directory path to java executable')
    parser.add_argument('--languagetool_url',default=URL_default,help='URL of LanguageTool server')
    parser.add_argument('--cam_device',default='0',help='camera device name or number for emotion detection')
    parser.add_argument('--frame_rate',default=1,type=float,help='frame rate for emotion detection')
    parser.add_argument('--show_video',default="on",help='enable/disable video output of emotion detection on screen')
    args=parser.parse_args()


    sobot = sobotify(start_mqtt_server=args.m,start_mqtt_client=False, mosquitto_path=args.mosquitto_path,debug=args.d)

    if args.e==True:
        sobot.start_extract(args.video_file,args.data_path,args.robot_name,args.ffmpeg_path,args.vosk_model_path,args.language)
    if args.r==True:
        sobot.start_robotcontroller(args.m,args.mosquitto_ip,args.robot_name,args.robot_ip,args.robot_conda_env,args.data_path,args.language,args.min_speech_speed,args.max_speech_speed, args.message)
    if args.l==True:
        sobot.start_listener(args.m,args.mosquitto_ip,args.vosk_model_path,args.language,args.keyword,args.sound_device)
    if args.c==True:
        sobot.start_chatbot(args.m,args.mosquitto_ip,args.llm_model,args.llm_temperature,args.llm_max_length)
    if args.f==True:
        sobot.start_emotion_detection(args.m,args.mosquitto_ip,args.robot_name,args.robot_ip,args.cam_device,args.frame_rate,args.show_video)
    if args.g==True:
        sobot.start_grammar_checking(args.m,args.mosquitto_ip,args.languagetool_path,args.java_path,args.language,args.languagetool_url,args.text)

    while(True):
        time.sleep(1000)