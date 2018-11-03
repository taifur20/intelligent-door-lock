
import paho.mqtt.client as mqtt
import RPi.GPIO as GPIO
import serial

ser = serial.Serial('/dev/ttyACM0',9600)



received_message = ""

# Define event callbacks
def on_connect(client, userdata, flags, rc):
    print("rc: " + str(rc))

def on_message(client, obj, msg):
    received_message = str(msg.payload)
    print(msg.topic + " " + str(msg.qos) + " " + received_message)
    ser.write(received_message)
    ser.write('\n')
	#received_message = str(msg.payload)
	#GPIO.output(led_pin,GPIO.HIGH)
	#GPIO.output(led_pin,GPIO.LOW)

def on_publish(client, obj, mid):
    print("mid: " + str(mid))

def on_subscribe(client, obj, mid, granted_qos):
    print("Subscribed: " + str(mid) + " " + str(granted_qos))

def on_log(client, obj, level, string):
    print(string)


client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.on_publish = on_publish
client.on_subscribe = on_subscribe

#client.username_pw_set("cnpemclt", "ccZRVtdCTqID")
client.connect("iot.eclipse.org", "1883")

#client.connect("m12.cloudmqtt.com", 15708, 60)

# Start subscribe, with QoS level 0
client.subscribe("test/door", 0)

# Publish a message
#client.publish("taifur", "my message")

#client.loop_forever()
rc = 0
while rc == 0:
    rc = client.loop()
print("rc: " + str(rc))


