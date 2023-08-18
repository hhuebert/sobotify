import paho.mqtt.client as mqtt
from signal import signal, SIGINT
import os
from sys import exit
import time
import argparse
from sobotify.commons.mqttclient import mqttClient
import json
import requests

#llm dummy class (use the real class above if llm (llm-J, BLOOM,...) is installed)
class llm_dummy:

    def __init__(self,ll_model) :
        self.query=''
        print ("init chatbot ...", flush=True)
        time.sleep(1) 
        print (" finished")
        
    def process_query(self) :
        print ("process query with llm dummy: " + self.query)
        time.sleep(3) 
        #self.gen_text = "42"
        self.gen_text = "This an important topic to talk about, and there are many different opinions about this issue. Also in research and literature it has been discussed in many ways (But be aware, this is not a real answer to your topic)."
        return self.gen_text

    def store_query(self,query) :
        global question_pending     
        self.query = query
        print("got query: "+ self.query)
        question_pending=True


class llm_json_api:

    def __init__(self,json_options) :
        print ("init chatbot ...", flush=True)
        self.query=''
        parser=argparse.ArgumentParser(description='argument parser for json api')
        parser.add_argument('--URL',default="",help='')
        parser.add_argument('--headers',default="",help='')
        parser.add_argument('--options',default="",help='')
        parser.add_argument('--query_key',default="",help='')
        json_api_args=parser.parse_args(json_options.strip('"').split())   

        self.URL=json_api_args.URL
        self.headers=json_api_args.headers.replace("'",'"')
        self.options=json_api_args.options.replace("'",'"')
        self.query_key=json_api_args.query_key
        print ("URL       =",self.URL)        
        print ("headers   =",self.headers)
        print ("options   =",self.options)
        print ("query key =",self.query_key)
        time.sleep(1) 
        print (" finished")
        
    def process_query(self) :
        json_query={self.query_key:self.query}
        json_data=json.loads(self.options)
        json_data.update(json_query)
        try:
            reply=requests.post(url=self.URL,json=json_data)
            self.gen_text=reply.text
        except:
            print ("error accessing llm api with following settings")
            print ("  URL=",self.URL)        
            print ("  json_data=",json_data)        
            self.gen_text=""
        print("reply is : "+ self.gen_text)
        return self.gen_text

    def store_query(self,query) :
        global question_pending     
        self.query = query.strip()
        print("got query: "+ self.query)
        question_pending=True



def llm_processor(mqtt,mosquitto_ip,llm_name,llm_options) :
    global question_pending  
    if llm_name=="dummy":
        llm_proc = llm_dummy(llm_options)
    elif llm_name=="json_api":
        llm_proc = llm_json_api(llm_options)
    else:
        print("unknown llm api, using llm dunmny")
        llm_proc = llm_dummy(llm_options)

    if mqtt=="on" :
        mqtt_client = mqttClient(mosquitto_ip,"llm")
        mqtt_client.subscribe("llm/query",llm_proc.store_query)
        mqtt_client.publish("llm/status/init-done")
        while True:
            if question_pending:
                question_pending=False
                answer = llm_proc.process_query()
                mqtt_client.publish("llm/reply",answer)
            time.sleep(1)
    else :
        while True:
            query= input("Please enter your quote:")
            llm_proc.store_query(query)
            answer = llm_proc.process_query()
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
    parser.add_argument('--llm_name',default="dummy",help='name of llm api')
    parser.add_argument('--llm_options',default="",help='options for llm')
    args=parser.parse_args()

    global question_pending   
    question_pending=False
    llm_processor(args.mqtt,args.mosquitto_ip,args.llm_name,args.llm_options)
