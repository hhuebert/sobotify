import os
import sys
import argparse
import subprocess
import time
import platform
import signal
import inspect
from datetime import datetime
import psutil

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
llm_name_default         = 'dummy'         # name of the llm api
llm_options_default      = ''              # llm options
show_video_default       = "on"            # show video during emotion detection
show_stickman_default    = "on"            # show stickman during emotion detection
frame_rate_default       = 1               # frame rate for emotion detection
cam_device_default       = "0"             # camera device for emotion detection
text_default             = ""              # text to checked for grammar
URL_default              = "http://localhost:8081/v2/check" # LanguageTool server URL
languagetool_path_default = os.path.join(os.path.expanduser("~"),".sobotify","languagetool")
java_path_default         = os.environ.get("JAVA_HOME","")
if java_path_default: 
    java_path_default     = os.path.join(java_path_default,"bin")
robot_options_default     = ""

if os.path.isfile(os.path.join(os.path.expanduser("~"),"miniconda3","condabin","conda.bat")):
	conda_exe=os.path.join(os.path.expanduser("~"),"miniconda3","condabin","conda.bat")
elif os.path.isfile(os.path.join(os.path.expanduser("~"),"AppData","Local","miniconda3","condabin","conda.bat")):
	conda_exe=os.path.join(os.path.expanduser("~"),"AppData","Local","miniconda3","condabin","conda.bat")
else :
	print ("Cannot find Conda executable path. Abort")
	exit()

class sobotify (object) :

    def __init__(self,start_mqtt_server=True,app_name="app",start_mqtt_client=True,mosquitto_path=mosquitto_path_default,mosquitto_ip=mosquitto_ip_default,debug=False,log=False) :
        print ("init sobotify")
        self.debug=debug
        self.analyze_proc=0
        self.mosquitto_proc=0
        self.rocontrol_proc=0
        self.rointerface_proc=0 
        self.speech_recognition_proc=0
        self.teleoperator_proc=0
        self.logging_server_proc=0
        self.llm_proc=0
        self.statement_pending=False
        self.statement = ""
        self.dominant_emotion_available=False
        self.dominant_emotion = ""
        self.grammar_checking_result_available=False
        self.grammar_checking_result = ""
        self.start_mqtt_client=start_mqtt_client
        self.log_enabled=log
        self.language=language_default
        self.sound_device=sound_device_default
        self.partial_text_pending=False

        if start_mqtt_server==True:
            self.start_mosquitto(mosquitto_path)
        if self.start_mqtt_client==True :
            from sobotify.commons.mqttclient import mqttClient
            self.mqtt_client = mqttClient(mosquitto_ip,app_name)
        if self.log_enabled==True :
            self.start_logging_server()
            from sobotify.tools.logger import LoggerClient
            self.logger=LoggerClient(self.mqtt_client)

    def stop_service(self,service):
        if not service==None: 
            try:
                project_process=psutil.Process(service.pid)
                project_children=project_process.children(recursive=True)
                print(project_children)
                for child in project_children:
                    try:
                        #print(f"kill process {child.name} with pid: {child.pid}")
                        child.kill()
                    except:
                        #print(f"process {child.name} with pid: {child.pid} already finished")					
                        pass
                try:
                    #print(f"kill process with pid: {self.project_proc.pid}")
                    service.kill()
                except:
                    #print(f"process with pid: {self.project_proc.pid} already finished")					
                    pass
            except:
                #print(f"process with pid: {self.project_proc.pid} does not exist (anymore)")					
                pass
        else:
            #print("no process to kill")
            pass
        service=None

    def log(self,message,topic=""):
        if self.log_enabled==True :
            self.logger.message(message,topic,level=2)

    def subscribe_face_detection(self,callback):
        self.mqtt_client.subscribe("robot_control/command/follow_head",callback)

    def subscribe_face_name(self,callback):
        self.mqtt_client.subscribe("facial_processing/name",callback)

    def subscribe_chatbot(self,callback):
         self.mqtt_client.subscribe("llm/reply",callback)

    def subscribe_listener(self,callback):
         self.mqtt_client.subscribe("speech-recognition/statement",callback)

    def store_statement(self,statement) :
        self.statement = statement
        print("got statement from human: "+ self.statement)
        self.statement_pending=True

    def store_partial_text(self,partial_text) :
        self.partial_text = partial_text
        #print("got statement from human: "+ self.statement)
        self.partial_text_pending=True

    def reply_from_listener(self):
            self.mqtt_client.subscribe("speech-recognition/partial-text",self.store_partial_text)
            timestamp=datetime.now()
            while not self.statement_pending:
                time.sleep(1)
                if self.partial_text_pending==True:
                    timestamp=datetime.now()
                    self.partial_text_pending=False
                waiting_time=(datetime.now()-timestamp).total_seconds()
                print ("waiting time=",waiting_time)
                if waiting_time > 12:  ## service not responding ==> restart
                    self.stop_service(self.speech_recognition_proc)
                    self.start_listener(language=self.language)
                    time.sleep(0.5)
                    if self.language=="english":
                        self.speak("Sorry, I couldn't listen to you. Could you please say that again?")
                    if self.language=="german":
                        self.speak("Entschuldige, leider konnte ich dir nicht zuhören. Kannst du das bitte wiederholen?")
                    self.mqtt_client.publish("speech-recognition/control/record/start","")
                    return False
            return True

    def listen(self,listen_to_keyword=False,keyword=keyword_default,detect_emotion=False):
        if (listen_to_keyword==True) :
            self.mqtt_client.publish("speech-recognition/control/record/listen_to_keyword",keyword)
        else :
            if detect_emotion:
                self.detect(command="start")
            self.mqtt_client.subscribe("speech-recognition/statement",self.store_statement)
            self.mqtt_client.publish("speech-recognition/control/record/start","")
            while not self.reply_from_listener():
                time.sleep(0.2)
            self.statement_pending=False
            if detect_emotion:
                emotion=self.detect(command="stop")
                return self.statement, emotion
            else:
                return self.statement

    def speak(self,message,gesture="",speed=0,detect_emotion=False):
        if detect_emotion:
            self.detect(command="start")
        if  (speed==0) :
            self.mqtt_client.publish("robot_control/command/set-min-speed",min_speech_speed_default)
            self.mqtt_client.publish("robot_control/command/set-max-speed",max_speech_speed_default)
        else :
            self.mqtt_client.publish("robot_control/command/set-speed",speed)
        if gesture:
            message=gesture+"|"+message
        self.mqtt_client.publish("robot_control/command/speak-and-gesture",message)
        print("waiting for robot to finish ...")             
        self.mqtt_client.wait_for("robot_control/status/done")
        print(" ... done")             
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
                self.mqtt_client.publish("facial_processing/start")
        elif command=="stop":
            if type=="emotion":
                self.mqtt_client.publish("facial_processing/stop")
                self.mqtt_client.subscribe("facial_processing/dominant_emotion",self.store_dominant_emotion)
                while not self.dominant_emotion_available:
                    time.sleep(1)    
                self.dominant_emotion_available=False
                return self.dominant_emotion

    def teleoperate(self,timeout=10,blocking=True):
        self.mqtt_client.publish("teleoperator/command/start")
        if blocking==True:
            time.sleep(timeout)
            self.mqtt_client.publish("teleoperator/command/stop")

    def stop_teleoperation(self):
        self.mqtt_client.publish("teleoperator/command/stop")

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
                      ffmpeg_path=ffmpeg_path_default,vosk_model_path=vosk_model_path_default,language=language_default,show_video=show_video_default):
        sobotify_path=os.path.dirname(os.path.abspath(__file__))
        arguments=[sys.executable,os.path.join(sobotify_path,'tools','extract','extract.py')]
        arguments.extend(('--video_file',video_file))
        arguments.extend(('--robot_name',robot_name))
        arguments.extend(('--ffmpeg_path',ffmpeg_path))
        arguments.extend(('--vosk_model_path',vosk_model_path))  
        arguments.extend(('--data_path',data_path))
        arguments.extend(('--language',language))
        arguments.extend(('--show_video',show_video))
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
            creationflags=subprocess.CREATE_NEW_CONSOLE
        else:
            creationflags=subprocess.CREATE_NO_WINDOW
        self.mosquitto_proc=subprocess.Popen(arguments,stdout=subprocess.PIPE, creationflags=creationflags)
        time.sleep(3)
        print ('started mosquitto, pid=',self.mosquitto_proc.pid)

   ########################################################################################################
    def start_teleoperator(self,mqtt=True,mosquitto_ip=mosquitto_ip_default,robot_name=robot_name_default,cam_device=cam_device_default,frame_rate=frame_rate_default,show_video=show_video_default,show_stickman=show_stickman_default):
        sobotify_path=os.path.dirname(os.path.abspath(__file__))
        script_path=os.path.join(sobotify_path,'tools','teleoperator.py')
        arguments=[sys.executable,script_path]
        if mqtt== True: 
            arguments.extend(('--mqtt',"on"))
        arguments.extend(('--mosquitto_ip',mosquitto_ip))
        arguments.extend(('--robot_name',robot_name))
        arguments.extend(('--cam_device',cam_device))
        arguments.extend(('--frame_rate',str(frame_rate)))
        arguments.extend(('--show_video',show_video))
        arguments.extend(('--show_stickman',show_stickman))
        if self.debug==True:
            print (*arguments)
            creationflags=subprocess.CREATE_NEW_CONSOLE
        else:
            creationflags=subprocess.CREATE_NO_WINDOW
        self.teleoperator_proc=subprocess.Popen(arguments,creationflags=creationflags)
        print ('started teleoperator, pid=',self.teleoperator_proc.pid)
        if mqtt== True: 
            print("waiting for teleoperator to finish initalization ...")  
            self.mqtt_client.wait_for("teleoperator/status/init-done")
            print(" ... done")      

    ########################################################################################################
    def start_logging_server(self,mqtt=True,mosquitto_ip=mosquitto_ip_default):
        sobotify_path=os.path.dirname(os.path.abspath(__file__))
        script_path=os.path.join(sobotify_path,'tools','logger.py')
        arguments=[sys.executable,script_path]
        if mqtt== True: 
            arguments.extend(('--mqtt',"on"))
        arguments.extend(('--mosquitto_ip',mosquitto_ip))
        if self.debug==True:
            print (*arguments)
            creationflags=subprocess.CREATE_NEW_CONSOLE
        else:
            creationflags=subprocess.CREATE_NO_WINDOW
        self.logging_server_proc=subprocess.Popen(arguments,creationflags=creationflags)
        print ('started logging server, pid=',self.logging_server_proc.pid)
        if mqtt== True: 
            print("waiting for logging server to finish initalization ...")  
            self.mqtt_client.wait_for("logging_server/status/init-done")
            print(" ... done")   

    ########################################################################################################
    def start_robotinterface(self,mqtt=True,mosquitto_ip=mosquitto_ip_default,robot_name=robot_name_default,robot_ip=robot_ip_default,
                           robot_options=robot_options_default, language=language_default,min_speech_speed=min_speech_speed_default,cam_device=cam_device_default,sound_device=sound_device_default,robot_conda_env=robot_conda_env_default) :
        sobotify_path=os.path.dirname(os.path.abspath(__file__))
        script_path=os.path.join(sobotify_path,'robots','robots.py')
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
        arguments.extend(('--robot_ip',robot_ip))
        arguments.extend(('--robot_options','"'+robot_options+'"'))
        arguments.extend(('--language',language))
        arguments.extend(('--speed',str(min_speech_speed)))
        arguments.extend(('--cam_device',cam_device))
        arguments.extend(('--sound_device',str(sound_device)))         
        if self.debug==True:
            print (*arguments)
            creationflags=subprocess.CREATE_NEW_CONSOLE
        else:
            creationflags=subprocess.CREATE_NO_WINDOW
        self.rointerface_proc=subprocess.Popen(arguments,creationflags=creationflags)
        #rointerface_proc=subprocess.Popen(arguments)
        print ('started robot interface, pid=',self.rointerface_proc.pid)
        if mqtt== True: 
            print("waiting for robot interface to finish initialization ...")  
            self.mqtt_client.wait_for("robot/status/init-done")
            print(" ... done")   

    ########################################################################################################
    def start_robotcontroller(self,mqtt=True,mosquitto_ip=mosquitto_ip_default,robot_name=robot_name_default,robot_ip=robot_ip_default,
                           robot_options=robot_options_default,cam_device=cam_device_default,sound_device=sound_device_default,robot_conda_env=robot_conda_env_default,data_path=data_path_default,language=language_default,
                           min_speech_speed=min_speech_speed_default,max_speech_speed=max_speech_speed_default,message=message_default) :
        self.start_robotinterface(mqtt,mosquitto_ip,robot_name,robot_ip,robot_options,language,min_speech_speed,cam_device,sound_device,robot_conda_env)
        sobotify_path=os.path.dirname(os.path.abspath(__file__))
        script_path=os.path.join(sobotify_path,'tools','robotcontrol','robotcontrol.py')
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
        arguments.extend(('--robot_options','"'+robot_options+'"'))
        arguments.extend(('--data_path',data_path))
        arguments.extend(('--language',language))
        arguments.extend(('--min_speech_speed',str(min_speech_speed)))
        arguments.extend(('--max_speech_speed',str(max_speech_speed)))
        arguments.extend(('--cam_device',cam_device))
        arguments.extend(('--sound_device',str(sound_device)))         
        if self.debug==True:
            print (*arguments)
            creationflags=subprocess.CREATE_NEW_CONSOLE
        else:
            creationflags=subprocess.CREATE_NO_WINDOW
        self.rocontrol_proc=subprocess.Popen(arguments,creationflags=creationflags)
        #rocontrol_proc=subprocess.Popen(arguments)
        print ('started robot controller, pid=',self.rocontrol_proc.pid)
        if mqtt== True: 
            print("waiting for robot controller to finish initialization ...")  
            self.mqtt_client.wait_for("robot_control/status/init-done")
            print(" ... done")   

    ########################################################################################################
    def start_listener(self,mqtt=True,mosquitto_ip=mosquitto_ip_default,vosk_model_path=vosk_model_path_default,language=language_default,
                                 keyword=keyword_default):
        self.language=language
        sobotify_path=os.path.dirname(os.path.abspath(__file__))
        script_path=os.path.join(sobotify_path,'tools','speech_recognition.py')
        arguments=[sys.executable,script_path]
        if mqtt== True: 
            arguments.extend(('--mqtt',"on"))
        arguments.extend(('--mosquitto_ip',mosquitto_ip))
        arguments.extend(('--vosk_model_path',vosk_model_path))
        arguments.extend(('--language',language))
        arguments.extend(('--keyword',keyword))
        if self.debug==True:
            print (*arguments)
            creationflags=subprocess.CREATE_NEW_CONSOLE
        else:
            creationflags=subprocess.CREATE_NO_WINDOW
        self.speech_recognition_proc=subprocess.Popen(arguments,creationflags=creationflags)
        print ('started speech recognition, pid=',self.speech_recognition_proc.pid)
        if mqtt== True: 
            print("waiting for speech recognition to finish initalization ...")  
            self.mqtt_client.wait_for("speech-recognition/status/init-done")
            print(" ... done")  

    ########################################################################################################
    def start_chatbot(self,mqtt=True,mosquitto_ip=mosquitto_ip_default,llm_name=llm_name_default,
                      llm_options=llm_options_default):
        sobotify_path=os.path.dirname(os.path.abspath(__file__))
        script_path=os.path.join(sobotify_path,'tools','chatbot.py')
        arguments=[sys.executable,script_path]
        if mqtt== True: 
            arguments.extend(('--mqtt',"on"))
        arguments.extend(('--mosquitto_ip',mosquitto_ip))
        arguments.extend(('--llm_name',llm_name))
        arguments.extend(('--llm_options','"'+llm_options+'"'))

        if self.debug==True:
            print (*arguments)
            creationflags=subprocess.CREATE_NEW_CONSOLE
        else:
            creationflags=subprocess.CREATE_NO_WINDOW
        self.llm_proc=subprocess.Popen(arguments,creationflags=creationflags)
        print ('started chatbot, pid=',self.llm_proc.pid)
        if mqtt== True: 
            print("waiting for chatbot to finish initalization ...")  
            self.mqtt_client.wait_for("llm/status/init-done")
            print(" ... done")  

    ######################################################################################################## 
    def start_facial_processing(self,mqtt=True,mosquitto_ip=mosquitto_ip_default,robot_name=robot_name_default,robot_ip=robot_ip_default,cam_device=cam_device_default,frame_rate=frame_rate_default,show_video=show_video_default):
        sobotify_path=os.path.dirname(os.path.abspath(__file__))
        script_path=os.path.join(sobotify_path,'tools','facial_processing.py')
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
            creationflags=subprocess.CREATE_NEW_CONSOLE
        else:
            creationflags=subprocess.CREATE_NO_WINDOW
        self.facial_processing_proc=subprocess.Popen(arguments,creationflags=creationflags)
        print ('started facial processing, pid=',self.facial_processing_proc.pid)
        if mqtt== True: 
            print("waiting for facial_processing to finish initalization ...")  
            self.mqtt_client.wait_for("facial_processing/status/init-done")
            print(" ... done")  

    ########################################################################################################   
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
            creationflags=subprocess.CREATE_NEW_CONSOLE
        else:
            creationflags=subprocess.CREATE_NO_WINDOW
        self.grammar_checking_proc=subprocess.Popen(arguments,creationflags=creationflags)
        print ('started grammar checking, pid=',self.grammar_checking_proc.pid)
        if mqtt== True: 
            print("waiting for grammar_checking to finish initalization ...")  
            self.mqtt_client.wait_for("grammar_checking/status/init-done")
            print(" ... done")  

    ########################################################################################################
    def terminate(self):
        if not self.analyze_proc==0: self.analyze_proc.kill()
        if not self.mosquitto_proc==0: self.mosquitto_proc.kill()
        if not self.speech_recognition_proc==0: self.speech_recognition_proc.kill()
        if not self.llm_proc==0: self.llm_proc.kill()
        if not self.rocontrol_proc==0: self.rocontrol_proc.kill()
        if not self.rointerface_proc==0: self.rointerface_proc.kill()
        if not self.teleoperator_proc==0: self.teleoperator_proc.kill()
        if not self.logging_server_proc==0: self.logging_server_proc.kill()

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
    parser.add_argument('-f',default="false",action="store_true",help='start facial processing')
    parser.add_argument('-g',default="false",action="store_true",help='start grammar checker')
    parser.add_argument('--mosquitto_ip',default='127.0.0.1',help='ip address of the mosquitto server')
    parser.add_argument('--mosquitto_path',default='',help='path to directory of the mosquitto executable')
    parser.add_argument('--robot_name',default='stickman',help='name of the robot (stickman,pepper,nao)')
    parser.add_argument('--robot_ip',default='127.0.0.1',help='ip address of the robot')
    parser.add_argument('--robot_options',default='',help='robot specific options')
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
    parser.add_argument('--llm_name',default="dummy",help='name of llm api')
    parser.add_argument('--llm_options',default="",help='options for llm')
    parser.add_argument('--text',default='',help='Text to be checked by the grammar checker')
    parser.add_argument('--languagetool_path',default=os.path.join(os.path.expanduser("~"),".sobotify","languagetool"),help='directory path to LanguageTool')
    parser.add_argument('--java_path',default=os.path.join(os.environ["JAVA_HOME"],"bin"),help='directory path to java executable')
    parser.add_argument('--languagetool_url',default=URL_default,help='URL of LanguageTool server')
    parser.add_argument('--cam_device',default='0',help='camera device name or number for emotion detection')
    parser.add_argument('--frame_rate',default=1,type=float,help='frame rate for emotion detection')
    parser.add_argument('--show_video',default="on",help='enable/disable video output of emotion detection or gesture extraction on screen')
    args=parser.parse_args()


    sobot = sobotify(start_mqtt_server=args.m,start_mqtt_client=False, mosquitto_path=args.mosquitto_path,debug=args.d)

    if args.e==True:
        sobot.start_extract(args.video_file,args.data_path,args.robot_name,args.ffmpeg_path,args.vosk_model_path,args.language,args.show_video)
    if args.r==True:
        sobot.start_robotcontroller(args.m,args.mosquitto_ip,args.robot_name,args.robot_ip,args.robot_options,args.cam_device,args.sound_device,args.robot_conda_env,args.data_path,args.language,args.min_speech_speed,args.max_speech_speed, args.message)
    if args.l==True:
        sobot.start_listener(args.m,args.mosquitto_ip,args.vosk_model_path,args.language,args.keyword)
    if args.c==True:
        sobot.start_chatbot(args.m,args.mosquitto_ip,args.llm_name,args.llm_options)
    if args.f==True:
        sobot.start_facial_processing(args.m,args.mosquitto_ip,args.robot_name,args.robot_ip,args.cam_device,args.frame_rate,args.show_video)
    if args.g==True:
        sobot.start_grammar_checking(args.m,args.mosquitto_ip,args.languagetool_path,args.java_path,args.language,args.languagetool_url,args.text)

    while(True):
        time.sleep(1000)