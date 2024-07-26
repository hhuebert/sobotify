class ALProxy():

    def __init__(self, Text, ipAddr, Port):
        print ("ALProxy::ALProxy")
        print ("   module :" + Text)        
        print ("   ipAddr :" + str(ipAddr))        
        print ("   port   :" + str(Port))   

    def systemVersion(self):
        return ("2.8")

    def goToPosture(self, Text, floatVal):
        print ("ALProxy::goToPosture " + Text + " to " + str(floatVal))
        
    def wakeUp(self):
        return True

    def getAngles(self,names,useSensor):
        return [0,0]

    def getData(self,name):
        return 0
    
    def setCollisionProtectionEnabled(self,names,enable):
        return True
    
    def getSubscribers(self):
        return []
    
    def unsubscribe(self,number):
        return True
    
    def getImageRemote(self, id):
        image=[]
        image.append(2)
        image.append(2)
        image.append(1)
        image.append(1)
        image.append(1)
        image.append(1)
        image.append([[0,1],[2,3]])
        
    def subscribeCamera(self, name, device,resolution, color_space, framerate):
        return True

    def setStiffnesses(self, Text, floatVal):
        print ("ALProxy::setStiffnesses of " + Text + " to " + str(floatVal))        

    def setAngles(self, names, angles, floatVal):
        print ("ALProxy::setAngles with speed : " +  str(floatVal)) 
        print ("  names : "+ str(names))
        print ("  angles: "+ str(angles))

    def setLanguage(self, Text):
        print ("ALProxy::setLanguage : " + Text)      

    def setParameter(self, Text, intVal):
        print ("ALProxy::setParameter : "+ Text + "=" + str(intVal))        

    def say(self, Text):
        print ("\nALProxy::say : " + Text)        

