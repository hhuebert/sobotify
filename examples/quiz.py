from signal import signal, SIGINT
from sys import exit
import time
import argparse
from sobotify import sobotify


tasks=[]
tasks.append({
    "question":"What is 4 times 12?",
    "answers":["forty eight"]
    })
tasks.append({
    "question":"Please name a shape with 4 corners?",
    "answers":["rectangle","square","rhombus","parallelogram","trapezoid","kite"]
    })
tasks.append({
    "question":"Is 7 a prime number?",
    "answers":["yes","yeah","true","right","sure"]
    })

class quiz:

    def __init__(self,robot_name,robot_ip,language,sound_device,mosquitto_ip) :
        print ("init quiz training ...")
        self.sobot=sobotify.sobotify(app_name="quiz-training",debug=False)
        self.sobot.start_robotcontroller(robot_name=robot_name,robot_ip=robot_ip, language=language)
        self.sobot.start_listener(language=language,sound_device=sound_device)
        time.sleep(10) # wait for all finish start up phase
        print (" ... done")

    def search_answer(self,keywords,answer) :
        for keyword in keywords :
            if keyword.lower() in answer.lower() :
                return True
        return False   

    def process_task(self,task) :
        self.sobot.speak(task["question"])
        for i in range(3) :
            if i>0 : self.sobot.speak("Please try again")
            answer=self.sobot.listen()
            if len(answer)<=1: self.sobot.speak("Sorry, I didn't hear your answer. Maybe it came to late or it was not loud enough.")
            else :
                if self.search_answer(task["answers"],answer) : 
                    self.sobot.speak("This is correct, very good.")
                    return True
                else :     
                    self.sobot.speak("the answer is not correct.")
        self.sobot.speak("a correct answer is "+ task["answers"][0])
        return False

    def run(self) :
        correct_answers=0
        self.sobot.speak("We will do a math quiz now. Please answer right after my questions")
        for task in tasks:
            if self.process_task(task): correct_answers+=1
            time.sleep(1)    
        self.sobot.speak(f"Thank you for taking part in the math quiz. You scored {correct_answers} out of {len(tasks)} tasks correct.")

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
    args=parser.parse_args()

    quiz_training = quiz(args.robot_name,args.robot_ip,args.language,args.sound_device,args.mosquitto_ip)
    quiz_training.run()
    print("done")
    while True:
        time.sleep(1)    
