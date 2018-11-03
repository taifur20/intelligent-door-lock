import time
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
myMQTTClient = AWSIoTMQTTClient("doorLock")
myMQTTClient.configureEndpoint("a3jra11pv5kiyg.iot.eu-west-1.amazonaws.com", 8883)
myMQTTClient.configureCredentials("./rootCA.pem", "./privateKEY.key", "./certificate.crt")

import serial
ser = serial.Serial('/dev/ttyACM0',9600)
guest_name = None

import boto3
from contextlib import closing


import os

client = boto3.client('polly', 'eu-west-1')
	
# trigger when receive mqtt message and sent the message to arduno
def customOnMessage(message):
    global guest_name
    print("Received a new message: ")
    msg = message.payload
    ser.write(msg)
    ser.write('\n')
    if msg == 'open' and guest_name != None:
        play_gretting()
        guest_name = None 
    if msg.find('#') + 1:
        msg = msg.translate(None, '#')
        guest_name = msg
        print('removed #')		
    print(msg)
    print(guest_name)
	
# Suback callback
def customSubackCallback(mid, data):
    print("Received SUBACK packet id: ")
    print(mid)
    print("Granted QoS: ")
    print(data)
    print("++++++++++++++\n\n")

# AWSIoTMQTTClient connection configuration
myMQTTClient.configureAutoReconnectBackoffTime(1, 32, 20)
myMQTTClient.configureDrainingFrequency(2)  # Draining: 2 Hz
myMQTTClient.configureConnectDisconnectTimeout(10)  # 10 sec
myMQTTClient.configureMQTTOperationTimeout(5)  # 5 sec
myMQTTClient.onMessage = customOnMessage

myMQTTClient.connect()
myMQTTClient.subscribeAsync("test/door", 1, ackCallback=customSubackCallback)

def play_gretting():
    global guest_name
    response = client.synthesize_speech(
	    OutputFormat='mp3',
	    Text=  'Welcome ' + guest_name + '. The door is open for you.',
            #Text=  'Welcome. The door is open for you.',
	    TextType='text',
	    VoiceId='Emma'
        )
    guest_name = None
    #print response
    if "AudioStream" in response:
        with closing(response["AudioStream"]) as stream:
            output = "welcome.mp3"

            try:
			    # Open a file for writing the output as a binary stream
                with open(output, "wb") as file:
                    file.write(stream.read())
            except IOError as error:
                # Could not write to file, exit gracefully
                print(error)
                sys.exit(-1)
        os.system('omxplayer welcome.mp3')
        print('played')

while True:
	time.sleep(0.1)

