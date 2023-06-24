import paho.mqtt.client as mqtt


class mqttClient(object):

    def __init__(self,mosquitto_ip,client_name):
        self.callback={}
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
        print ("published! - " + str(rc))

    def on_message(self, client, userdata, msg):
        topic = msg.topic
        callback_entry=self.callback.get(topic,self.callback.get("#",None))
        if not callback_entry==None:
            if callback_entry[1]==False:
                message = msg.payload.decode('utf-8')
                print ("received on topic: " + topic + " ====> message: " + message )
            else :
                message = msg.payload
            callback=callback_entry[0]
            if callback_entry[2]==True:
                callback(message,msg.topic)
            else :
                callback(message)

    def on_connect(self, client, userdata, flags, rc):
        print ("Connected! - " + str(rc))
    
    def terminate(self):
        self.client.disconnect()
        self.client.loop_stop()