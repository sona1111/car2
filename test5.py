import RPi.GPIO as GPIO
import time


GPIO.setmode(GPIO.BOARD)
  
#GPIO.setup(16, GPIO.OUT)
  
#steer = GPIO.PWM(16, 50) 


  
GPIO.setup(26, GPIO.OUT)
  
motor = GPIO.PWM(26, 50)
motor.start(100)


try:
	while True:
		
		
		#0.47 full stop
		
		#steer.start(50)
		
		i = raw_input('> ')
		#p=(float(i)*100.0)/3.3
		#while True:
		
		
			
			
			#if type(D) == float:
			#	if D <= 100:
			#		break
			
		#print p
		motor.ChangeDutyCycle(float(i))
		motor.ChangeFrequency(float(100))
			#steer.ChangeDutyCycle(float(i))
			#steer.ChangeFrequency(float(100))
			
			
	#	time.sleep(30)
		#motor.stop()
		#steer.stop()
		

except KeyboardInterrupt:
    pass
#motor.stop()
#steer.stop()
GPIO.cleanup()

  
#p.start(50)             
#p.ChangeDutyCycle(90)   
#p.ChangeFrequency(100)  
#p.stop() 



class motorDriver(object):

	def __init__(self):
		pass
		             
  

