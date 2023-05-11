import paho.mqtt.client as mqtt


class mqttClient(object):

    def __init__(self,mosquitto_ip,client_name):
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

    def subscribe(self,subscibe_topic,subscibe_callback) :
        self.client.subscribe(subscibe_topic)
        self.message_callback=subscibe_callback

    def publish(self,subscibe_topic,message) :
        self.client.publish(subscibe_topic,message)

    def on_publish(self, client, userdata, rc):
        print ("published! - " + str(rc))

    def on_message(self, client, userdata, msg):
        message = msg.payload.decode('utf-8')
        print ("received message:", message)
        self.message_callback(message)

    def on_connect(self, client, userdata, flags, rc):
        print ("Connected! - " + str(rc))
    
    def terminate(self):
        self.client.disconnect()
        self.client.loop_stop()