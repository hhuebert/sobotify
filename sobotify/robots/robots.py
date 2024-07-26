#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse
import sys
import threading
from sobotify.commons.mqttclient import mqttClient
from time import sleep
import cv2 as cv
import ast

LIST_OF_ROBOTS=("stickman","pepper","nao","cozmo","mykeepon")

def get_names() :
    return LIST_OF_ROBOTS

def get_vision(name,robot_ip,cam_device) :
        if name=='stickman' or name=='pepper' or name=='pepper_sim' or name=='nao' or name=='nao_sim' or  name=='mykeepon':
            import sobotify.robots.stickman.stickman as stickman
            return stickman.vision(cam_device)
        elif name=='cozmo' :
            import sobotify.robots.cozmo.cozmo as cozmo
            return cozmo.vision()
        else :
            print("unknow robot :" + str(name))
            exit()

def get_sound(name,robot_ip,sound_device) :
        if name=='stickman' or name=='pepper' or name=='pepper_sim' or name=='nao' or name=='nao_sim' or  name=='mykeepon' or name=='cozmo':
            import sobotify.robots.stickman.stickman as stickman
            return stickman.sound(sound_device)
        elif name=='pepper' :
            import sobotify.robots.pepper.pepper as pepper
            return pepper.sound(sound_device)
        elif name=='pepper_sim' :
            import sobotify.robots.pepper.pepper_sim as pepper_sim
            return pepper_sim.sound(sound_device)
        elif name=='nao' :
            import sobotify.robots.nao.nao as nao
            return nao.sound(sound_device)
        elif name=='nao_sim' :
            import sobotify.robots.nao.nao_sim as nao_sim
            return nao_sim.sound(sound_device)
        elif name=='cozmo' :
            import sobotify.robots.cozmo.cozmo as cozmo
            my_cozmo=cozmo.cozmo(sound_device)
            return my_cozmo
        elif name=='mykeepon' :
            import sobotify.robots.mykeepon.mykeepon as mykeepon
            return mykeepon.sound(sound_device)
        else :
            print("unknow robot :" + str(name))
            exit()


def get_gesture_converter(name) :
    if name=='stickman' :
        return None
    elif name=='pepper' :
        import sobotify.robots.pepper.landmarks2angles as landmarks2angles
        return landmarks2angles.convert
    elif name=='nao' :
        import sobotify.robots.nao.landmarks2angles as landmarks2angles
        return landmarks2angles.convert
    elif name=='cozmo' :
        import sobotify.robots.cozmo.landmarks2angles as landmarks2angles
        return landmarks2angles.convert
    elif name=='mykeepon' :
        import sobotify.robots.mykeepon.landmarks2angles as landmarks2angles
        return landmarks2angles.convert
    else :
        print("unknow robot :" + str(name))
        return None                   
    
def get_all_interfaces(name,robot_ip,robot_options,cam_device,sound_device) :
        parser=argparse.ArgumentParser(description='start an mqtt client for controlling a robot')
        parser.add_argument('--nao',default="",nargs="+",help='nao specific options')
        parser.add_argument('--nao_sim',default="",nargs="+",help='nao simulator specific options')
        parser.add_argument('--pepper',default="",nargs="+",help='pepper specific options')
        parser.add_argument('--pepper_sim',default="",nargs="+",help='pepper simulator specific options')
        parser.add_argument('--cozmo',default="",nargs="+",help='cozmo specific options')
        parser.add_argument('--stickman',default="",nargs="+",help='stickman specific options')
        robot_options_args=parser.parse_args(robot_options.strip('"').split())   

        if name=='stickman' :
            import sobotify.robots.stickman.stickman as stickman
            my_stickman=stickman.stickman(cam_device,sound_device)
            return my_stickman
        elif name=='pepper' :
            if not (sys.version_info[0]==2 and sys.version_info[1]==7) :
                print("Pepper robot can only be used with Python version 2.7.x (your version is " + str(sys.version_info[0])+"."+str(sys.version_info[1])+")")
                exit()
            import sobotify.robots.pepper.pepper as pepper
            my_pepper=pepper.Pepper(robot_ip,cam_device,sound_device)
            return my_pepper
        elif name=='pepper_sim' :
            import sobotify.robots.pepper.pepper_sim as pepper_sim
            return pepper_sim.speech(),pepper_sim.motion(),pepper_sim.vision(cam_device),pepper_sim.sound(sound_device)
        elif name=='nao' :
            if not (sys.version_info[0]==2 and sys.version_info[1]==7) :
                print("Nao robot can only be used with Python version 2.7.x (your version is " + str(sys.version_info[0])+"."+str(sys.version_info[1])+")")
                exit()
            import sobotify.robots.nao.nao as nao
            my_nao=nao.NAO(robot_ip,robot_options_args.nao,cam_device,sound_device)
            return my_nao
        elif name=='nao_sim' :
            import sobotify.robots.nao.nao_sim as nao_sim
            return nao_sim.speech(),nao_sim.motion(),nao_sim.vision(cam_device),nao_sim.sound(sound_device)
        elif name=='cozmo' :
            import sobotify.robots.cozmo.cozmo as cozmo
            my_cozmo=cozmo.cozmo(sound_device)
            return my_cozmo
        elif name=='mykeepon' :
            PORT=robot_ip
            import sobotify.robots.mykeepon.mykeepon as mykeepon
            my_mykeepon=mykeepon.MyKeepon(PORT,cam_device,sound_device)
            return my_mykeepon
        else :
            print("unknow robot :" + str(name))
            exit()    


class RobotInterface():

    def __init__(self,mqtt,mosquitto_ip,robot_name,robot_ip,robot_options,language,speed,cam_device,sound_device):
        self.mqtt=mqtt
        self.stop_robotinterface=False
        self.get_image_flag=False
        self.get_audio_flag=False
        self.head_update_flag=False
        self.start_streaming_flag=False
        self.stop_streaming_flag=False
        self.set_language_flag=False
        self.set_speed_flag=False
        self.say_flag=False
        self.move_flag=False
        self.search_head_flag=False
        self.follow_head_flag=False
        self.get_file_extension_flag=False
        self.motion_terminate_flag=False

        self.robot = get_all_interfaces(robot_name,robot_ip,robot_options,cam_device,sound_device)

        self.thread_get_image = threading.Thread(target=self.get_image_loop)
        self.thread_get_image.start()

        self.thread_follow_head = threading.Thread(target=self.follow_head_loop)
        self.thread_follow_head.start()

        self.thread_search_head = threading.Thread(target=self.search_head_loop)
        self.thread_search_head.start()

        self.thread_start_streaming = threading.Thread(target=self.start_streaming_loop)
        self.thread_start_streaming.start()

        self.thread_stop_streaming = threading.Thread(target=self.stop_streaming_loop)
        self.thread_stop_streaming.start()

        self.thread_set_language = threading.Thread(target=self.set_language_loop)
        self.thread_set_language.start()

        self.thread_set_speed = threading.Thread(target=self.set_speed_loop)
        self.thread_set_speed.start()

        self.thread_say = threading.Thread(target=self.say_loop)
        self.thread_say.start()

        self.thread_move = threading.Thread(target=self.move_loop)
        self.thread_move.start()

        self.thread_get_audio = threading.Thread(target=self.get_audio_loop)
        self.thread_get_audio.start()
        
        self.thread_get_file_extension = threading.Thread(target=self.get_file_extension_loop)
        self.thread_get_file_extension.start()

        self.thread_motion_terminate = threading.Thread(target=self.motion_terminate_loop)
        self.thread_motion_terminate.start()

        if mqtt=="on" :
            self.mqtt_client = mqttClient(mosquitto_ip,"robot_interface")
            self.mqtt_client.subscribe("robot/command/get_image",self.get_image)
            self.mqtt_client.subscribe("robot/command/streaming/start",self.start_streaming)
            self.mqtt_client.subscribe("robot/command/streaming/stop",self.stop_streaming)
            self.mqtt_client.subscribe("robot/command/get_audio_data",self.get_audio)
            self.mqtt_client.subscribe("robot/command/set_language",self.set_language)
            self.mqtt_client.subscribe("robot/command/set_speed",self.set_speed)
            self.mqtt_client.subscribe("robot/command/say",self.say)
            self.mqtt_client.subscribe("robot/command/move",self.move)
            self.mqtt_client.subscribe("robot/command/follow_head",self.follow_head)
            self.mqtt_client.subscribe("robot/command/search_head",self.search_head)
            self.mqtt_client.subscribe("robot/command/get_file_extension",self.get_file_extension)
            self.mqtt_client.subscribe("robot/command/motion_terminate",self.motion_terminate)
            self.mqtt_client.publish("robot/status/init-done")
        print(" ... done")  

    def get_file_extension(self,message="") :
        self.get_file_extension_flag=True

    def get_file_extension_loop(self) :
        while True:
            if self.stop_robotinterface==True:
                break    
            if self.get_file_extension_flag:
                self.get_file_extension_flag=False
                self.file_extension=self.robot.motion.getFileExtension()
                if self.mqtt=="on" :
                    self.mqtt_client.publish("robot/status/file_extension",self.file_extension)
                else:
                    return self.file_extension
            sleep(0.2)

    def motion_terminate(self,message="") :
        self.motion_terminate_flag=True

    def motion_terminate_loop(self) :
        while True:
            if self.stop_robotinterface==True:
                break    
            if self.motion_terminate_flag:
                self.motion_terminate_flag=False
                self.robot.motion.terminate()
            sleep(0.2)

    def get_image(self,message) : 
        self.get_image_flag=True

    def get_image_loop(self) : 
        while True:
            if self.stop_robotinterface==True:
                break
            if self.get_image_flag:
                self.get_image_flag=False
                ret,image=self.robot.vision.get_image()
                if ret==True:
                    ret, img=cv.imencode(".ppm",image)
                    if ret==True:
                        img_byte=bytearray(img)
                        self.mqtt_client.publish("robot/image",img_byte)
            sleep(0.02)

    def start_streaming(self,message="") :
        self.start_streaming_flag=True

    def start_streaming_loop(self) :
        while True:
            if self.stop_robotinterface==True:
                break    
            if self.start_streaming_flag:
                self.start_streaming_flag=False
                self.samplerate=self.robot.sound.start_streaming()
                if self.mqtt=="on" :
                    self.mqtt_client.publish("robot/status/samplerate",self.samplerate)
                else:
                    return self.samplerate
            sleep(0.2)

    def stop_streaming(self,message="") :
        self.stop_streaming_flag=True

    def stop_streaming_loop(self) :
        while True:
            if self.stop_robotinterface==True:
                break    
            if self.stop_streaming_flag:
                self.stop_streaming_flag=False
                self.robot.sound.stop_streaming()
            sleep(0.2)

    def set_language(self,message="") :
        self.language=message
        print ("got language:"+self.language)
        self.set_language_flag=True

    def set_language_loop(self) :
        while True:
            if self.stop_robotinterface==True:
                break    
            if self.set_language_flag:
                self.set_language_flag=False
                print ("set language:"+self.language)
                self.robot.speech.setLanguage(self.language)
            sleep(0.2)

    def set_speed(self,message="") :
        self.speed=int(message)
        self.set_speed_flag=True

    def set_speed_loop(self) :
        while True:
            if self.stop_robotinterface==True:
                break    
            if self.set_speed_flag:
                self.set_speed_flag=False
                self.robot.speech.setSpeed(self.speed)
            sleep(0.2)

    def say(self,message="") :
        self.message=message
        self.say_flag=True

    def say_loop(self) :
        while True:
            if self.stop_robotinterface==True:
                break    
            if self.say_flag:
                self.say_flag=False
                self.robot.speech.say(self.message)
                self.mqtt_client.publish("robot/status/speech_done")
            sleep(0.2)

    def move(self,message="") :
        self.move_data=ast.literal_eval(message)
        self.move_flag=True

    def move_loop(self) :
        while True:
            if self.stop_robotinterface==True:
                break    
            if self.move_flag:
                self.move_flag=False
                self.robot.motion.move(self.move_data)
            sleep(0.02)

    def get_audio(self,message) :
        self.get_audio_flag=True

    def get_audio_loop(self) : 
        while True:
            if self.stop_robotinterface==True:
                break
            if self.get_audio_flag:
                self.get_audio_flag=False
                ret,audio=self.robot.sound.get_audio_data()
                if ret==True:
                    #img_byte=bytearray(img)
                    self.mqtt_client.publish("robot/audio",audio)
            sleep(0.02)

    def follow_head(self,message="") :
        self.head_data=message
        self.follow_head_flag=True

    def follow_head_loop(self) :
        while True:
            if self.stop_robotinterface==True:
                break    
            if self.follow_head_flag:
                self.follow_head_flag=False
                self.robot.motion.follow_head(self.head_data)
            sleep(0.2)

    def search_head(self,message="") :
        self.search_head_flag=True

    def search_head_loop(self) :
        while True:
            if self.stop_robotinterface==True:
                break    
            if self.search_head_flag:
                self.search_head_flag=False
                self.robot.motion.search_head()
            sleep(0.2)

    def terminate(self) :
        self.stop_robotinterface=True
        sleep(1)
        self.thread_get_image.join()
        self.thread_follow_head.join()
        self.thread_search_head.join()
        self.thread_start_streaming.join()
        self.thread_stop_streaming.join()
        self.thread_set_language.join()
        self.thread_set_speed.join()
        self.thread_say.join()
        self.thread_move.join()
        self.thread_get_audio.join()
        self.thread_get_file_extension.join()
        self.thread_motion_terminate.join()
        self.robot.terminate()



def robot_interface(mqtt,mosquitto_ip,robot_name,robot_ip,robot_options,language,speed,cam_device,sound_device) :
    print ("starting robot interface ...")
    robot_if = RobotInterface(mqtt,mosquitto_ip,robot_name,robot_ip,robot_options,language,speed,cam_device,sound_device)
    if mqtt=="on" :
        while True:
            sleep(1000)
    else :
        robot_if.robot.speech.say("Hello World")
        robot_if.terminate()
 
if __name__ == "__main__":
    parser=argparse.ArgumentParser(description='start an mqtt client for controlling a robot')
    parser.add_argument('--mqtt',default="off",help='enable/disable mqtt client (on/off)')
    parser.add_argument('--mosquitto_ip',default='127.0.0.1',help='ip address of the mosquitto server')
    parser.add_argument('--robot_name',default='stickman',help='name of the robot (stickman,pepper)')
    parser.add_argument('--robot_ip',default='127.0.0.1',help='ip address of the robot')
    parser.add_argument('--robot_options',default='',help='robot specific options')
    parser.add_argument('--language',default="english",help='choose language (english,german)')
    parser.add_argument('--speed',default=100,type=int,help='choose speech speed')
    parser.add_argument('--cam_device',default='0',help='camera device name or number')
    parser.add_argument('--sound_device',default=0,type=int,help='number of sound device, can be found with: import sounddevice;sounddevice.query_devices()')
    args=parser.parse_args()   
    robot_interface(args.mqtt,args.mosquitto_ip,args.robot_name,args.robot_ip,args.robot_options,args.language,args.speed,args.cam_device,args.sound_device)

 