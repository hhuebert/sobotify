from signal import signal, SIGINT
from sys import exit
import time
import argparse
from sobotify import sobotify
import ast

class debate_partner:

    def __init__(self,robot_name,robot_ip,language,keyword,sound_device,mosquitto_ip) :
        print ("init debate partner ...")
        self.statement_pending=False
        self.reply_pending=False
        self.sobot=sobotify.sobotify(app_name="debate-partner",mosquitto_ip=mosquitto_ip,debug=False)
        self.sobot.start_listener(mosquitto_ip=mosquitto_ip,language=language,keyword=keyword,sound_device=sound_device)
        self.sobot.start_robotcontroller(robot_name=robot_name,mosquitto_ip=mosquitto_ip,robot_ip=robot_ip, language=language)
        self.sobot.subscribe_listener(self.store_statement)
        self.sobot.start_grammar_checking(language=language)
        print (" ... done")

    def store_statement(self,statement) :
        self.statement = statement
        print("got statement from human: "+ self.statement)
        self.statement_pending=True

    def evaluate_grammar(self,text):
        errors_raw=self.sobot.grammar_check(text)
        errors=ast.literal_eval(errors_raw)
        for error in errors :
            issue_text=error.get("issue","")
            message=error.get("message","")
            short_message=error.get("short_message","")
            replacement=error.get("replacement","")
            print ("--------------------------------------------------------------------------------------------")
            print ("Error         : " + issue_text)
            print ("Message       : " + message)
            print ("Short message : " + short_message)
            print ("Suggestion    : " + issue_text + " => " + replacement)
        if len(errors)==0:
            return False
        else :
            return True

    def run(self) :
        self.sobot.listen(listen_to_keyword=True)
        while True:
            if self.statement_pending:
                self.statement_pending=False
                errors=self.evaluate_grammar(self.statement)
                if errors==True:
                    self.sobot.speak("One or more mistakes are there")
                else:
                    self.sobot.speak("very good")
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
    args=parser.parse_args()

    debate = debate_partner(args.robot_name,args.robot_ip,args.language,args.keyword,args.sound_device,args.mosquitto_ip)
    debate.run()