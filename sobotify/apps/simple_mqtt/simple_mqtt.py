from signal import signal, SIGINT
from sys import exit
import time
import argparse
from sobotify import sobotify

LANGUAGE="english"
KEYWORD="apple tree" 
MQTT_SUBSCRIBE_TOPIC="mytopic_sub"
MQTT_PUBLISH_TOPIC="mytopic_pub"

class simple_mqtt:

    def __init__(self,robot_name,robot_ip,sound_device,mosquitto_ip) :
        print ("init simple mqtt app ...")
        self.human_statement_pending=False
        self.mqtt_message_pending=False
        self.human_statement=""
        self.mqtt_message=""

        self.sobot=sobotify.sobotify(app_name="simple-mqtt",mosquitto_ip=mosquitto_ip,debug=False)
        self.sobot.start_listener(mosquitto_ip=mosquitto_ip,language=LANGUAGE,keyword=KEYWORD)
        self.sobot.start_robotcontroller(robot_name=robot_name,mosquitto_ip=mosquitto_ip,robot_ip=robot_ip, language=LANGUAGE,sound_device=sound_device)
        self.sobot.subscribe_listener(self.store_human_statement)
        self.subscribe_mqtt(MQTT_SUBSCRIBE_TOPIC,self.store_mqtt_message)
        print (" ... done")

    def publish_mqtt(self,message):
        self.sobot.mqtt_client.publish(MQTT_PUBLISH_TOPIC,message)

    def subscribe_mqtt(self,topic,callback):
        self.sobot.mqtt_client.subscribe(topic,callback)

    def store_mqtt_message(self,message) :
        self.mqtt_message = message
        print("got mqtt message: "+ self.mqtt_message)
        self.mqtt_message_pending=True

    def store_human_statement(self,statement) :
        self.human_statement = statement
        print("got statement from human: "+ self.human_statement)
        self.human_statement_pending=True

    def run(self) :
        self.sobot.speak("Hello, I am happy to talk to you")
        self.sobot.speak("Please tell me what you want to do by starting and stopping your request with the keyword " + KEYWORD)
        self.sobot.listen(listen_to_keyword=True)
        while True:
            if self.human_statement_pending:
                self.human_statement_pending=False
                self.sobot.speak("You said " + self.human_statement)
                self.publish_mqtt(self.human_statement)

            if self.mqtt_message_pending:
                self.mqtt_message_pending=False
                self.sobot.speak(self.mqtt_message)
            time.sleep(1)    

    def terminate(self):
        self.sobot.terminate()

def handler(signal_received, frame):
    # Handle cleanup here
    print('SIGINT or CTRL-C detected. Exiting gracefully')
    debate.terminate()
    exit(0)

if __name__ == "__main__":
    signal(SIGINT, handler)
    parser=argparse.ArgumentParser(description='speech recognition with mqtt client')
    parser.add_argument('--mosquitto_ip',default='127.0.0.1',help='ip address of the mosquitto server')
    parser.add_argument('--robot_name',default='stickman',help='name of the robot (stickman,pepper,nao)')
    parser.add_argument('--robot_ip',default='127.0.0.1',help='ip address of the robot')
    parser.add_argument('--keyword',default='apple tree',help='key word to activate speech recognition')
    parser.add_argument('--language',default="english",help='choose language (english,german)')
    parser.add_argument('--sound_device',default=0,type=int,help='number of sound device, can be found with: import sounddevice;sounddevice.query_devices()')
    parser.add_argument('--project_file',default='quiz_data.xlsx',help='project file with app data')
    args=parser.parse_args()

    debate = simple_mqtt(args.robot_name,args.robot_ip,args.sound_device,args.mosquitto_ip)
    debate.run()