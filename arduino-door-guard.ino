#include <Servo.h>

String inputString = "";         // a string to hold incoming data
boolean stringComplete = false;  // whether the string is complete

//servo motor is used to control the lock
Servo myservo;  // create servo object to control a servo

void setup() {
  // initialize serial:
  Serial.begin(9600);

  inputString.reserve(200);
  myservo.attach(9);  // attaches the servo on pin 9 to the servo object
}

void loop() {
  
  if (stringComplete) {
    //lcd.clear();
    //lcd.print(inputString);
    if(inputString == "open"){
        openDoor();
        delay(20);
      }
    else if(inputString == "close"){
        closeDoor();
        delay(20);
      }  
    // clear the string:
    inputString = "";
    stringComplete = false;
  }
}

/*
  SerialEvent occurs whenever a new data comes in the
 hardware serial RX.  This routine is run between each
 time loop() runs, so using delay inside loop can delay
 response.  Multiple bytes of data may be available.
 */

void serialEvent() {
  while (Serial.available()) {    
    // get the new byte:
    char inChar = (char)Serial.read();     
    // if the incoming character is a newline, set a flag
    // so the main loop can do something about it:
    if (inChar == '\n') {
      stringComplete = true;
    }
    else
    // add it to the inputString:  
      inputString += inChar;
  }
}

void openDoor(){
  myservo.write(0); //place servo knob at 0 degree
  delay(100);   
}

void closeDoor(){
  myservo.write(65); //place servo knob at 65 degree to fully closed the lock
  delay(100); 
}
