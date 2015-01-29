import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BOARD)
Pins = {'P0':(11,17),'P1':(12,18),'P2':(13,21),'P3':(15,22),'P4':(16,23),'P5':(18,24),'P6':(22,25),'P7':(7,4),
'CE1':(26,0),'CE0':(24,0),'SCLK':(23,0),'MISO':(21,0),'MOSI':(19,0),'RDX':(10,0),'TDX':(8,0),'SCL':(5,0),'SDA':(3,0)}

GPIO.setup(Pins['P0'][0] ,GPIO.OUT)
GPIO.setup(Pins['P1'][0] ,GPIO.OUT)
GPIO.setup(Pins['P2'][0] ,GPIO.OUT)
GPIO.setup(Pins['P3'][0] ,GPIO.OUT)
GPIO.setup(Pins['SCLK'][0] ,GPIO.OUT)


pwm4 = GPIO.PWM(Pins['P3'][0], 100)
pwm5 = GPIO.PWM(Pins['SCLK'][0], 100)



while True:
    
    print "Enter new values in the form t,t,t or f,f,f. e.x. t,f,t"
    values = raw_input("> ")   
    pwm4.stop() 
    if values == 'q':
        break
    
    values = values.split(',')
    #values = map(lambda x: True if x == 't' else False, values)
    values[0:3] = map(lambda x: True if x == 't' else False, values[0:3])
    
    pwm4.start(float(values[3]))
    pwm5.start(float(values[4]))
    
    #if len(values) == 4:
    if len(values) == 5:
        
        GPIO.output(Pins['P0'][0], GPIO.OUT)
        GPIO.output(Pins['P1'][0], GPIO.OUT)
        GPIO.output(Pins['P2'][0], GPIO.OUT)
        GPIO.output(Pins['P3'][0], GPIO.OUT)
	
	if values[0] == True:
	    GPIO.output(Pins['P0'][0], GPIO.HIGH)
	else:
	    GPIO.output(Pins['P0'][0], GPIO.LOW)
	if values[1] == True:
	    GPIO.output(Pins['P1'][0], GPIO.HIGH)
	else:
	    GPIO.output(Pins['P1'][0], GPIO.LOW)
	if values[2] == True:
	    GPIO.output(Pins['P2'][0], GPIO.HIGH)
	else:
	    GPIO.output(Pins['P2'][0], GPIO.LOW)
    
           
        
    else:
        print "Incorrect number of values entered, please try again."

GPIO.cleanup()
pwm4.stop()
pwm5.stop()
