from signal import signal, SIGINT
from sys import exit
import time
import argparse
from sobotify import sobotify
from read_project_data import get_project_info

default_timeout=60

class teleoperation:

    def __init__(self,robot_name,robot_ip,language,sound_device,mosquitto_ip,project_file) :
        print ("init teleoperation ...")
        self.general_info=get_project_info(project_file)
        print (self.general_info)

        self.sobot=sobotify.sobotify(app_name="teleoperation",mosquitto_ip=mosquitto_ip,debug=False, log=False)
        self.sobot.start_robotcontroller(robot_name=robot_name,mosquitto_ip=mosquitto_ip,robot_ip=robot_ip, language=language, cam_device="off")
        self.sobot.start_teleoperator(robot_name=robot_name,cam_device="0",frame_rate=10,show_video="on",show_stickman="on")

        if self.general_info["timeout"].isnumeric():
            self.timeout=int(self.general_info["timeout"])
        else:
            self.timeout=default_timeout

        print (" ... done")

    def run(self) :

        self.sobot.speak(self.general_info["welcome"])
        self.sobot.teleoperate(blocking=False)
        time.sleep(self.timeout)
        self.sobot.stop_teleoperation()
        self.sobot.speak(self.general_info["farewell"])
        time.sleep(3)

    def terminate(self):
        self.sobot.terminate()

def handler(signal_received, frame):
    # Handle cleanup here
    print('SIGINT or CTRL-C detected. Exiting gracefully')
    teleoperator.terminate()
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

    teleoperator = teleoperation(args.robot_name,args.robot_ip,args.language,args.sound_device,args.mosquitto_ip,args.project_file)
    teleoperator.run()
    teleoperator.terminate()