from signal import signal, SIGINT
from sys import exit
import time
import argparse
from sobotify import sobotify

class debate_partner:

    def __init__(self,robot_name,robot_ip,language,keyword,mosquitto_ip) :
        print ("init debate partner")
        self.statement_pending=False
        self.reply_pending=False
        self.sobot=sobotify.sobotify(app_name="debate-partner",debug=False)
        self.sobot.start_mosquitto()
        self.sobot.start_robotcontrol(robot_name=robot_name,robot_ip=robot_ip, language=language)
        self.sobot.start_llm_processor()
        self.sobot.start_speech_recognition(language=language,keyword=keyword)
        self.sobot.subscribe_llm_reply(self.store_reply)
        self.sobot.subscribe_speech_recognition(self.store_statement)

    def store_statement(self,statement) :
        self.statement = statement
        print("got statement from human: "+ self.statement)
        self.statement_pending=True

    def store_reply(self,reply) :
        self.reply = reply
        print("got reply from llm: "+ self.reply)
        self.reply_pending=True

    def run(self) :
        while True:
            if self.statement_pending:
                self.statement_pending=False
                self.sobot.robot_say_and_gesture("Hello user, thank you for starting a debate. This is a very interesting topic.")
                self.sobot.llm_send_request(self.statement)
            if self.reply_pending:
                self.reply_pending=False
                self.sobot.robot_say_and_gesture("My reply is " + self.reply)
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
    args=parser.parse_args()

    debate = debate_partner(args.robot_name,args.robot_ip,args.language,args.keyword,args.mosquitto_ip)
    debate.run()