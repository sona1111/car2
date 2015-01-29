import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BOARD)
  
#GPIO.setup(16, GPIO.OUT)
  
#steer = GPIO.PWM(16, 50) 


  
GPIO.setup(16, GPIO.OUT)


  
motor = GPIO.PWM(16, 100)
motor.start(50.0)

r = raw_input()

GPIO.cleanup()


#time.sleep(10)
