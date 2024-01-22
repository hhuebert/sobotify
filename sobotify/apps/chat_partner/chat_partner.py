from signal import signal, SIGINT
from sys import exit
import time
import argparse
from sobotify import sobotify
from read_project_data import get_project_info

class chat_partner:

    def __init__(self,robot_name,robot_ip,language,keyword,sound_device,mosquitto_ip,project_file) :
        print ("init chat partner ...")
        self.statement_pending=False
        self.reply_pending=False
        self.general_info=get_project_info(project_file)
        print (self.general_info)

        self.sobot=sobotify.sobotify(app_name="chat-partner",mosquitto_ip=mosquitto_ip,debug=True)
        self.sobot.start_listener(mosquitto_ip=mosquitto_ip,language=language,keyword=self.general_info["key_word"])
        self.sobot.start_robotcontroller(robot_name=robot_name,mosquitto_ip=mosquitto_ip,robot_ip=robot_ip, language=language,sound_device=sound_device)
        self.sobot.start_chatbot(llm_name= self.general_info["llm_name"],llm_options= self.general_info["llm_options"])
        self.sobot.subscribe_listener(self.store_statement)
        self.sobot.subscribe_chatbot(self.store_reply)
        print (" ... done")

    def store_statement(self,statement) :
        self.statement = statement
        print("got statement from human: "+ self.statement)
        self.statement_pending=True

    def store_reply(self,reply) :
        self.reply = reply
        print("got reply from llm: "+ self.reply)
        self.reply_pending=True

    def run(self) :
        self.sobot.speak(self.general_info["welcome"])
        self.sobot.speak(self.general_info["key_word_intro"])
        self.sobot.speak(self.general_info["key_word"])
        self.sobot.listen(listen_to_keyword=True)
        while True:
            if self.statement_pending:
                self.statement_pending=False
                self.sobot.chat(self.statement)
                self.sobot.speak(self.general_info["query_intro"])
            if self.reply_pending:
                self.reply_pending=False
                self.sobot.speak(self.general_info["reply_intro"] + " " + self.reply)
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

    debate = chat_partner(args.robot_name,args.robot_ip,args.language,args.keyword,args.sound_device,args.mosquitto_ip,args.project_file)
    debate.run()