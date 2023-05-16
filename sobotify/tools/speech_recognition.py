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

from sobotify.commons.mqttclient import mqttClient

# code based on: https://github.com/alphacep/vosk-api/blob/master/python/example/test_microphone.py

class voskListener:

    def __init__(self,keyword,model_path,language,sound_device):        
        self.keyword=keyword.lower()
        self.sound_device=int(sound_device)
        # get samplerate from audiodevice
        try:
            device_info = sd.query_devices(self.sound_device, "input")
        except ValueError:
            print(sd.query_devices())
            print("==========================================================")
            print ("Error: Could not open the selected input sound device : " +  str(self.sound_device))
            print ("Choose a different device from the list above (must have inputs)")
            print ("   and provide it with the argument --sound_device")
            exit()
        self.samplerate = int(device_info["default_samplerate"])

        #create queue for storing audio samples
        self.audioqueue = queue.Queue()

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

   # this function is called from the sound device handler to store the audio block in the queue
    def callback(self,indata, frames, time, status):
        """This is called (from a separate thread) for each audio block."""
        if status:
            print(status, file=sys.stderr)
        self.audioqueue.put(bytes(indata))


    def find_keyword(self,record_text):
        query_text=""
        with sd.RawInputStream(samplerate=self.samplerate, blocksize = 8000, device=self.sound_device,
                dtype="int16", channels=1, callback=self.callback):
            rec = KaldiRecognizer(self.model, self.samplerate)
            while True:
                data = self.audioqueue.get()

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
                        return query_text
                    
    def get_query(self) :
           # wait for keyword
            print("listening and waiting for keyword: "+self.keyword+" ...")
            self.find_keyword(False)
            winsound.Beep(1000,1000)
            print("found keyword => start recording query ...");
            # listen to query
            query_text=self.find_keyword(True)
            print("... stop recording query");
            winsound.Beep(500,1000)
            print("your query is: " + query_text)
            time.sleep(1)
            return query_text

def speechrecognition(mqtt,mosquitto_ip,vosk_keyword,vosk_model_path,language,sound_device):
    if mqtt=="on" :
        mqtt_client = mqttClient(mosquitto_ip,"speech-recognition")
    vosk_listener = voskListener(vosk_keyword,vosk_model_path,language,sound_device)
    while True: 
        query_text=vosk_listener.get_query()
        if mqtt=="on" :
            mqtt_client.publish("speech-recognition/statement",query_text)

if __name__ == "__main__":
    parser=argparse.ArgumentParser(description='speech recognition with mqtt client')
    parser.add_argument('--mqtt',default="off",help='enable/disable mqtt client (on/off)')
    parser.add_argument('--mosquitto_ip',default='127.0.0.1',help='ip address of the mosquitto server')
    parser.add_argument('--vosk_model_path',default=os.path.join(os.path.expanduser("~"),".sobotify","vosk","models"),help='path to vosk_model')
    parser.add_argument('--language',default="english",help='choose language (english,german)')
    parser.add_argument('--vosk_keyword',default='apple tree',help='key word to activate vosk listener')
    parser.add_argument('--sound_device',default=0,type=int,help='number of sound device, can be found with: import sounddevice;sounddevice.query_devices()')
    args=parser.parse_args()
    speechrecognition(args.mqtt,args.mosquitto_ip,args.vosk_keyword,args.vosk_model_path,args.language,args.sound_device)