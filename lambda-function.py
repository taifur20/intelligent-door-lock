"""
This sample demonstrates a simple skill built with the Amazon Alexa Skills Kit.
The Intent Schema, Custom Slots, and Sample Utterances for this skill, as well
as testing instructions are located at http://amzn.to/1LzFrj6
 
For additional samples, visit the Alexa Skills Kit Getting Started guide at
http://amzn.to/1LGWsLG
"""
 
from __future__ import print_function
import urllib2
import xml.etree.ElementTree as etree
from datetime import datetime as dt

from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
myMQTTClient = AWSIoTMQTTClient("doorLock")
myMQTTClient.configureEndpoint("a3jra11pv5kiyg.iot.eu-west-1.amazonaws.com", 8883)
myMQTTClient.configureCredentials("./rootCA.pem", "./privateKEY.key", "./certificate.crt")

# AWSIoTMQTTClient connection configuration
myMQTTClient.configureAutoReconnectBackoffTime(1, 32, 20)
#myMQTTClient.configureOfflinePublishQueueing(-1)  # Infinite offline Publish queueing
myMQTTClient.configureDrainingFrequency(2)  # Draining: 2 Hz
myMQTTClient.configureConnectDisconnectTimeout(10)  # 10 sec
myMQTTClient.configureMQTTOperationTimeout(5)  # 5 sec

myMQTTClient.connect()
#myMQTTClient.connectAsync()


import boto3
import io
import time

BUCKET = "taifur12345bucket"
KEY = "adnan_1.jpg"
COLLECTION = "family_collection"

door_state = False

rekognition = boto3.client('rekognition', region_name='eu-west-1')
dynamodb = boto3.client('dynamodb', region_name='eu-west-1')

def lambda_handler(event, context):
    """ Route the incoming request based on type (LaunchRequest, IntentRequest,
    etc.) The JSON body of the request is provided in the event parameter.
    """
    print("event.session.application.applicationId=" +
          event['session']['application']['applicationId'])
          
    #myMQTTClient.connect()
 
    """
    Uncomment this if statement and populate with your skill's application ID to
    prevent someone else from configuring a skill that sends requests to this
    function.
    """
    # if (event['session']['application']['applicationId'] !=
    #         "amzn1.echo-sdk-ams.app.[unique-value-here]"):
    #     raise ValueError("Invalid Application ID")
 
    if event['session']['new']:
        on_session_started({'requestId': event['request']['requestId']},
                           event['session'])
 
    if event['request']['type'] == "LaunchRequest":
        return on_launch(event['request'], event['session'])
    elif event['request']['type'] == "IntentRequest":
        return on_intent(event['request'], event['session'])
    elif event['request']['type'] == "SessionEndedRequest":
        return on_session_ended(event['request'], event['session'])
 
 
def on_session_started(session_started_request, session):
    """ Called when the session starts """
 
    print("on_session_started requestId=" + session_started_request['requestId']
          + ", sessionId=" + session['sessionId'])
 
 
def on_launch(launch_request, session):
    """ Called when the user launches the skill without specifying what they
    want
    """
 
    print("on_launch requestId=" + launch_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # Dispatch to your skill's launch
    return get_welcome_response()
 
 
def on_intent(intent_request, session):
    """ Called when the user specifies an intent for this skill """
 
    print("on_intent requestId=" + intent_request['requestId'] +
          ", sessionId=" + session['sessionId'])
 
    intent = intent_request['intent']
    intent_name = intent_request['intent']['name']
 
    # Dispatch to your skill's intent handlers
    if intent_name == "IdentifyGuestIntent":
        return guest_search(intent, session)
    elif intent_name == "GiveAccessIntent":
        return give_access(intent, session)
    elif intent_name == "CloseDoorIntent":
        return close_door(intent, session)
    elif intent_name == "CheckDoorIntent":
        return check_door(intent, session)
    elif intent_name == "DescribeGuestIntent":
        return describe_guest(intent, session)
    elif intent_name == "AddGuestIntent":
        return add_guest(intent, session)
    elif intent_name == "AMAZON.HelpIntent":
        return get_welcome_response()
    elif intent_name == "AMAZON.StopIntent" or intent_name == "AMAZON.CancelIntent":
        return session_end(intent, session)
    else:
        raise ValueError("Invalid intent")

 
def on_session_ended(session_ended_request, session):
    """ Called when the user ends the session.
 
    Is not called when the skill returns should_end_session=true
    """
    print("on_session_ended requestId=" + session_ended_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # add cleanup logic here
 
# --------------- Functions that control the skill's behavior ------------------
 
 
def get_welcome_response():
    """ If we wanted to initialize the session to have some attributes we could
    add those here
    """
 
    session_attributes = {}
    card_title = "Welcome"
    speech_output = "Welcome to the door lock application. " \
                    "You can ask me, who is at the front door or" \
                    " open the door"
    # If the user either does not reply to the welcome message or says something
    # that is not understood, they will be prompted again with this text.
    reprompt_text = "Please ask me for checking the door by telling, " \
                    "Who is at the front door?"
    should_end_session = False
    #myMQTTClient.publish("test/door", "welcome", 0)
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

def give_access(intent, session):
    """ If we wanted to initialize the session to have some attributes we could
    add those here
    """
    #myMQTTClient.publish("test/door", "open", 0)
    myMQTTClient.publishAsync("test/door", "open", 1, ackCallback=None)
    global door_state
    session_attributes = {}
    card_title = "Opening Door"
    speech_output = "The door is now open."
    # If the user either does not reply to the welcome message or says something
    # that is not understood, they will be prompted again with this text.
    reprompt_text = ""
    should_end_session = True
    #myMQTTClient.connectAsync()
    #myMQTTClient.publish("test/door", "open", 0)
    time.sleep(2)
    door_state = True
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))
 
def close_door(intent, session):
    """ If we wanted to initialize the session to have some attributes we could
    add those here
    """
    #myMQTTClient.publish("test/door", "close", 0)
    myMQTTClient.publishAsync("test/door", "close", 1, ackCallback=None)
    global door_state
    session_attributes = {}
    card_title = "Closing Door"
    speech_output = "The door is now closed."
    
    # If the user either does not reply to the welcome message or says something
    # that is not understood, they will be prompted again with this text.
    reprompt_text = ""
    should_end_session = True
    door_state = False
    time.sleep(2)
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def check_door(intent, session):
    """ If we wanted to initialize the session to have some attributes we could
    add those here
    """
    global door_state
    session_attributes = {}
    card_title = "Checking Door"
    if door_state == True:
        speech_output = "The door is open."
    else:
        speech_output = "The door is closed."
    # If the user either does not reply to the welcome message or says something
    # that is not understood, they will be prompted again with this text.
    reprompt_text = ""
    should_end_session = True
    #myMQTTClient.publish("test/door", "open", 0)
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))
        
def describe_guest(intent, session):
    """ If we wanted to initialize the session to have some attributes we could
    add those here
    """
    session_attributes = {}
    card_title = "Guest Details"
    speech_output = "The guest is waiting with smiling face."
    
    # If the user either does not reply to the welcome message or says something
    # that is not understood, they will be prompted again with this text.
    reprompt_text = ""
    should_end_session = True
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))
        
def add_guest(intent, session):
    """ If we wanted to initialize the session to have some attributes we could
    add those here
    """
    session_attributes = {}
    card_title = "Adding Guest"
    speech_output = "The guest's details is stored for next time."
    
    # If the user either does not reply to the welcome message or says something
    # that is not understood, they will be prompted again with this text.
    reprompt_text = ""
    should_end_session = True
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))
 
		
def guest_search(intent, session):
    
    card_title = "Guest's Identity"
    session_attributes = {}
    should_end_session = True
    speech_output = "I dont know the person."
    reprompt_text = ""
    response = rekognition.search_faces_by_image(
            CollectionId='family_collection',
            Image={ 
				"S3Object": {
					"Bucket": BUCKET,
					"Name": KEY,
				}
			},                                    
			)
	#print(response)    
    for match in response['FaceMatches']:
        print (match['Face']['FaceId'],match['Face']['Confidence'])
			
        face = dynamodb.get_item(
			TableName='taifur12345table',  
			Key={'RekognitionId': {'S': match['Face']['FaceId']}}
			)
		
        if 'Item' in face:
            guest = face['Item']['FullName']['S']
            speech_output = guest + " is waiting at the door."
	        #print (face['Item']['FullName']['S'])
            #guest = face['Item']['FullName']['S']
            #speech_output = " is waiting at the door." 
            reprompt_text = ""
            break
        else:
            print ('no match found in person lookup')

			
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def session_end(intent, session):
    """ If we wanted to initialize the session to have some attributes we could
    add those here
    """
    session_attributes = {}
    card_title = "End"
    speech_output = "Thank you for calling me. Have a nice day!"
    
    # If the user either does not reply to the welcome message or says something
    # that is not understood, they will be prompted again with this text.
    reprompt_text = ""
    should_end_session = True
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))        
 
# --------------- Helpers that build all of the responses ----------------------
 
 
def build_speechlet_response(title, output, reprompt_text, should_end_session):
    return {
        'outputSpeech': {
            'type': 'PlainText',
            'text': output
        },
        'card': {
            'type': 'Simple',
            'title': title,
            'content': output
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': reprompt_text
            }
        },
        'shouldEndSession': should_end_session
    }
 
 
def build_response(session_attributes, speechlet_response):
    return {
        'version': '1.0',
        'sessionAttributes': session_attributes,
        'response': speechlet_response
    }