import paho.mqtt.client as mqtt
from signal import signal, SIGINT
import os
from sys import exit
import time
import argparse

#llm dummy class (use the real class above if llm (llm-J, BLOOM,...) is installed)
class llm:

    def __init__(self,ll_model) :
        self.query=''
        print ("init ll model ", ll_model ,"...", end = '', flush=True)
        time.sleep(1) 
        print (" finished")
        
    def process_query(self,llm_temperature,llm_max_length) :
        print ("process query with llm dummy: " + self.query)
        print("llm-temperature:",llm_temperature)
        print("llm-max-length:",llm_max_length)
        time.sleep(3) 
        self.gen_text = "42"
        return self.gen_text

    def store_query(self,query) :
        global question_pending     
        self.query = query
        print("got query: "+ self.query)
        question_pending=True


class mqttClient(object):

    def __init__(self,mosquitto_ip,client_name):
        self.client = mqtt.Client(client_name, clean_session = False)
        self.broker = mosquitto_ip       
        self.client.on_connect = self.on_connect
        self.client.on_publish = self.on_publish
        self.client.on_message = self.on_message
        try:
            self.client.connect(self.broker, 1883)
        except:
            print('cannot connect to mqtt server at ip address: ',str(mosquitto_ip))
            print('start mqtt server(e.g. mosquitto) or check ip address')
            exit()
        self.client.loop_start()

    def subscribe(self,subscibe_topic,subscibe_callback) :
        self.client.subscribe(subscibe_topic)
        self.message_callback=subscibe_callback

    def publish(self,subscibe_topic,message) :
        self.client.publish(subscibe_topic,message)

    def on_publish(self, client, userdata, rc):
        print ("published! - " + str(rc))

    def on_message(self, client, userdata, msg):
        message = msg.payload.decode('utf-8')
        print ("received message:", message)
        self.message_callback(message)

    def on_connect(self, client, userdata, flags, rc):
        print ("Connected! - " + str(rc))
    
    def terminate(self):
        self.client.disconnect()
        self.client.loop_stop()


def llm_processor(mqtt,mosquitto_ip,llm_model,llm_temperature,llm_max_length) :
    global question_pending   
    llm_proc = llm(llm_model)
    if mqtt=="on" :
        mqtt_client = mqttClient(mosquitto_ip,"llm-Processor")
        mqtt_client.subscribe("vosk_client",llm_proc.store_query)
        while True:
            if question_pending:
                question_pending=False
                mqtt_client.publish("pepper_client","Hello User, thank you for starting a debate. This is a very interesting topic.")
                answer = llm_proc.process_query(llm_temperature,llm_max_length)
                mqtt_client.publish("pepper_client","The answer to your question is " + answer)
            time.sleep(1)
    else :
        while True:
            query= input("Please enter your quote:")
            llm_proc.store_query(query)
            answer = llm_proc.process_query(llm_temperature,llm_max_length)
            print("The answer to your question is " + answer)

def handler(signal_received, frame):
    # Handle cleanup here
    print('SIGINT or CTRL-C detected. Exiting gracefully')
    exit(0)

if __name__ == "__main__":
    signal(SIGINT, handler)
    parser=argparse.ArgumentParser(description='speech recognition with mqtt client')
    parser.add_argument('--mqtt',default="off",help='enable/disable mqtt client (on/off)')
    parser.add_argument('--mosquitto_ip',default='127.0.0.1',help='ip address of the mosquitto server')
    parser.add_argument('--llm_model',default='bigscience/bloom-7b1',help='name of the llm model (e.g. EleutherAI/llm-j-6B or bigscience/bloom-560m)')
    parser.add_argument('--llm_temperature',default=1.0,type=float,help='temperature value for the llm model (between 0.0 and 1.0)')
    parser.add_argument('--llm_max_length',default=200,type=int,help='maximum length of the generated text')
    args=parser.parse_args()

    global question_pending   
    question_pending=False
    llm_processor(args.mqtt,args.mosquitto_ip,args.llm_model,args.llm_temperature,args.llm_max_length)
