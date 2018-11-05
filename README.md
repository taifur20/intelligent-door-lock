# Intelligent Door Lock

## What is it?
This an intelligent door lock which can recognize a guest when he comes to the door step and press the bell button, greets the guest with his/her name, notify the owner about the guest and remember an unknown guest. House owner can know the name of the guest by asking Alexa like "Alexa, who is at the front door?" You can also ask Alexa to open or close the door without interrupting your work. I made a custom Alexa Skill for this. Using the skill you can know your guest and welcome him/her inside your house without leaving your seat.

## Hardware used in this project
1. Raspberry Pi & Raspberry Pi Camera Module
2. Arduino UNO
3. Amazon Alexa
4. Tactile Button
5. Door Lock (3D Printed for demo purpose)
6. Speaker
7. Audio Amplifier

## Software & Web services used in this project
1. Amazon Alexa Alexa Skills Kit
2. Amazon Web Services AWS DynamoDB
3. Amazon Web Services AWS S3
4. Amazon Web Services AWS IAM
5. Amazon Web Services AWS SNS
6. Amazon Web Services Amazon Rekognition
7. Amazon Web Services Amazon Polly
8. Amazon Web Services AWS Lambda
9. Amazon Web Services AWS IoT
10. Amazon Web Services AWS SDK
11. Arduino IDE

## How it works?

When a guest comes to your door and press the calling button, it performs three tasks:

1. It takes a picture of the guest and upload it to AWS S3 Bucket and S3 Bucket trigger a SNS notification.
2. It sends an email with the photo to the house owner.
3. It sends a greeting text to AWS Polly and then play the audio greeting for the guest returned by the Polly.

After getting the notification from AWS SNS or getting the email, house owner can ask Alexa to introduce the guest by invoking a custom Alexa skill "Door Guard" and saying:

Alexa, ask door guard who is at the front door? or

Alexa, ask door guard who came?

Alexa triggers a Lambda function and Lambda function does the following jobs:

1. Read the image uploaded to the S3 Bucket.
2. Sends a face search request for the image to AWS Rekognition.
3. After getting face matches result return by Rekognition, Lambda search for the name to AWS DynamoDB and return the name to the Alexa if found.
4. Alexa provides the name to the house owner and house owner can again call the Alexa to open the door for the guest.
5. In this case Lambda sends a open door command to AWS IoT to a specific MQTT topic. 
6. Raspberry Pi receives this MQTT command and sends to Arduino using serial port. Arduino opens or close the lock accordingly. The following block diagram can helps for better understanding.

## Instructions

### Setting up the Raspberry Pi
1. Install python serial module using the command: `sudo apt-get install python-serial`
2. Install AWS IoT SDK using following command: `sudo pip install AWSIoTPythonSDK`
3. Install the Boto3 library using the following command: `sudo pip install boto3`

### Installing & Configuring AWS CLI
1. Install the AWS CLI (in your PC or Raspberry Pi) with the following command: `pip install awscli --upgrade --user`
You need to configure AWS CLI with Access Key ID, Secret Access Key, AWS Region Name and Command Output format before getting started with it. Follow [this tutorial](https://iotbytes.wordpress.com/aws-iot-cli-on-raspberry-pi/) for completing the whole process.

### Setting up Amazon S3 Bucket, Amazon Rekognition and Amazon DynamoDB
1. Create a face collection to Amazon Rekognition using the command from CLI: `aws rekognition create-collection --collection-id guest_collection --region eu-west-1`
2. Create an Amazon DynamoDB table from AWS CLI using the command: `aws dynamodb create-table --table-name guest_collection \
--attribute-definitions AttributeName=RekognitionId,AttributeType=S \
--key-schema AttributeName=RekognitionId,KeyType=HASH \
--provisioned-throughput ReadCapacityUnits=1,WriteCapacityUnits=1 \
--region eu-west-1`
3. For the IndexFaces operation, you can provide the images as bytes or make them available to Amazon Rekognition inside an Amazon S3 bucket. Upload the images (images of the known guests) to an Amazon S3 bucket using AWS Management Console. To do that you need to creatre a s3 bucket. Use the following command from AWS CLI: `aws s3 mb s3://guest-images --region eu-west-1`

Although all the preparation steps were performed from the AWS CLI, you need to create an IAM role that grants your function the rights to access the objects from Amazon S3, initiate the IndexFaces function of Amazon Rekognition, and create multiple entries within your Amazon DynamoDB key-value store for a mapping between the FaceId and the person’s full name.

4. To get the access use the following json code and save as *access-policy.json*
```
{ 
    "Version": "2012-10-17", 
    "Statement": [ 
        {
             "Effect": "Allow",
             "Action": [ 
                "logs:CreateLogGroup", 
                "logs:CreateLogStream", 
                "logs:PutLogEvents" 
                ], 
                "Resource": "arn:aws:logs:*:*:*"
         }, 
         {
             "Effect": "Allow", 
             "Action": [ 
                "s3:GetObject"
                 ], 
                "Resource": [
                     "arn:aws:s3:::bucket-name/*" 
                      ]
          }, 
          { 
            "Effect": "Allow", 
            "Action": [
                 "dynamodb:PutItem" 
            ], 
            "Resource": [ 
                "arn:aws:dynamodb:aws-region:account-id:table/family_collection"
            ] 
          }, 
          { 
            "Effect": "Allow", 
            "Action": [ 
                "rekognition:IndexFaces"
             ],
            "Resource": "*"
                 }
             ]
        }
```
For the access policy, ensure you replace aws-region, account-id, and the actual name of the resources (e.g., bucket-name and family_collection) with the name of the resources in your environment.

5. Now, attach the access policy to the role using following command:`aws iam put-role-policy --role-name LambdaRekognitionRole --policy-name \ LambdaPermissions --policy-document file://access-policy.json`

6. Now, run the following python code to upload the images into S3 Bucket. Before running the code be sure that you keep all the images and the python file in the same directory. (or use the code file named *upload-multiple-image-with-name.py*)
```
import boto3
s3 = boto3.resource('s3')
# Get list of objects for indexing
images=[('afridi.jpg','Shahid Afridi'),
       ('sakib.jpg','Sakib Al Hasan'),
       ('kohli.jpg','Birat Kohli'),
       ('masrafi.jpg','Mashrafe Bin Mortaza'),
       ('ganguli.jpg','Sourav Ganguly')
      ]
# Iterate through list to upload objects to S3   
for image in images:
   file = open(image[0],'rb')
   object = s3.Object('taifur12345bucket',image[0])
   ret = object.put(Body=file,
                   Metadata={'FullName':image[1]}
                   )
   #print(image[0])
   #print(image[1])
```
7. Now, add the Face Index to AWS DynamoDB with full name for every image using the following python code. (or use the code file named as *index-face-and-store-db.py*)
```
import boto3
from decimal import Decimal
import json
import urllib
BUCKET = "taifur12345bucket"
KEY = "sample.jpg"
IMAGE_ID = KEY  # S3 key as ImageId
COLLECTION = "family_collection"
dynamodb = boto3.client('dynamodb', "eu-west-1")
s3 = boto3.client('s3')
# Note: you have to create the collection first!
# rekognition.create_collection(CollectionId=COLLECTION)
def update_index(tableName,faceId, fullName):
	response = dynamodb.put_item(
	TableName=tableName,
	Item={
		'RekognitionId': {'S': faceId},
		'FullName': {'S': fullName}
		}
	)
	#print(response)
def index_faces(bucket, key, collection_id, image_id=None, attributes=(), region="eu-west-1"):
	rekognition = boto3.client("rekognition", region)
	response = rekognition.index_faces(
		Image={
			"S3Object": {
				"Bucket": bucket,
				"Name": key,
			}
		},
		CollectionId=collection_id,
		ExternalImageId="taifur",
	    DetectionAttributes=attributes,
	)
	if response['ResponseMetadata']['HTTPStatusCode'] == 200:
		faceId = response['FaceRecords'][0]['Face']['FaceId']
		print(faceId)
		ret = s3.head_object(Bucket=bucket,Key=key)
		personFullName = ret['Metadata']['fullname']
		#print(ret)
		print(personFullName)
		update_index('taifur12345table',faceId,personFullName)
	  # Print response to console.
	  #print(response)
	  return response['FaceRecords']
for record in index_faces(BUCKET, KEY, COLLECTION, IMAGE_ID):
	face = record['Face']
	# details = record['FaceDetail']
	print "Face ({}%)".format(face['Confidence'])
	print "  FaceId: {}".format(face['FaceId'])
	print "  ImageId: {}".format(face['ImageId'])
```
  ### Creating Custom Alexa Skill
  Create a custom Alexa Skill using following JSON code (or use *alex_skill.json* file). If your never create a custom Alexa skill before you can follow this nice tutorial: [How To Build A Custom Amazon Alexa Skill](https://medium.com/crowdbotics/how-to-build-a-custom-amazon-alexa-skill-step-by-step-my-favorite-chess-player-dcc0edae53fb). You can also follow my tutorial from hackster.
  
  ```
  {
    "languageModel": {
        "invocationName": "door guard",
        "intents": [
            {
                "name": "AddGuestIntent",
                "slots": [],
                "samples": [
                    "Add guest in your memory",
                    "Add person in your memory",
                    "Add the person in your memory",
                    "Add the guest to your memory",
                    "Remember the man",
                    "Remember the guy",
                    "Remember the person",
                    "Remember the guest",
                    "Remember him",
                    "Remember her",
                    "Save the guest",
                    "Save the person",
                    "Save the guy",
                    "Remember",
                    "Save"
                ]
            },
            {
                "name": "AMAZON.CancelIntent",
                "slots": [],
                "samples": []
            },
            {
                "name": "AMAZON.HelpIntent",
                "slots": [],
                "samples": []
            },
            {
                "name": "AMAZON.StopIntent",
                "slots": [],
                "samples": []
            },
            {
                "name": "CheckDoorIntent",
                "slots": [],
                "samples": [
                    "Is the door unlocked",
                    "Is the door locked",
                    "Check door lock",
                    "Check door ",
                    "Is the door closed",
                    "What is the door condition",
                    "Is my door open",
                    "Check my door",
                    "Is the door open",
                    "Check the door",
                    "Is the door open or closed"
                ]
            },
            {
                "name": "CloseDoorIntent",
                "slots": [],
                "samples": [
                    "Lock door",
                    "Close door ",
                    "Lock the door ",
                    "Close the door ",
                    "Close my door",
                    "Make the door lock",
                    "Make the door close",
                    "Lock"
                ]
            },
            {
                "name": "DescribeGuestIntent",
                "slots": [],
                "samples": [
                    "Tell some details about the man",
                    "Tell some details about the guy",
                    "Give some details about the man",
                    "Give some details about the guy",
                    "Give some details about the person",
                    "Tell some details about the person",
                    "Tell some details about the guest",
                    "Give some details about the guest",
                    "Introduce the person",
                    "Introduce the guest",
                    "Give some details",
                    "Give details",
                    "Explain him",
                    "Explain her",
                    "How is he",
                    "How is she",
                    "How he look",
                    "How she looks"
                ]
            },
            {
                "name": "GiveAccessIntent",
                "slots": [],
                "samples": [
                    "Let the guest come",
                    "Let her come",
                    "Let him come",
                    "Allow her",
                    "Allow him",
                    "Let the guy enter",
                    "Let the person enter",
                    "Let the guest enter",
                    "Allow the guy",
                    "Allow the person",
                    "Allow the guest",
                    "Open the door",
                    "Open",
                    "Allow",
                    "Open the lock",
                    "Open lock",
                    "Let him enter",
                    "Let her enter"
                ]
            },
            {
                "name": "IdentifyGuestIntent",
                "slots": [],
                "samples": [
                    "Who want to meet",
                    "Who came",
                    "Who is waiting ",
                    "Who is at the front door",
                    "Who",
                    "Who is he",
                    "Who is she",
                    "Who is outside"
                ]
            }
        ],
        "types": []
    }
}
```

### Creating Lambda Function
1. Create a Lambda Function using *LambdaRekognitionRole* we created using aws cli.
2. Download the code file for Lambda function (*lambda-function.py*) from above and replace the skill id with your own. Download AWSIoTPythonSDK from the github and make a .zip folder including all (lambda code, certificate file, private key file, root ca file and SDK moudle directory. For reference see *module.zip* file).
3. Go to the Lambda function again from AWS console and from the code section choose Upload a ZIP file, browse the zip file you created and then click on Save.

If you need some guidance about creating AWS Lambda function follow the tutorial [AWS Lambda Functions Made Easy](https://codeburst.io/aws-lambda-functions-made-easy-1fae0feeab27).

### Creating a thing on AWS IoT
For receiving MQTT message to Raspberry Pi form AWS you need to setup AWS IoT for MQTT. To get help on configuring AWS IoT you may follow this tutorial [AWS IoT: Creating your first cloud-bound device](https://medium.com/tensoriot/aws-iot-creating-your-first-cloud-bound-device-d8dca0695f43).

### You have completed the work for AWS Cloud! 

### Code for Raspberry Pi
1. Transfer the file *capture-button-upload-email.py* to your Raspberry Pi. This Python program takes an image when a guest press the bell button, uploads the image to S3 bucket and emails the image to the specific address set to the code.
2. Transfer the file *aws-iot-receive.py* to your Raspberry Pi. This file receives the MQTT message from AWS IoT server, open the door and greets the guest by his/her name with the help of Amazon Polly. It also sends the command to the Arduino board using serial port.
3. Upload the program *arduino-door-guard.ino* to the Arduino board. This program is used to open or close the lock according to the command received from Raspberry pi using serial port.

### Run the Python program *capture-button-upload-email.py* and *aws-iot-receive.py* from the Raspberry Pi.
### Congratulation! You Intelligent Door Lock is Completely Ready to Operate!!
