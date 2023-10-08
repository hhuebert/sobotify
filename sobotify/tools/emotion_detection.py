import paho.mqtt.client as mqtt
from signal import signal, SIGINT
import os
from sys import exit
import time
import argparse
from sobotify.commons.mqttclient import mqttClient
from sobotify.commons.logger import LoggerClient
import cv2 as cv
import numpy as np
from deepface import DeepFace
from datetime import datetime

face_database=os.path.join(os.path.expanduser("~"),".sobotify","face_db")

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

def offsets(face,img_width,img_height):
    #center_img_x=int(img_width/2)
    #center_img_y=int(img_height/2)
    #center_face_x=int(x+w/2)
    #center_face_y=int(y+h/2)
    #offset_x=center_face_x-center_img_x
    #offset_y=center_face_y-center_img_y
    #offset_rel_x=round(offset_x/(img_width/2),3)
    #offset_rel_y=round(offset_y/(img_height/2),3)
    #face_img=face['face']
    x=face["x"]
    y=face["y"]
    w=face["w"]
    h=face["h"]
    offset_rel_x=round((2*x+w)/(img_width)-1,2)
    offset_rel_y=round((2*y+h)/(img_height)-1,2)
    return offset_rel_x,offset_rel_y

class EmotionDetection:

    def __init__(self,mqtt,mosquitto_ip,robot_name,robot_ip,cam_device) :
        self.mqtt=mqtt
        self.last_time=datetime.now()
        self.emotions_accum={}
        self.reset_emotion_values()
        if self.mqtt=="on" :
            self.mqtt_client = mqttClient(mosquitto_ip,"emotion_detection")
            self.mqtt_client.subscribe("robot_control/image",self.store_image,raw_data=True)
            self.mqtt_client.subscribe("emotion_detection/start",self.start_detection)
            self.mqtt_client.subscribe("emotion_detection/stop",self.stop_detection)
        else :
            self.robot=getRobot(robot_name,robot_ip,cam_device) 
        print ("init emotion detection ...", flush=True)
        self.image_available=False
        self.start_detection_flag=False
        self.stop_detection_flag=False
        self.query=''
        if self.mqtt=="on" :
            self.mqtt_client.publish("emotion_detection/status/init-done")
            self.log=LoggerClient(self.mqtt_client)
        print (" finished")

    def reset_emotion_values(self) :
        self.emotions_accum['angry']=0.0
        self.emotions_accum['disgust']=0.0
        self.emotions_accum['fear']=0.0
        self.emotions_accum['happy']=0.0
        self.emotions_accum['sad']=0.0
        self.emotions_accum['surprise']=0.0
        self.emotions_accum['neutral']=0.0
        self.emotions_accum['amount']=0

    def store_image(self,image) :
        img_byte=bytearray(image)
        im_array=np.asarray(img_byte)
        self.image=cv.imdecode(im_array,cv.IMREAD_COLOR)
        self.log.image(self.image,"raw")
        self.image_available=True

    def get_image(self) :
        if self.mqtt=="on" :
            self.mqtt_client.publish("robot_control/command/get_image")
            last_request=datetime.now()
            while not self.image_available:
                time.sleep(0.01)    
                delta_time=(datetime.now()-last_request).total_seconds()
                if delta_time>3:
                    last_request=datetime.now()
                    self.mqtt_client.publish("robot_control/command/get_image")
            self.image_available=False
            return self.image
        else: 
            ret,self.image=self.robot.get_image()
            return self.image

    def send_head_data(self,face,img_width,img_height):
        offset_x, offset_y = offsets(face,img_width,img_height)
        print(offset_x)
        print(offset_y)
        head_data={}
        head_data["offset_x"]=offset_x
        head_data["offset_y"]=offset_y
        head_data["img_width"]=img_width
        head_data["img_height"]=img_height
        self.mqtt_client.publish("robot_control/command/follow_head",str(head_data))

    def draw_bounding_box(self,img,face,text_top="",text_bottom="",text_size=1,text_width=1) :
        x=face["x"]
        y=face["y"]
        w=face["w"]
        h=face["h"]
        cv.rectangle(img,(x,y),(x+w,y+h),(255,0,0),3)
        cv.putText(img,text_top,(int(x+w/8),int(y+h/4)),cv.FONT_HERSHEY_DUPLEX,text_size,(0,255,0),text_width)
        cv.putText(img,text_bottom,(int(x+w/8),int(y+3*h/4)),cv.FONT_HERSHEY_DUPLEX,text_size,(0,255,0),text_width)

    def face_detect(self,img) :
        faces=DeepFace.extract_faces(img)
        face=faces[0]['facial_area']
        self.draw_bounding_box(img,face)
        return face

    def emotion_detect(self,img) :
        emotions=DeepFace.analyze(img,actions=["emotion"])
        if len(emotions)>0:
            dominant_emotion=emotions[0]["dominant_emotion"]
            #print(emotions[0]["emotion"])
            for emotion,value in emotions[0]["emotion"].items() :
                #print(emotion+"::"+str(value))
                self.emotions_accum[emotion]+=value
            self.emotions_accum['amount']+=1
            #print(emotions_accum)
            face=emotions[0]["region"]
            self.mqtt_client.publish("emotion_detection/emotions",str(emotions[0]["emotion"]))
            return face,dominant_emotion

    def face_recognition(self,img) :
        face_string=""
        name=""
        faces = DeepFace.find(img, db_path = face_database)
        print (faces[0])
        for index,face in faces[0].iterrows():
            if index==0:
                name=os.path.splitext(os.path.basename(face["identity"]))[0]
                difference=round(face["VGG-Face_cosine"],2)
                face_string=name+":"+str(difference)
            #print (face)
            print(os.path.splitext(os.path.basename(face["identity"]))[0],":",round(face["VGG-Face_cosine"],2))
        self.mqtt_client.publish("emotion_detection/name",str(name))
        return face_string


    def detect(self,show_video,fps,detect_emo=False) :
        detect_emotion=detect_emo
        while True :
            if self.start_detection_flag==True:
                detect_emotion=True
            delta_time=(datetime.now()-self.last_time).total_seconds()
            while delta_time < 1/fps:
                delta_time=(datetime.now()-self.last_time).total_seconds()
            self.last_time=datetime.now()
            img=self.get_image()
            img_height=img.shape[0]
            img_width=img.shape[1]
            try:
                face_string=self.face_recognition(img)
            except:
                print ("face not found in database")
                if self.mqtt=="on" :
                    self.mqtt_client.publish("emotion_detection/name","")
            if img_width>600:
                text_size=1
                text_width=2
            else:
                text_size=0.5
                text_width=1            
            try:
                if detect_emotion==True:
                    face,dominant_emotion=self.emotion_detect(img)
                    self.draw_bounding_box(img,face,dominant_emotion,face_string,text_size,text_width)
                else :
                    face=self.face_detect(img)
                    self.draw_bounding_box(img,face,"",face_string,text_size,text_width)
                self.send_head_data(face,img_width,img_height)
            except:
                cv.putText(img,"no face detected",(int(img_width/8),int(img_height/8)),cv.FONT_HERSHEY_DUPLEX,text_size,(0,0,255),text_width)

            self.log.image(img,"fer")

            if show_video=="on":
                cv.imshow("Image",img)
                if cv.waitKey(1) == ord("q"):
                    break

            if self.stop_detection_flag == True :
                if self.emotions_accum["amount"]==0:
                    dominant_emotion_accum="none"
                else:
                    dominant_emotion_accum=max(self.emotions_accum,key=self.emotions_accum.get)
                self.mqtt_client.publish("emotion_detection/dominant_emotion",dominant_emotion_accum)
                self.stop_detection_flag=False
                detect_emotion=False
        cv.destroyAllWindows()
        if self.emotions_accum["amount"]==0:
            dominant_emotion_accum="none"
        else:
            dominant_emotion_accum=max(self.emotions_accum,key=self.emotions_accum.get)
        return dominant_emotion_accum

    def start_detection(self,message) :
        self.reset_emotion_values()
        self.start_detection_flag=True

    def stop_detection(self,message) :
        self.stop_detection_flag=True


def emotion_detection(mqtt,mosquitto_ip,robot_name,robot_ip,cam_device,frame_rate,show_video) :
    em_detect = EmotionDetection(mqtt,mosquitto_ip,robot_name,robot_ip,cam_device)
    if mqtt=="on" :
        em_detect.detect(show_video,frame_rate)
    else :
        emotion=em_detect.detect(show_video,frame_rate,True)
        print("The dominant emotion is:" + emotion)

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
