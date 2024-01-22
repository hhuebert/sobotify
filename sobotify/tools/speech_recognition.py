import sys
import os
import time
import argparse
from signal import signal, SIGINT
import sounddevice as sd
import queue
import json
from vosk import Model, KaldiRecognizer, SetLogLevel
import winsound
from datetime import datetime
import sobotify.robots.robots as robots
from sobotify.commons.mqttclient import mqttClient

# code based on: https://github.com/alphacep/vosk-api/blob/master/python/example/test_microphone.py

class voskListener:

    def __init__(self,mqtt,mosquitto_ip,robot_name,robot_ip,keyword,model_path,language,sound_device,timeout=20, timeout_silence=2):        
        self.stop_recording_flag=False
        self.start_recording_flag=False
        self.keyword=keyword.lower()
        self.mqtt=mqtt
        self.timeout=timeout
        self.timeout_silence=timeout_silence
        self.start_recording_after_keyword_flag=False
        self.detected_text=False
        self.audio_available=False
        self.samplerate_available=False
        self.audio_data=None
        if self.mqtt=="on" :
            self.mqtt_client = mqttClient(mosquitto_ip,"speech-recognition")
            self.mqtt_client.subscribe("speech-recognition/control/record/listen_to_keyword",self.start_recording_after_keyword)
            self.mqtt_client.subscribe("speech-recognition/control/record/start",self.start_recording)
            self.mqtt_client.publish("speech-recognition/status/init-done")
            self.mqtt_client.subscribe("robot_control/audio",self.store_audio,raw_data=True)
        
        # load vosk model
        full_model_path=os.path.join(model_path,language)

        if not os.path.exists(full_model_path):
            print ("cannot find model at "+full_model_path);
            print ("Please download the model from https://alphacephei.com/vosk/models, unpack it, rename it to \""+language+"\" and copy it to folder "+model_path)
            exit (1)
        print('loading vosk model: ',full_model_path)
        print("please be patient ...")
        SetLogLevel(-1)
        try:
            self.model = Model(full_model_path)
        except Exception:
            print ("error loading the model: ",Exception)
            print ("maybe memory limit reached ==> choose a smaller vosk model")
            exit(1)
        print("... done")
        if self.mqtt=="on" :
            print("waiting for command ...")
        else :
            self.audio=robots.get_sound(robot_name,robot_ip,sound_device)
            self.start_recording_after_keyword("")   

    def store_samplerate(self,samplerate) :
        self.samplerate = int(samplerate)
        #print("samplerate : " + samplerate)
        self.samplerate_available=True

    def start_streaming(self):
        if self.mqtt=="on" :
            self.mqtt_client.subscribe("robot_control/status/samplerate",self.store_samplerate)
            self.mqtt_client.publish("robot_control/command/streaming/start")
            while not self.samplerate_available:
                time.sleep(0.2)
            self.samplerate_available=False
            return self.samplerate
        else:
            self.samplerate = self.audio.start_streaming()
            return self.samplerate

    def stop_streaming(self):
        if self.mqtt=="on" :
            self.mqtt_client.publish("robot_control/command/streaming/stop")
        else:
            self.audio.stop_streaming()

    def store_audio(self,audio_data) :
        self.audio_data = audio_data
        print("got audio_data : "+ str(sys.getsizeof(self.audio_data)))
        #img_byte=bytearray(image)
        #self.log.image(self.image,"raw")
        self.audio_available=True

    def get_audio_data(self):
        if self.mqtt=="on" :
            self.mqtt_client.publish("robot_control/command/get_audio_data","")
            while not self.audio_available:
                time.sleep(0.02)
            self.audio_available=False
            return self.audio_data
        else :
            ret,self.audio_data=self.audio.get_audio_data()
            return self.audio_data

    def record(self):
        self.detected_text=False
        start_recording=datetime.now()  
        start_quiet=datetime.now()  
        query_text=""
        partial_result=""
        samplerate=self.start_streaming()
        rec = KaldiRecognizer(self.model, samplerate)
        while True:
            recording_time   = (datetime.now()-start_recording).total_seconds()
            delta_time_quiet = (datetime.now()-start_quiet).total_seconds()
            if recording_time > self.timeout or (self.detected_text and delta_time_quiet > self.timeout_silence):
                self.stop_streaming()
                return query_text+" "+partial_result

            data = self.get_audio_data()

            # if a full text phrase is ready
            if rec.AcceptWaveform(data):
                text_result=json.loads(rec.Result())["text"].lower()
                query_text+= " " + text_result
                print("text : "+text_result)
                if len(text_result)>0:
                    self.mqtt_client.publish("speech-recognition/text",text_result)

            # if the partial result is extended with a new word
            else:
                partial_result=json.loads(rec.PartialResult())["partial"].lower()
                if not partial_result=="" :
                    start_quiet=datetime.now()  
                    self.detected_text=True
                print("partial text : "+ partial_result)
                if len(partial_result)>0:
                    self.mqtt_client.publish("speech-recognition/partial-text",partial_result)


    def start_recording_after_keyword(self,message) :
        self.start_recording_after_keyword_flag=True

    def find_keyword(self,record_text):
            query_text=""
            samplerate=self.start_streaming()
            rec = KaldiRecognizer(self.model, samplerate)
            while True:
                data = self.get_audio_data()

                # if a full text phrase is ready
                if rec.AcceptWaveform(data):
                    text_result=json.loads(rec.Result())["text"].lower()
                    if record_text: query_text+= " " + text_result
                    # print("text : "+text_result)

                # if the partial resultis extended with a new word
                else:
                    partial_result=json.loads(rec.PartialResult())["partial"].lower()
                    #print(partial_result)
                    if self.keyword in partial_result:
                        partial_result = partial_result.replace(self.keyword,"")
                        if record_text: query_text += " " + partial_result
                        #print ("full text : " + query_text)
                        self.stop_streaming()
                        return query_text
                    
    def get_query(self) :
            # wait for keyword
            print("listening and waiting for keyword: "+self.keyword+" ...")
            self.find_keyword(False)
            winsound.Beep(1000,2000)
            print("found keyword => start recording query ...");
            # listen to query
            query_text=self.find_keyword(True)
            print("... stop recording query")
            winsound.Beep(500,2000)
            print("your query is: " + query_text)
            time.sleep(1)
            return query_text

    def start_recording(self,message):
        self.start_recording_flag=True

    def do_recording(self):
        print("start recording")
        winsound.Beep(1000,2000)
        query_text=self.record()
        winsound.Beep(500,2000)
        if self.mqtt=="on" :
            print("publish message: " + query_text)
            self.mqtt_client.publish("speech-recognition/statement",query_text)

def speechrecognition(mqtt,mosquitto_ip,robot_name,robot_ip,keyword,vosk_model_path,language,sound_device, timeout, timeout_silence):
    listener = voskListener(mqtt,mosquitto_ip,robot_name,robot_ip,keyword,vosk_model_path,language,sound_device,timeout, timeout_silence)
    while True: 
        if listener.start_recording_after_keyword_flag==True:
            query_text=listener.get_query()
            if mqtt=="on" :
                listener.mqtt_client.publish("speech-recognition/statement",query_text)
            else :
                print("message: "+ query_text)
        if listener.start_recording_flag==True:
            listener.start_recording_flag=False
            listener.do_recording()
        time.sleep(0.5)

if __name__ == "__main__":
    parser=argparse.ArgumentParser(description='speech recognition with mqtt client')
    parser.add_argument('--mqtt',default="off",help='enable/disable mqtt client (on/off)')
    parser.add_argument('--mosquitto_ip',default='127.0.0.1',help='ip address of the mosquitto server')
    parser.add_argument('--robot_name',default='stickman',help='name of the robot (stickman,pepper)')
    parser.add_argument('--robot_ip',default='127.0.0.1',help='ip address of the robot')
    parser.add_argument('--vosk_model_path',default=os.path.join(os.path.expanduser("~"),".sobotify","vosk","models"),help='path to vosk_model')
    parser.add_argument('--language',default="english",help='choose language (english,german)')
    parser.add_argument('--keyword',default='apple tree',help='key word to activate vosk listener')
    parser.add_argument('--sound_device',default=0,type=int,help='number of sound device, can be found with: import sounddevice;sounddevice.query_devices()')
    parser.add_argument('--timeout',default=20.0,type=int,help='timeout in seconds, after which the recording stops')
    parser.add_argument('--timeout_silence',default=2.0,type=int,help='time of silence in seconds, after which the recording stops')
    args=parser.parse_args()
    speechrecognition(args.mqtt,args.mosquitto_ip,args.robot_name,args.robot_ip,args.keyword,args.vosk_model_path,args.language,args.sound_device,args.timeout,args.timeout_silence)
