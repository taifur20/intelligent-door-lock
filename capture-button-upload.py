
import time
import picamera

import boto3

s3 = boto3.resource('s3')

import RPi.GPIO as GPIO

import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from email.MIMEBase import MIMEBase
from email import encoders


GPIO.setmode(GPIO.BCM)
GPIO.setup(4, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)


def gpio_callback(self):
	capture_image()
	time.sleep(0.3)
	print('Captured')
	upload_image()
	time.sleep(2)
	send_email()
	

GPIO.add_event_detect(4, GPIO.FALLING, callback=gpio_callback, bouncetime=3000)


def capture_image():
	with picamera.PiCamera() as camera:
		camera.resolution = (640, 480)
		camera.start_preview()
		camera.capture('sample.jpg')
		camera.stop_preview()
		camera.close()
		return
		
				
def upload_image():
	file = open('sample.jpg','rb')
	object = s3.Object('taifur12345bucket','sample.jpg')
	ret = object.put(Body=file,
			Metadata={'FullName':'Guest'}
			)
	print(ret)
	return


def send_email(): 
    fromaddr = "Put From Which Email"
    toaddr = "put to which email"
     
    msg = MIMEMultipart()
     
    msg['From'] = fromaddr
    msg['To'] = toaddr
    msg['Subject'] = "New Guest"
     
    body = "A new guest is waiting at your front door. Photo of the guest is attached."
     
    msg.attach(MIMEText(body, 'plain'))
     
    filename = "sample.jpg"
    attachment = open("/home/pi/sample.jpg", "rb")
     
    part = MIMEBase('application', 'octet-stream')
    part.set_payload((attachment).read())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', "attachment; filename= %s" % filename)
     
    msg.attach(part)
     
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(fromaddr, "password of your email")
    text = msg.as_string()
    server.sendmail(fromaddr, toaddr, text)
    server.quit()
	
