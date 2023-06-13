import paho.mqtt.client as mqtt
from signal import signal, SIGINT
import os
from sys import exit
import time
import argparse
from sobotify.commons.mqttclient import mqttClient
import cv2 as cv
from deepface import DeepFace
from datetime import datetime

## open-cv related part based on example code in: 
# https://docs.opencv.org/3.4/dd/d43/tutorial_py_video_display.html


def getRobot(name,robot_ip,cam_device) :
        if name=='stickman' or name=='pepper' or name=='pepper_sim' or name=='nao' or name=='nao_sim' or  name=='mykeepon':
            import sobotify.robots.stickman.stickman as stickman
            return stickman.vision(cam_device)
        elif name=='cozmo' :
            import sobotify.robots.cozmo.cozmo as cozmo
            my_cozmo=cozmo.cozmo()
            return my_cozmo
        else :
            print("unknow robot :" + str(name))
            exit()

class EmotionDetection:

    def __init__(self,robot_name,robot_ip,cam_device) :
        print ("init emotion detection ...", flush=True)
        self.start_detection_flag=False
        self.stop_detection_flag=False
        self.query=''
        self.robot=getRobot(robot_name,robot_ip,cam_device)
        print (" finished")
        
    def detect(self,show_video,fps) :

        emotions_accum={}
        emotions_accum['angry']=0.0
        emotions_accum['disgust']=0.0
        emotions_accum['fear']=0.0
        emotions_accum['happy']=0.0
        emotions_accum['sad']=0.0
        emotions_accum['surprise']=0.0
        emotions_accum['neutral']=0.0
        emotions_accum['amount']=0

        last_time=datetime.now()
        while True :
            delta_time=(datetime.now()-last_time).total_seconds()
            while delta_time < 1/fps:
                delta_time=(datetime.now()-last_time).total_seconds()
            last_time=datetime.now()
            ret,img=self.robot.get_image()
            img_height=img.shape[0]
            img_width=img.shape[1]
            if img_width>600:
                text_size=1
                text_width=2
            else:
                text_size=0.5
                text_width=1
            if ret:
                try:
                    emotions=DeepFace.analyze(img,actions=["emotion"])
                    if len(emotions)>0:
                        x=emotions[0]["region"]["x"]
                        y=emotions[0]["region"]["y"]
                        w=emotions[0]["region"]["w"]
                        h=emotions[0]["region"]["h"]
                        dominant_emotion=emotions[0]["dominant_emotion"]
                        #print(emotions[0]["emotion"])
                        for emotion,value in emotions[0]["emotion"].items() :
                            #print(emotion+"::"+str(value))
                            emotions_accum[emotion]+=value
                        emotions_accum['amount']+=1
                        #print(emotions_accum)

                        cv.rectangle(img,(x,y),(x+w,y+h),(255,0,0),3)
                        cv.putText(img,dominant_emotion,(int(x+w/8),int(y+h/4)),cv.FONT_HERSHEY_DUPLEX,text_size,(0,255,0),text_width)
                except:
                    cv.putText(img,"no face detected",(int(img_width/8),int(img_height/8)),cv.FONT_HERSHEY_DUPLEX,text_size,(0,0,255),text_width)

                if show_video=="on":
                    cv.imshow("Image",img)
                    if cv.waitKey(1) == ord("q"):
                        break
                if self.stop_detection_flag == True :
                    self.stop_detection_flag=False
                    break
        cv.destroyAllWindows()

        #print(emotions_accum)
        max_emotion=max(emotions_accum,key=emotions_accum.get)
        #print(max_emotion)
        return max_emotion

    def start_detection(self,message) :
        self.start_detection_flag=True

    def stop_detection(self,message) :
        self.stop_detection_flag=True


def emotion_detection(mqtt,mosquitto_ip,robot_name,robot_ip,cam_device,frame_rate,show_video) :
    em_detect = EmotionDetection(robot_name,robot_ip,cam_device)
    if mqtt=="on" :
        mqtt_client = mqttClient(mosquitto_ip,"emotion_detection")
        mqtt_client.subscribe("emotion_detection/start",em_detect.start_detection)
        mqtt_client.subscribe("emotion_detection/stop",em_detect.stop_detection)
        mqtt_client.publish("emotion_detection/status/init-done")
        while True:
            if em_detect.start_detection_flag:
                em_detect.start_detection_flag=False
                emotion=em_detect.detect(show_video,frame_rate)
                mqtt_client.publish("emotion_detection/dominant_emotion",emotion)
            time.sleep(1)
    else :
        emotion=em_detect.detect(show_video,frame_rate)
        print("The dominant emotion is:" + emotion)
        while True:
            time.sleep(1)

def handler(signal_received, frame):
    # Handle cleanup here
    print('SIGINT or CTRL-C detected. Exiting gracefully')
    exit(0)

if __name__ == "__main__":
    signal(SIGINT, handler)
    parser=argparse.ArgumentParser(description='speech recognition with mqtt client')
    parser.add_argument('--mqtt',default="off",help='enable/disable mqtt client (on/off)')
    parser.add_argument('--show_video',default="on",help='enable/disable video output on screen')
    parser.add_argument('--mosquitto_ip',default='127.0.0.1',help='ip address of the mosquitto server')
    parser.add_argument('--robot_name',default='stickman',help='name of the robot (stickman,pepper)')
    parser.add_argument('--robot_ip',default='127.0.0.1',help='ip address of the robot')
    parser.add_argument('--cam_device',default='0',help='camera device name or number')
    parser.add_argument('--frame_rate',default=1,type=float,help='frame rate')
    args=parser.parse_args()

    emotion_detection(args.mqtt,args.mosquitto_ip,args.robot_name,args.robot_ip,args.cam_device,args.frame_rate,args.show_video)
