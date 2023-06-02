import paho.mqtt.client as mqtt
from signal import signal, SIGINT
import os
from sys import exit
import time
import argparse
from sobotify.commons.mqttclient import mqttClient

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
        #self.gen_text = "42"
        self.gen_text = "This an important topic to talk about, and there are many different opinions about this issue. Also in research and literature it has been discussed in many ways (But be aware, this is not a real answer to your topic)."
        return self.gen_text

    def store_query(self,query) :
        global question_pending     
        self.query = query
        print("got query: "+ self.query)
        question_pending=True

def llm_processor(mqtt,mosquitto_ip,llm_model,llm_temperature,llm_max_length) :
    global question_pending   
    llm_proc = llm(llm_model)
    if mqtt=="on" :
        mqtt_client = mqttClient(mosquitto_ip,"llm")
        mqtt_client.subscribe("llm/query",llm_proc.store_query)
        mqtt_client.publish("llm/status/init-done")
        while True:
            if question_pending:
                question_pending=False
                answer = llm_proc.process_query(llm_temperature,llm_max_length)
                mqtt_client.publish("llm/reply",answer)
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
