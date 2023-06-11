import paho.mqtt.client as mqtt
from signal import signal, SIGINT
import os
from sys import exit
import time
import argparse
from sobotify.commons.mqttclient import mqttClient
import requests
import json
import subprocess

URL_default="http://localhost:8081/v2/check"

class GrammarChecker:
    
    #java -cp languagetool-server.jar org.languagetool.server.HTTPServer --port 8081 --allow-origin

    def __init__(self,languagetool_path,java_path,language,URL) :
        self.URL=URL
        self.start_check_flag=False
        self.text=""
        if language.lower()=="english":
            self.language="en-US"
        elif language.lower()=="german":
            self.language="de-DE"
        print ("init grammar checker ...", flush=True)
        languagetool_full_path=os.path.join(languagetool_path,"languagetool-server.jar")
        #java_path=os.path.join(os.environ["ProgramFiles"],"Java","jdk","bin","java.exe")
        java_path=os.path.join(java_path,"java.exe")
        arguments=[java_path]
        arguments.extend(('-cp',languagetool_full_path))
        arguments.append('org.languagetool.server.HTTPServer')
        arguments.extend(('--port',"8081"))
        arguments.append('--allow-origin')
        #if self.debug==True:
        print (*arguments)
        self.languagetool_proc=subprocess.Popen(arguments,creationflags=subprocess.CREATE_NEW_CONSOLE)
        time.sleep(5) 
        print ('started LanguageTool server, pid=',self.languagetool_proc.pid)
        print (" finished")



    def check(self,text) :
        results=[]
        #result=requests.post(self.URL,data={"text":text,"language":language,"level":"picky","enabledCategories":"GRAMMAR","enabledOnly":"true"})
        #result=requests.post(self.URL,data={"text":text,"language":self.language,"level":"picky"})
        #result=requests.post(self.URL,data={"text":text,"language":self.language,"disabledCategories":"TYPOS,CASING"})
        result=requests.post(self.URL,data={"text":text,"language":self.language})
        print (result.text)
        result_dict=json.loads(result.text)
        print(json.dumps(result_dict,indent=2,ensure_ascii=False))
        for issue in result_dict["matches"] :
            result={}
            offset=int(issue.get("offset","0"))
            length=int(issue.get("length","0"))
            issue_text=text[offset:offset+length]
            message=issue.get("message","")
            short_message=issue.get("shortMessage","")
            replacements=issue.get("replacements","")
            if len(replacements)>0:
                replacement=replacements[0].get("value","")
            else:
                replacement=""
            result["issue"]=issue_text
            result["message"]=message
            result["short_message"]=short_message
            result["replacement"]=replacement
            results.append(result)
            print ("--------------------------------------------------------------------------------------------")
            print ("Error         : " + issue_text)
            print ("Message       : " + message)
            print ("Short message : " + short_message)
            print ("Suggestion    : " + issue_text + " => " + replacement)
        return results

    def start_check(self,message) :
        self.start_check_flag=True
        self.text=message

    def stop_detection(self,message) :
        self.stop_detection_flag=True

def grammar_checking(mqtt,mosquitto_ip,languagetool_path,java_path,language,URL,text) :
    grammar_check = GrammarChecker(languagetool_path,java_path,language,URL)
    if mqtt=="on" :
        mqtt_client = mqttClient(mosquitto_ip,"grammar_checking")
        mqtt_client.subscribe("grammar_checking/text",grammar_check.start_check)
        mqtt_client.publish("grammar_checking/status/init-done")
        while True:
            if grammar_check.start_check_flag:
                grammar_check.start_check_flag=False
                result=grammar_check.check(grammar_check.text)
                #print (result)
                mqtt_client.publish("grammar_checking/result",str(result))
            time.sleep(1)
    else :
        result=grammar_check.check(text)
        #print("Results of grammar check")
        #print(result)
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
    parser.add_argument('--mosquitto_ip',default='127.0.0.1',help='ip address of the mosquitto server')
    parser.add_argument('--languagetool_path',default=os.path.join(os.path.expanduser("~"),".sobotify","languagetool"),help='directory path to LanguageTool')
    parser.add_argument('--java_path',default=os.path.join(os.environ["JAVA_HOME"],"bin"),help='directory path to java executable')
    parser.add_argument('--language',default="english",help='choose language (english,german)')
    parser.add_argument('--languagetool_url',default=URL_default,help='URL of LanguageTool server')
    parser.add_argument('--text',default="",help='text to be checked')
    args=parser.parse_args()

    grammar_checking(args.mqtt,args.mosquitto_ip,args.languagetool_path,args.java_path,args.language,args.languagetool_url,args.text)
