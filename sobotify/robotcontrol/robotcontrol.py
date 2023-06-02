import os
import sys
import argparse
import threading
import csv
import srt
from datetime import datetime
from time import sleep

from sobotify.commons.mqttclient import mqttClient
import sobotify.robotcontrol.data

DEBUG_CALLS=False
DEBUG_SYNC=True
DEBUG_SYNC2=False
DEBUG_TXT_REPLACE=False
speed_factor = 1.0

def getRobot(name,robot_ip) :
        if name=='stickman' :
            import sobotify.robots.stickman.stickman as stickman
            return stickman.speech(),stickman.motion()
        elif name=='pepper' :
            if not (sys.version_info[0]==2 and sys.version_info[1]==7) :
                print("Pepper robot can only be used with Python version 2.7.x (your version is " + str(sys.version_info[0])+"."+str(sys.version_info[1])+")")
                exit()
            import sobotify.robots.pepper.pepper as pepper
            return pepper.speech(robot_ip),pepper.motion(robot_ip)
        elif name=='pepper_sim' :
            import sobotify.robots.pepper.pepper_sim as pepper_sim
            return pepper_sim.speech(),pepper_sim.motion()
        elif name=='nao' :
            if not (sys.version_info[0]==2 and sys.version_info[1]==7) :
                print("Nao robot can only be used with Python version 2.7.x (your version is " + str(sys.version_info[0])+"."+str(sys.version_info[1])+")")
                exit()
            import sobotify.robots.nao.nao as nao
            return nao.speech(robot_ip),nao.motion(robot_ip)
        elif name=='nao_sim' :
            import sobotify.robots.nao.nao_sim as nao_sim
            return nao_sim.speech(),nao_sim.motion()
        else :
            print("unknow robot :" + str(name))
            exit()

def convert_to_ascii(text):
    if not isinstance(text,unicode):
        print ("not unicode")
        text=text.decode("utf-8","ignore")
    text=text.replace(U"\u00E4","ae")
    text=text.replace(U"\u00C4","Ae")
    text=text.replace(U"\u00F6","oe")
    text=text.replace(U"\u00D6","Oe")
    text=text.replace(U"\u00FC","ue")
    text=text.replace(U"\u00DC","Ue")
    text=text.replace(U"\u00DF","ss")
    text= text.encode(encoding="ASCII",errors="ignore")
    return text

def readFile(filename,data_path):
    try: 
        file_name = data_path + "/" + filename
        if DEBUG_CALLS==True: 
            print ("read data from "+file_name);
        file1 = open(file_name, "r")
        lines = file1.readlines()
        file1.close()
    except: 
        print("warning: file not found: " + file_name)
        lines=""
    return lines

def readCSVFile(filename,data_path):
    try: 
        file_name = data_path + "/" + filename
        if DEBUG_CALLS==True: 
            print ("read data from "+file_name);
        if sys.version_info[0]<3 :    
            file   = open(file_name, "rb")
        else:
            file   = open(file_name, "r", newline='')
        reader = csv.reader(file)
    except: 
        print("warning: file not found: " + file_name)
        file = None
        reader = []
    return file,reader

def readSrtFile(filename,data_path):
    try: 
        file_name = data_path + "/" + filename
        srtFile = open(file_name,'r')
        srtText = srtFile.read()
    except: 
        print("no srt file found: " + file_name)
        srtText=""
    return srtText 

class TextTool :
    def __init__(self):
        self.text = None
        self.replacements = None

    def getSubString(self,start_word,end_word,search_pos):
        begin = self.text.lower().find(start_word.lower(),search_pos)
        if (begin==-1): 
            print("error: substring after "+ start_word + " not found")
            return ""
        else :  
            begin = begin + len(start_word)        

        if (end_word=="") : 
            return self.text[begin:]
        end = self.text.lower().find(end_word.lower(),search_pos)
        if (end==-1): 
            print("error: substring before "+ end_word + " not found")
            return ""
        return self.text[begin:end]

    def replace(self,originalText):
        finalText=originalText
        for lines in self.replacements :
            try: 
                keyword, start_word, end_word, search_pos = lines.split("#")
                replacement_text = self.getSubString(start_word.strip(),end_word.strip(),int(search_pos))
                finalText=finalText.replace(keyword,replacement_text)
                if DEBUG_TXT_REPLACE==True: 
                    print("replaced " + keyword + " with " +  replacement_text);
                    print("original text: " + lines.content)
                    print("replaced text: " + finalText)
            except:
                continue
        return finalText



class RobotControl(): 

    def __init__(self,mqtt,mosquitto_ip,data_path, language, min_speech_speed, max_speech_speed,robot_name,robot_ip):
        self.mqtt=mqtt
        if mqtt=="on" :
            self.mqtt_client = mqttClient(mosquitto_ip,"robot")
            self.mqtt_client.subscribe("robot/speak-and-gesture",self.action)
            self.mqtt_client.subscribe("robot/control/set-speed",self.set_speed)
            self.mqtt_client.subscribe("robot/control/set-max-speed",self.set_max_speed)
            self.mqtt_client.subscribe("robot/control/set-min-speed",self.set_min_speed)
        self.speech,self.motion = getRobot(robot_name,robot_ip)
        self.speech.setLanguage(language)
        self.text_tool = TextTool()
        self.running = False
        self.talking = False
        self.tag = None
        self.srtText = None
        self.start_time = None
        self.data_path=data_path
        self.data_path_random=os.path.dirname(sobotify.robotcontrol.data.__file__)
        self.current_datapath= self.data_path
        self.min_speech_speed=int(min_speech_speed)
        self.max_speech_speed=int(max_speech_speed)
        if mqtt=="on" :
            self.mqtt_client.publish("robot/status/init-done")


    def set_speed(self,message):
        self.set_min_speed(message)
        self.set_max_speed(message)

    def set_max_speed(self,message):
        self.max_speech_speed=int(message)

    def set_min_speed(self,message):
        self.min_speech_speed=int(message)

    def deltatime(self,end) :
        time_string = "{:.3f}".format((end-self.start_time).total_seconds())
        return time_string
        
    def speechSpeedCalc(self,time_stamp,end_time,speech_text):
        speech_time   = end_time-time_stamp
        if speech_time==0: 
            speech_time=1
        speech_chars  = len(speech_text)
        speech_speed_chars = speech_chars/7.0/speech_time*60*0.7;
        speech_speed = int(speech_speed_chars)
        if (speech_speed>self.max_speech_speed):
            print("warning: " + str(speech_speed) + " is above maximum speech speed -> set speed to "+ str(self.max_speech_speed))
            speech_speed= self.max_speech_speed
        elif (speech_speed<self.min_speech_speed):
            print("warning: " + str(speech_speed) + " is below minimum speech speed -> set speed to "+ str(self.min_speech_speed))
            speech_speed= self.min_speech_speed
        if DEBUG_SYNC==True: 
            print ("\nspeech length = " + "{:.3f}".format(speech_time))
            print ("speech chars  = " + str(speech_chars))
            print ("speech speed  = " + str(speech_speed))
            print ("\n"+str(time_stamp) +  " : " +  speech_text)
        return speech_speed

    def sync(self,start,time_stamp,show_message=False):
        delta_time=(datetime.now()-start).total_seconds()
        diff = time_stamp-delta_time
        if DEBUG_SYNC==True and show_message==True: 
            print ("\nsleep for :" + "{:.3f}".format(diff))
        if (diff>0) :
            sleep(diff)
        
    def say(self):
        self.talking = True;
        start = datetime.now()
        print ("speech starts at   : " + self.deltatime(start))
        for lines in srt.parse(self.srtText):
            speech_text  = self.text_tool.replace(lines.content)
            time_stamp   = lines.start.total_seconds()*speed_factor
            end_time     = lines.end.total_seconds()*speed_factor
            speech_speed = self.speechSpeedCalc(time_stamp,end_time,speech_text)
            self.sync(start,time_stamp,True)
            self.speech.setSpeed(speech_speed)
            self.speech.say(speech_text)
        print ("\nspeech done at     : " + self.deltatime(datetime.now()))                        
        self.talking=False;

    def movement(self,reader):           
        last_motion=0.;
        start=datetime.now()        
        print ("movement starts at : " + self.deltatime(start))
        for i,landm in enumerate(reader) :
            if (self.talking==False) :
                break;
            time_stamp= float(landm[0])*speed_factor
            landm.pop(0)
            self.sync(start,time_stamp)
            if DEBUG_SYNC==True: 
                if (i%15==0):
                    print ("\n"+str(time_stamp))
            delta_time=(datetime.now()-start).total_seconds()
            diff_since_last_motion= delta_time-last_motion
            if (diff_since_last_motion>0.05) :
                if DEBUG_SYNC==True: 
                    sys.stdout.write(".") 
                self.motion.move(landm)                
                last_motion= delta_time
            else :
                if DEBUG_SYNC2==True: 
                    print ("no movement : " + str(time_stamp))
        print ("\nmovement done at   : " + self.deltatime(datetime.now()))                              

    def move(self):
        motion_file,motion_reader = readCSVFile(self.tag + self.motion.getFileExtension() + ".csv",self.current_datapath)  
        self.movement(motion_reader)
        if motion_file != None :
            motion_file.close()
        while (self.talking==True):
            random_motion_file,random_motion_reader = readCSVFile("random"+ self.motion.getFileExtension() + ".csv", self.data_path_random)  
            self.movement(random_motion_reader)
            if random_motion_file != None :
                random_motion_file.close()
 
    def action(self,message):     
        if (sys.version_info[0]==2 and sys.version_info[1]==7) :
            message= convert_to_ascii(message)
        parts = message.split("|")
        if len(parts)>1:
            self.tag = parts[0]
            self.text_tool.text=parts[1]
            self.current_datapath= self.data_path
        else :
            self.tag = "random"
            self.text_tool.text=parts[0]
            self.current_datapath= self.data_path_random
        self.text_tool.replacements = readFile(self.tag + "_replace.txt",self.current_datapath)
        self.srtText                = readSrtFile(self.tag + ".srt",self.current_datapath)
        if (sys.version_info[0]==2 and sys.version_info[1]==7) :
            self.srtText= convert_to_ascii(self.srtText)
        self.start_time = datetime.now()
        print ("action starts at   : " + str(self.start_time))
        thread_speech = threading.Thread(target=self.say)
        thread_motion = threading.Thread(target=self.move)
        thread_speech.start()
        thread_motion.start()
        thread_speech.join()
        thread_motion.join()
        self.motion.terminate()
        if self.mqtt=="on" :
            self.mqtt_client.publish("robot/done","")
        print ("action done at     : " + str(datetime.now()))
        
    def start(self):
        self.running = True
        print ("Starting Acting")
                                 
    def terminate(self):
        if self.running:
            self.running = False
        self.speech.terminate()

def robotcontroller(mqtt,mosquitto_ip,data_path,language,min_speech_speed,max_speech_speed,robot_name,robot_ip,message,gesture) :
    print ("starting robot controller ...")
    robot = RobotControl(mqtt,mosquitto_ip,data_path,language,min_speech_speed,max_speech_speed,robot_name,robot_ip)
    if mqtt=="on" :
        while True:
            sleep(1000)
    else :
        if gesture=="":
            print ("received message:", message)
            robot.action(message)
        else :
            print ("received gesture:", gesture)
            robot.action(gesture+"|")
        robot.terminate()


if __name__ == "__main__":
    parser=argparse.ArgumentParser(description='start an mqtt client for controlling a robot')
    parser.add_argument('--mqtt',default="off",help='enable/disable mqtt client (on/off)')
    parser.add_argument('--mosquitto_ip',default='127.0.0.1',help='ip address of the mosquitto server')
    parser.add_argument('--message',default='Hello World',help='message to be spoken by the robot')
    parser.add_argument('--gesture',default='',help='gesture to be done by the robot')
    parser.add_argument('--robot_name',default='stickman',help='name of the robot (stickman,pepper)')
    parser.add_argument('--robot_ip',default='127.0.0.1',help='ip address of the robot')
    parser.add_argument('--data_path',default=os.path.join(os.path.expanduser("~"),".sobotify","data"),help='path to movement/speech data')
    parser.add_argument('--language',default="english",help='choose language (english,german)')
    parser.add_argument('--min_speech_speed',default=70,help='minimum speech speed of robot')
    parser.add_argument('--max_speech_speed',default=110,help='maximum speech speed of robot')
    args=parser.parse_args()   
    robotcontroller(args.mqtt,args.mosquitto_ip,args.data_path,args.language,args.min_speech_speed,args.max_speech_speed,args.robot_name,args.robot_ip,args.message,args.gesture)

 