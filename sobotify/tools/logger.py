import paho.mqtt.client as mqtt
from signal import signal, SIGINT
import os
from sys import exit
import time
import argparse
from sobotify.commons.mqttclient import mqttClient
import csv
from datetime import datetime
import cv2 as cv
import inspect

SERVER_CONNECT_TIMEOUT= 5   # timeout fpr client to connect to server (in seconds)
FLUSH_FILE_INTERVAL   = 2   # interval to write the current messages to disk (in seconds)s

LOG_FILE_DIR          = os.path.join(os.path.expanduser("~"),".sobotify","log")
IGNORED_MESSAGES      = ("robot/image",
                         "robot/command/get_image",
                         "robot/audio",
                         "robot/command/get_audio_data"
                         )

def timestamp():
        return datetime.now().isoformat()

def timestamp_filesystem():
        return datetime.now().strftime("%y%m%d_%H%M%S_%f")

class LoggerClient():
    def __init__(self,mqtt_client) :
        self.logging=False
        print ("init logging_client ...", flush=True)
        self.mqtt_client=mqtt_client
        self.get_log_dir_done_flag =False
        self.log_dir=self.get_log_dir()
        print (" done")

    def store_log_dir(self,message) :
        print("got init done: "+ message)
        self.log_dir=message
        self.get_log_dir_done_flag =True

    def get_log_dir(self):
        self.mqtt_client.subscribe("logging_server/status/log_dir",self.store_log_dir)
        self.mqtt_client.publish("logging_server/command/get_log_dir")
        print("waiting for logging server to send log directory ...")             
        start_time=datetime.now()
        while not self.get_log_dir_done_flag==True:
            delta_time=(datetime.now()-start_time).total_seconds()
            if delta_time > SERVER_CONNECT_TIMEOUT :
                print("Server did not reply, logging disabled")
                self.logging=False
                return None
            time.sleep(0.5)
        print(" ... done")  
        self.logging=True
        return self.log_dir

    def message(self,message,topic="",level=1) :
        if self.logging==True:
            if topic=="":
                full_filename=inspect.stack()[level].filename
                filename, ext = os.path.splitext(os.path.basename(full_filename))
                function=inspect.stack()[level].function
                lineno=inspect.stack()[level].lineno
                full_topic=f"log/{filename}/{function}/{lineno}"
            else:
                full_topic=f"log/{topic}"
            self.mqtt_client.publish(full_topic,message)

    def image(self,cv_image,name="",type=".png") :
        if self.logging==True:
            if not name=="":
                name=name+"_"
            img_filename=os.path.join(self.log_dir,name+timestamp_filesystem()+type)
            print ("log image to "+img_filename)
            cv.imwrite(img_filename,cv_image)

class LoggerServer():

    def __init__(self,mosquitto_ip) :
        print ("init logging server ...", flush=True)
        self.last_flush_file_time=datetime.now()
        self.mqtt_client = mqttClient(mosquitto_ip,"logging_server")
        self.mqtt_client.subscribe("#",self.process_message,raw_data=True,receive_topic=True)

        #create and open csv log file
        self.log_dir=os.path.join(LOG_FILE_DIR,timestamp_filesystem())
        os.makedirs(self.log_dir)
        log_filename=os.path.join(self.log_dir,"_log_messages.csv")
        print(log_filename)
        self.log_file=open(log_filename, "w", newline='')
        self.message_writer = csv.writer(self.log_file)
        row=["timestamp","topic","message"]
        self.message_writer.writerow(row)

        self.mqtt_client.publish("logging_server/status/init-done")
        print (" finished")

    def send_log_dir(self) :
        self.mqtt_client.publish("logging_server/status/log_dir",self.log_dir)

    def flush_file(self) :
        curr_time=datetime.now()
        delta_time=(curr_time-self.last_flush_file_time).total_seconds()
        if delta_time > FLUSH_FILE_INTERVAL :
            #print("write messages to disk")
            self.last_flush_file_time=curr_time
            self.log_file.flush()

    def store_message(self,message,topic) :
        row=[]
        row.append(timestamp())
        row.append(topic)
        row.append(message)
        self.message_writer.writerow(row)
        #print(f"store message: {row}")

    def process_message(self,message,topic) :
        self.topic   = topic
        self.message = message
        if topic=="logging_server/command/get_log_dir":
            self.send_log_dir()
        elif topic in IGNORED_MESSAGES:
            pass
        else:
            message = message.decode('utf-8')
            #print(f"logging: {self.topic} : {self.message}" )
            self.store_message(message,topic)

    def terminate(self,message,topic) :
        self.store_message("closing logging server","close")
        self.log_file.flush()
        self.log_file.close()


def logging_server(mqtt,mosquitto_ip) :
    global log_server
    log_server = LoggerServer(mosquitto_ip)
    if mqtt=="on" :
        while True:
            time.sleep(1)
            log_server.flush_file()
    else :
        while True:
            time.sleep(1)
            log_server.flush_file()

def handler(signal_received, frame):
    # Handle cleanup here
    log_server.terminate()
    print('SIGINT or CTRL-C detected. Exiting gracefully')
    exit(0)

if __name__ == "__main__":
    signal(SIGINT, handler)
    parser=argparse.ArgumentParser(description='speech recognition with mqtt client')
    parser.add_argument('--mqtt',default="off",help='enable/disable mqtt client (on/off)')
    parser.add_argument('--mosquitto_ip',default='127.0.0.1',help='ip address of the mosquitto server')
    args=parser.parse_args()
    logging_server(args.mqtt,args.mosquitto_ip)
