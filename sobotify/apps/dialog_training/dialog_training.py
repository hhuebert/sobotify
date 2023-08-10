from signal import signal, SIGINT
from sys import exit
import time
import argparse
from tkinter.messagebox import QUESTION
from sobotify import sobotify
import random
from read_project_data import get_project_info
from read_project_data import get_project_settings

"""
Attribution: 
This app was created by Haeseon Yun 
Only minor modification were applied/added 
  (e.g. refactoring, read project data)
"""

class dialogTraining:

    def __init__(self,robot_name,robot_ip,language,sound_device,mosquitto_ip,project_file) :
        print ("init dialog training")
        self.general_info,self.task_groups=get_project_info(project_file)
        self.sobot=sobotify.sobotify(app_name="dialog-training",debug=False,log=True)
        self.sobot.start_emotion_detection(robot_name=robot_name,robot_ip=robot_ip)
        self.sobot.start_robotcontroller(robot_name=robot_name,robot_ip=robot_ip, language=language)
        self.sobot.start_listener(language=language,sound_device=sound_device)
        print (" ... done")

    def emotion_feedback(self,emotion):
        if emotion=="none" :
            print("no emotion detected => no feedback")
            self.sobot.log("emotion_feedback","none") 
        elif emotion=="happy" :
            time.sleep(1)
            self.sobot.speak(random.choice(self.general_info["happy_emotion_hints"]),gesture=random.choice(self.general_info["happy_gesture"]))
            time.sleep(1)
            self.sobot.log("emotion_feedback","happy") 
        elif emotion=="sad":
            time.sleep(1)
            self.sobot.speak(random.choice(self.general_info["sad_emotion_hints"]),gesture=random.choice(self.general_info["neutral_gesture"]))
            time.sleep(1)
            self.sobot.log("emotion_feedback","sad") 
        elif emotion=="neutral" :
            time.sleep(1)
            self.sobot.speak(random.choice(self.general_info["neutral_emotion_hints"] ),gesture=random.choice(self.general_info["neutral_gesture"]))
            time.sleep(1)
            self.sobot.log("emotion_feedback","neutral") 
        else: 
            time.sleep(1)
            self.sobot.speak(random.choice(self.general_info["negative_emotion_hints"] ),gesture=random.choice(self.general_info["negative_gesture"] ))
            time.sleep(1)
            self.sobot.log("emotion_feedback","negative") 
        #MAKE random list so that there are various feedback


    def search_keywords(self,keywords,answer) :
        for keyword in keywords :
            print("seraching for >"+keyword.lower()+"< in >"+answer.lower()+"<")
            self.sobot.log("search_keywords",keyword.lower()+"< in >"+answer.lower())
            if keyword.lower() in answer.lower() :
                return True
        return False   

    def search_keyword_groups(self,keyword_groups,answer) :
        for keywords in keyword_groups :
            if not self.search_keywords(keywords,answer) :
                return False
        return True   
    
    def process_task(self,task) :
        speed=80
        for i in range(2) :
            speed=speed-5
            time.sleep(1)
            self.sobot.speak(task["question"][i],speed=speed,detect_emotion=False)
            #print("ASKIMG_EMOTION: " + asking_emotion)
            #answer=self.sobot.listen()
            answer,listening_emotion=self.sobot.listen(detect_emotion=True)
            print ("LISTENING_EMOTION: " + listening_emotion)
            self.sobot.log("Listenin_emotion", listening_emotion)

            if len(answer.split())<=1 and not self.search_keyword_groups(task["keywords"],answer) : 
                time.sleep(1)
                self.sobot.speak(self.general_info["affirmation"], speed=speed)
                self.sobot.log("feedback","incorrect") 
                self.emotion_feedback(listening_emotion)

            elif self.search_keyword_groups(task["keywords"],answer) and not self.search_keyword_groups(task["phrase"],answer) and self.search_keyword_groups(task["pronunciation1"],answer) :
                print ("1")
                time.sleep(1)
                self.sobot.speak(task["keyword_hint"])
                self.sobot.log("hint","keyword_hint")
                time.sleep(1)
                self.sobot.speak(task["hint4"])
                self.sobot.log("hint","hint4")
                self.emotion_feedback(listening_emotion)
                #self.sobot.speak(task["phrase_hint"])
                break

            elif self.search_keyword_groups(task["keywords"],answer) and not self.search_keyword_groups(task["phrase"],answer) :
                print ("2")
                time.sleep(1)
                self.sobot.speak(task["keyword_hint"])
                self.sobot.log("hint","keyword_hint")
                time.sleep(1)
                self.sobot.speak(task["phrase_hint"])
                self.sobot.log("hint","phrase_hint")
                self.emotion_feedback(listening_emotion)
                break

            elif len(answer.split())<=2 and self.search_keyword_groups(task["keywords"],answer) :
                print ("3---------Keyword + NOT LONG----------")
                time.sleep(1)
                self.sobot.speak(self.general_info["full_sentence_request"], speed=speed, gesture=random.choice(self.general_info["happy_gesture"]))
                time.sleep(1)
                self.sobot.speak(task["phrase_hint"])
                self.sobot.log("hint","phrase_hint")
                self.emotion_feedback(listening_emotion)
                break
            elif not self.search_keyword_groups(task["keywords"],answer) :
                print ("4---------NOT Keyword----------")
                time.sleep(1)
                self.sobot.speak(task["hint1"],speed=speed)
                self.sobot.log("hint","hint1")
                self.emotion_feedback(listening_emotion)

                
            elif self.search_keyword_groups(task["keywords"],answer) and self.search_keyword_groups(task["phrase"],answer) and self.search_keyword_groups(task["adjective"],answer) :
                print ("5---------Keyword + Phrase + Adjective----------")
                time.sleep(1)
                self.sobot.speak(random.choice(self.general_info["perfect_feedback"]),gesture=random.choice(self.general_info["happy_gesture"]))
                time.sleep(1)
                self.sobot.log("achievement","all_correct")
                self.emotion_feedback(listening_emotion)

                return True
            else : 
                print ("6-------NOT ADJECTIVE----------")
                time.sleep(1)
                self.sobot.speak(task["adjective_hint"], speed=speed)
                self.sobot.log("hint","adjective_hint")
                self.emotion_feedback(listening_emotion)
                break

        for i in range(1) :
            speed=speed-5
            time.sleep(1)
            self.sobot.speak(task["question"][i+1],speed=speed)
            answer=self.sobot.listen()
            if self.search_keyword_groups(task["phrase"],answer) :
                print("a-----KW PASS---------Phrase Check-----------------")
                if not self.search_keyword_groups(task["adjective"],answer) :
                    print("b----KW PASS---------Phrase PASS-----NOT Adjective----------")
                    time.sleep(1)
                    self.sobot.speak(task["adjective_hint"])
                    self.sobot.log("hint","adjective_hint")
                    self.emotion_feedback(listening_emotion)

                else :
                    if self.search_keyword_groups(task["grammar1"],answer):
                        print("c-----KW PASS---------Phrase Pass--------NOT Grammar---------")
                        time.sleep(1)
                        self.sobot.speak(task["hint2"], speed=speed)
                        self.sobot.log("hint","hint2") 
                        time.sleep(1)
                        self.sobot.speak(task["hint3"] + task["answer"], speed=speed)
                        self.sobot.log("hint","hint3") 
                        self.sobot.log("hint","answer")
                        self.emotion_feedback(listening_emotion)
                        return True

                    else : #not self.search_keyword_groups(task["grammar1"],answer) : 
                        print("d----KW PASS----Phrase PASS----------------")
                        time.sleep(1)
                        self.sobot.speak(random.choice(self.general_info["great_job_feedback"]), speed=speed, gesture=random.choice(self.general_info["happy_gesture"])) #NEED List of praise sentences. 
                        time.sleep(1)
                        self.sobot.log("feedback","positive")
                        if self.search_keyword_groups(task["pronunciation1"],answer):
                            print("e-----KW PASS----Phrase PASS------X Pronunciation-----")
                            time.sleep(1)
                            self.sobot.speak(task["hint4"] + self.general_info["once_again"] + task["answer"], speed=speed)
                            self.sobot.log("hint","hint4")
                            self.sobot.log("hint","answer")

                            time.sleep(1)  
                            self.sobot.speak(self.general_info["reply_great"], speed=speed, gesture=random.choice(self.general_info["happy_gesture"]))
                            time.sleep(1)
                            self.sobot.log("feedback","achievement_positive")
                            self.emotion_feedback(listening_emotion)
                            return True

                        else : 
                            print("f-----KW PASS----Phrase PASS------Pronnciation PASS-----")
                            #ALL Correct NEED List of praise sentences. 
                            time.sleep(1)
                            self.sobot.speak(random.choice(self.general_info["great_job_feedback"]),gesture=random.choice(self.general_info["happy_gesture"]))
                            time.sleep(1)
                            self.sobot.log("feedback","achievement_positive")
                            self.emotion_feedback(listening_emotion)
                            return True
            #elif not self.search_keyword_groups(task["phrase"],answer) and self.search_keyword_groups(task["pronunciation1"],answer): 
            #    self.sobot.speak(task["hint4"], speed)
            #elif not self.search_keyword_groups(task["phrase"],answer) and not self.search_keyword_groups(task["pronunciation1"],answer): 
            #    self.sobot.speak(task["phrase_hint"])
            #else :
            #    self.sobot.speak(task["hint1"], speed)
        print("g")
        time.sleep(1)
        self.sobot.speak(task["hint3"])
        self.sobot.log("hint","hint3") 
        time.sleep(1)
        self.sobot.speak(task["answer"])
        self.sobot.log("hint","answer") 

    def run(self) :
        self.sobot.speak(self.general_info["welcome"])
        time.sleep(1)
        self.sobot.speak(self.general_info["welcome2"])
        time.sleep(1)
        for num,tasks in enumerate(self.task_groups):
            self.sobot.speak(self.general_info["getprepared_dialog"][num])
            time.sleep(10)
            self.sobot.speak(self.general_info["getstarted"])     
            for task in tasks:
                self.process_task(task)
                time.sleep(1)    
            self.sobot.speak(self.general_info["taskdone"][num],gesture=random.choice(self.general_info["intermediate_gesture"]))
            time.sleep(10)

        self.sobot.speak(self.general_info["farewell"],gesture=random.choice(self.general_info["intermediate_gesture"]))

    def terminate(self):
        self.sobot.terminate()

def handler(signal_received, frame):
    # Handle cleanup here
    print('SIGINT or CTRL-C detected. Exiting gracefully')
    training.terminate()
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

    training = dialogTraining(args.robot_name,args.robot_ip,args.language,args.sound_device,args.mosquitto_ip,args.project_file)
    training.run()
    print("done")
    while True:
        time.sleep(1)    
