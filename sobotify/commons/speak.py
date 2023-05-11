import sys
import pyttsx3
import argparse

class VirtBotSpeech():

    def __init__(self):
        self.engine = pyttsx3.init()
        self.engine.setProperty('voice', "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\TTS_MS_EN-US_ZIRA_11.0")
        self.engine.setProperty('rate',100);
        self.voices = self.engine.getProperty('voices')
        
    def setLanguage(self, language_string):
        if language_string.lower()=="english":
            self.engine.setProperty('voice', "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\TTS_MS_EN-US_ZIRA_11.0")
        if language_string.lower()=="german":
            self.engine.setProperty('voice', "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\TTS_MS_DE-DE_HEDDA_11.0")      

    def setSpeed(self, speedVal):
        speed=2*speedVal;
        self.engine.setProperty('rate',speed);      
        print ("set speed to:",speed), 

    def say(self, Text):
        self.engine.say(Text)
        self.engine.runAndWait()

if __name__ == "__main__":
    VB=VirtBotSpeech();
    
    parser=argparse.ArgumentParser(description='The Social Robot Framework')
    parser.add_argument('--language',default="english",help='choose language (english,german)')
    parser.add_argument('--speed',default=100,help='speech speed of robot')
    parser.add_argument('--message',default='Hello World',help='message to be spoken by the robot')
    args=parser.parse_args()   
    VB.setLanguage(args.language)
    VB.setSpeed(int(args.speed))
    VB.say(args.message)
