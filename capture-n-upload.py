import time
import picamera

import boto3
s3 = boto3.resource('s3')

import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(4, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

#this function automatically called in button press and can call other two functions
def gpio_callback(self):
	capture_image()
	time.sleep(0.3)
	print('Captured')
	upload_image()
	time.sleep(2)
	
#detect a button press and call gpio_callback function
GPIO.add_event_detect(4, GPIO.FALLING, callback=gpio_callback, bouncetime=2000)


#this function capture an image from pi camera and save it as sample.jpg
def capture_image():
	with picamera.PiCamera() as camera:
		camera.resolution = (640, 480)
		camera.start_preview()
		camera.capture('sample.jpg')
		camera.stop_preview()
		camera.close()
		return
		
				

#this function uploads the sample.jpg to AWS S3 Bucket with a name as Guest
def upload_image():
	file = open('sample.jpg','rb')
	object = s3.Object('taifur12345bucket','sample.jpg')
	ret = object.put(Body=file,
			Metadata={'FullName':'Guest'}
			)
	print(ret)
	return
	
