import paho.mqtt.client as mqtt
import time 

class mqttClient(object):

    def __init__(self,mosquitto_ip,client_name,debug=False):
        self.callback={}
        self.debug=debug
        self.message=""
        self.message_available=False
        self.get_message_topic=""
        self.get_message_raw_data=False
        self.client = mqtt.Client(client_name, clean_session = False)
        self.broker = mosquitto_ip       
        self.client.on_connect = self.on_connect
        self.client.on_publish = self.on_publish
        self.client.on_message = self.on_message
        try:
            self.client.connect(self.broker, 1883)
        except:
            print('cannot connect to mqtt server at ip address: ',str(mosquitto_ip))
            print('start mqtt server(e.g. mosquitto) or check ip address')
            exit()
        self.client.loop_start()

    def subscribe(self,topic,callback,raw_data=False,receive_topic=False) :
        self.client.subscribe(topic)
        self.callback[topic]=[callback,raw_data,receive_topic]

    def publish(self,subscibe_topic,message="") :
        self.client.publish(subscibe_topic,message)

    def on_publish(self, client, userdata, rc):
        if self.debug : print ("published! - " + str(rc))

    def on_message(self, client, userdata, msg):
        topic = msg.topic
        callback_entry=self.callback.get(topic,self.callback.get("#",None))
        if not callback_entry==None:
            if callback_entry[1]==False:
                message = msg.payload.decode('utf-8')
                if self.debug : print ("received on topic: " + topic + " ====> message: " + message )
            else :
                message = msg.payload
            callback=callback_entry[0]
            if callback_entry[2]==True:
                callback(message,msg.topic)
            else :
                callback(message)
        if self.get_message_topic==topic:
            if self.get_message_raw_data==False:
                message = msg.payload.decode('utf-8')
                if self.debug : print ("received on topic: " + topic + " ====> message: " + message )
            else :
                message = msg.payload
            self.message=message
            self.message_available=True

    def get_message(self,topic,raw_data=False):
        ########################
        # warning: this method might not be thread safe => maybe use separate objects to fix
        ########################
        self.get_message_raw_data=raw_data
        self.client.subscribe(topic)
        self.get_message_topic=topic
        while not self.message_available:
            time.sleep(0.01)    
        #print("get_message: "+ self.message)
        self.message_available=False
        self.get_message_topic=""
        return self.message

    def wait_for(self,topic):
        self.get_message(topic)

    def on_connect(self, client, userdata, flags, rc):
        if self.debug : print ("Connected! - " + str(rc))
    
    def terminate(self):
        self.client.disconnect()
        self.client.loop_stop()