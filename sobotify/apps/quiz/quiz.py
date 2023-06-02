from signal import signal, SIGINT
from sys import exit
import time
import argparse
from sobotify import sobotify
from read_project_data import get_tasks
from read_project_data import get_general_info
from read_project_data import get_project_settings

class quiz:

    def __init__(self,robot_name,robot_ip,language,sound_device,mosquitto_ip,project_file) :
        print ("init quiz training ...")
        self.sobot=sobotify.sobotify(app_name="quiz-training",debug=False)
        self.sobot.start_robotcontroller(robot_name=robot_name,robot_ip=robot_ip, language=language)
        self.sobot.start_listener(language=language,sound_device=sound_device)
        self.general_info=get_general_info(project_file)
        self.tasks=get_tasks(project_file)
        print (" ... done")

    def search_answers(self,keywords,answer) :
        for keyword in keywords :
            if keyword.lower() in answer.lower() :
                return True
        return False   

    def search_answer_groups(self,keyword_groups,answer) :
        for keywords in keyword_groups :
            if not self.search_answers(keywords,answer) :
                return False
        return True   

    def process_task(self,task) :
        self.sobot.speak(task["question"])
        for i in range(3) :
            if i>0 : self.sobot.speak(task["question2"])
            answer=self.sobot.listen()
            if len(answer)<=1: self.sobot.speak(self.general_info["noanswer"])
            else :
                if self.search_answer_groups(task["answers"],answer) : 
                    self.sobot.speak(self.general_info["correct"])
                    return True
                else :     
                    self.sobot.speak(self.general_info["incorrect"])
        self.sobot.speak(task["answer"])
        return False

    def run(self) :
        correct_answers=0
        self.sobot.speak(self.general_info["welcome"],speed=70)
        for task in self.tasks:
            if self.process_task(task): correct_answers+=1
            time.sleep(1)    
            
        self.sobot.speak(self.general_info["score"]+" "+str(round(correct_answers/len(self.tasks)*100))+ " %")
        #self.sobot.speak(f"You scored {correct_answers} out of {len(tasks)} tasks correct.")
        self.sobot.speak(self.general_info["farewell"])

    def terminate(self):
        self.sobot.terminate()

def handler(signal_received, frame):
    # Handle cleanup here
    print('SIGINT or CTRL-C detected. Exiting gracefully')
    quiz_training.terminate()
    exit(0)

if __name__ == "__main__":
    signal(SIGINT, handler)
    parser=argparse.ArgumentParser(description='speech recognition with mqtt client')
    parser.add_argument('--mosquitto_ip',default='127.0.0.1',help='ip address of the mosquitto server')
    parser.add_argument('--robot_name',default='stickman',help='name of the robot (stickman,pepper,nao)')
    parser.add_argument('--robot_ip',default='127.0.0.1',help='ip address of the robot')
    parser.add_argument('--language',default="english",help='choose language (english,german)')
    parser.add_argument('--sound_device',default=0,type=int,help='number of sound device, can be found with: import sounddevice;sounddevice.query_devices()')
    parser.add_argument('--project_file',default='quiz_data.xlsx',help='project file with app data')
    args=parser.parse_args()

    quiz_training = quiz(args.robot_name,args.robot_ip,args.language,args.sound_device,args.mosquitto_ip,args.project_file)
    quiz_training.run()
    print("done")
    while True:
        time.sleep(1)    
