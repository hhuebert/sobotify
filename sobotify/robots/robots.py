#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse
import sys

LIST_OF_ROBOTS=("stickman","pepper","nao","cozmo","mykeepon")

def get_names() :
    return LIST_OF_ROBOTS

def get_vision(name,robot_ip,cam_device) :
        if name=='stickman' or name=='pepper' or name=='pepper_sim' or name=='nao' or name=='nao_sim' or  name=='mykeepon':
            import sobotify.robots.stickman.stickman as stickman
            return stickman.vision(cam_device)
        elif name=='cozmo' :
            import sobotify.robots.cozmo.cozmo as cozmo
            my_cozmo=cozmo.cozmo()
            return my_cozmo
        else :
            print("unknow robot :" + str(name))
            exit()

def get_sound(name,robot_ip,sound_device) :
        if name=='stickman' or name=='pepper' or name=='pepper_sim' or name=='nao' or name=='nao_sim' or  name=='mykeepon' or name=='cozmo':
            import sobotify.robots.stickman.stickman as stickman
            return stickman.sound(sound_device)
        elif name=='pepper' :
            import sobotify.robots.pepper.pepper as pepper
            return pepper.sound(sound_device)
        elif name=='pepper_sim' :
            import sobotify.robots.pepper.pepper_sim as pepper_sim
            return pepper_sim.sound(sound_device)
        elif name=='nao' :
            import sobotify.robots.nao.nao as nao
            return nao.sound(sound_device)
        elif name=='nao_sim' :
            import sobotify.robots.nao.nao_sim as nao_sim
            return nao_sim.sound(sound_device)
        elif name=='cozmo' :
            import sobotify.robots.cozmo.cozmo as cozmo
            my_cozmo=cozmo.cozmo(sound_device)
            return my_cozmo
        elif name=='mykeepon' :
            import sobotify.robots.mykeepon.mykeepon as mykeepon
            return mykeepon.sound(sound_device)
        else :
            print("unknow robot :" + str(name))
            exit()


def get_gesture_conversion(name) :
    if name=='stickman' :
        return None
    elif name=='pepper' :
        import sobotify.robots.pepper.landmarks2angles as landmarks2angles
        return landmarks2angles.landmarks2angles
    elif name=='nao' :
        import sobotify.robots.nao.landmarks2angles as landmarks2angles
        return landmarks2angles.landmarks2angles
    elif name=='cozmo' :
        import sobotify.robots.cozmo.landmarks2angles as landmarks2angles
        return landmarks2angles.landmarks2angles
    elif name=='mykeepon' :
        import sobotify.robots.mykeepon.landmarks2angles as landmarks2angles
        return landmarks2angles.landmarks2angles
    else :
        print("unknow robot :" + str(name))
        return None            
    
def get_all_interfaces(name,robot_ip,robot_options,cam_device,sound_device) :
        parser=argparse.ArgumentParser(description='start an mqtt client for controlling a robot')
        parser.add_argument('--nao',default="",nargs="+",help='nao specific options')
        parser.add_argument('--nao_sim',default="",nargs="+",help='nao simulator specific options')
        parser.add_argument('--pepper',default="",nargs="+",help='pepper specific options')
        parser.add_argument('--pepper_sim',default="",nargs="+",help='pepper simulator specific options')
        parser.add_argument('--cozmo',default="",nargs="+",help='cozmo specific options')
        parser.add_argument('--stickman',default="",nargs="+",help='stickman specific options')
        robot_options_args=parser.parse_args(robot_options.strip('"').split())   

        if name=='stickman' :
            import sobotify.robots.stickman.stickman as stickman
            return stickman.speech(),stickman.motion(),stickman.vision(cam_device),stickman.sound(sound_device)
        elif name=='pepper' :
            if not (sys.version_info[0]==2 and sys.version_info[1]==7) :
                print("Pepper robot can only be used with Python version 2.7.x (your version is " + str(sys.version_info[0])+"."+str(sys.version_info[1])+")")
                exit()
            import sobotify.robots.pepper.pepper as pepper
            return pepper.speech(robot_ip),pepper.motion(robot_ip),pepper.vision(robot_ip,cam_device),pepper.sound(sound_device)
        elif name=='pepper_sim' :
            import sobotify.robots.pepper.pepper_sim as pepper_sim
            return pepper_sim.speech(),pepper_sim.motion(),pepper_sim.vision(cam_device),pepper_sim.sound(sound_device)
        elif name=='nao' :
            if not (sys.version_info[0]==2 and sys.version_info[1]==7) :
                print("Nao robot can only be used with Python version 2.7.x (your version is " + str(sys.version_info[0])+"."+str(sys.version_info[1])+")")
                exit()
            import sobotify.robots.nao.nao as nao
            return nao.speech(robot_ip),nao.motion(robot_ip,robot_options_args.nao),nao.vision(robot_ip,cam_device),nao.sound(sound_device)
        elif name=='nao_sim' :
            import sobotify.robots.nao.nao_sim as nao_sim
            return nao_sim.speech(),nao_sim.motion(),nao_sim.vision(cam_device),nao_sim.sound(sound_device)
        elif name=='cozmo' :
            import sobotify.robots.cozmo.cozmo as cozmo
            my_cozmo=cozmo.cozmo(sound_device)
            return my_cozmo,my_cozmo,my_cozmo,my_cozmo
        elif name=='mykeepon' :
            import sobotify.robots.mykeepon.mykeepon as mykeepon
            return mykeepon.speech(),mykeepon.motion(robot_ip),mykeepon.vision(cam_device),mykeepon.sound(sound_device)
        else :
            print("unknow robot :" + str(name))
            exit()    