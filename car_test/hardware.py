from carMath import SpeedManager, DistSmoother, AngleManager
import time
import datetime
import RPi.GPIO as GPIO
from threading import Thread
import math


#set GPIO mode
GPIO.setmode(GPIO.BOARD)

#Defining Costants
Pins = {'P0':(11,17),'P1':(12,18),'P2':(13,21),'P3':(15,22),'P4':(16,23),'P5':(18,24),'P6':(22,25),'P7':(7,4),
'CE1':(26,0),'CE0':(24,0),'SCLK':(23,0),'MISO':(21,0),'MOSI':(19,0),'RDX':(10,0),'TDX':(8,0),'SCL':(5,0),'SDA':(3,0)}
#distance from back axle to center of mass, in cm
asub2 = 13.5
asub2sq = 182.25
#distance from front to back axle, in cm
carlen = 32.5
carlensq = 1056.25

#left wheel: right max : 30, left max: 35

#engine values for the specific car(values are in voltage)
PowerEngine = {"forward":0.188,"backwards":0.325,"stop":0.226}

#PowerEngine = {"forward":3.3,"backwards":3.3,"stop":1.5}
SteeringEngine_c = {"left":0.13,"right":0.35,"center":0.208}
#Raspberry Pi Constant voltage out value
RaspberryPiVout = 3.3

class Hardware(object):

    def __init__(self, Type, pinsIn, pinsOut):
        
        #set Pins array
        self.pinsIn = pinsIn
        self.pinsOut = pinsOut
        self.initPins()
        #count amount of Pins
        self.numPinsIn = len(pinsIn)
        self.numPinsOut = len(pinsOut)

        # set specific type of hardware variables 
        if (Type == "pwm"):
            self.frequency = 50         
            self.p = GPIO.PWM(self.pinsOut[0], self.frequency)
        if (Type == "sensor"):  
            pass
            
    #set the values of the pins on the PI
    def initPins(self):
        
        for i in self.pinsIn:
            GPIO.setup(i,GPIO.IN)
    
        for o in self.pinsOut:
            GPIO.setup(o,GPIO.OUT)    
            GPIO.output(o, GPIO.LOW)
            
            
    #sends the desired / required voltage using pulse with modulation
    def pwm(self, voltage):
      
      	
        VPercent = voltage*100/RaspberryPiVout
        
        #print "Voltage " + str(voltage)
        #print "Vpercent " + str(VPercent)
        #self.p.ChangeDutyCycle(VPercent)
    
    	#s = raw_input('> ')
    	self.p.ChangeDutyCycle(VPercent)
    	
    def pwmStop(self):
    	self.p.ChangeDutyCycle(0)

		
		
    	
    	
    	
    
    

class UsonicSens(Hardware):
    
    def __init__(self,pinsIn,pinsOut):        #saves the values of the pins and other constants
    
        super(UsonicSens, self).__init__("sensor",pinsIn, pinsOut)
        
        self.decPulseTrigger = 0.0001 
        self.inttimeout = 2100
        self.lastReading = 0
        self.speed = SpeedManager()
        self.linearDist = DistSmoother(40,20, 10)

        #time.sleep(0.3)
    '''    
    def reading_th(self):
		while True:
			print self.lastReading
			time.sleep(0.7)
     '''   
        
    def sens(self, auto = True):
		
		
		
		
		while True:
		
			t = time.time()

			# Trigger high for 0.0001s then low
			GPIO.output(self.pinsOut[0], True)
			time.sleep(self.decPulseTrigger)
			GPIO.output(self.pinsOut[0], False)

			# Wait for echo to go high (or timeout)
			intcountdown = self.inttimeout

			while (GPIO.input(self.pinsIn[0]) == 0 and intcountdown > 0):
				intcountdown = intcountdown - 1

			# If echo is high
			if intcountdown > 0:

				# Start timer and init timeout countdown
				echostart = time.time()
				intcountdown = self.inttimeout

			# Wait for echo to go low (or timeout)
				while (GPIO.input(self.pinsIn[0]) == 1 and intcountdown > 0):
					intcountdown = intcountdown - 1

				# Stop timer
				echoend = time.time()

				# Echo duration
				echoduration = echoend - echostart


				# Display distance
				if intcountdown > 0:
					intdistance = (echoduration*1000000)/58
					self.lastReading = intdistance
	
			else:
				self.lastReading = -1
				
			
			
			# Wait at least .01s before re trig (or in this case .1s)            
			time.sleep(.1)
			
			#update speed
			#self.speed.updateBySensor(self.lastReading, t)
			#attempt to update reading
			#self.linearDist.updateBySensor(self.lastReading)
			
			if auto == False:
				break
				
				
	
		
    def autoSense(self):
        th = Thread(target = self.sens)
        th.setDaemon(True)
        th.start()


	

    def getReading(self):
        
        return round(self.lastReading,3)
        


        
        
class PowerEngine3(Hardware):
    
    def __init__(self,pinsIn,pinsOut):
        super(PowerEngine3, self).__init__("pwm",pinsIn, pinsOut)
        self.pinsIn = pinsIn
        self.pinsOut = pinsOut
        self.p.start(100)
    	self.pwm(self.convertToVolt(0.0))
    	self.speedPercent = 0.0
    	self.flag = True
    	self.th = Thread(target=self.rotate)
    	self.th.setDaemon(True)
    	self.th.start()


    def rotate(self):
    	
    	while self.flag == True:
		
            time.sleep(0.1)
            print 'test45423'
            print self.speedPercent
            if self.speedPercent == '0':			
                self.pwm(self.convertToVolt(float(self.speedPercent)))
                self.pwmStop()

            else:				
                self.pwm(self.convertToVolt(float(0)))
                time.sleep(0.07)
                self.pwm(self.convertToVolt(float(self.speedPercent)))


				
    def set_rotate(self, command):

#        self.flag = False
#        self.th.join()
        self.speedPercent = command
#        self.th = Thread(target=self.rotate)
#        self.th.setDaemon(True)      
#        self.th.start()        
        
        


    		
            
          
    def convertToVolt(self, value):
        
        if (value >= -100.0 and value < 0.0):                  
            return (((PowerEngine['backwards'] - PowerEngine['stop'])/100)*(-value))+PowerEngine['stop']
        
        elif (value <= 100.0 and value > 0.0):
            return PowerEngine['stop']-(((PowerEngine['stop'] - PowerEngine['forward'])/100)*value)
            
        else:
            return PowerEngine['stop']
            

 

class PowerEngine2(Hardware):
    
    def __init__(self,pinsIn,pinsOut, speedSens):
        super(PowerEngine2, self).__init__("pwm",pinsIn, pinsOut)
        self.pinsIn = pinsIn
        self.pinsOut = pinsOut
        self.p.start(100)
    	self.pwm(self.convertToVolt(0.0))
    	self.speedSens = speedSens
    
    def rotate(self,speedPercent):
    	
    	
		if ((float(speedPercent) > 0.0 and float(self.speedSens.speed.aveSpeed) > 0.0) or (float(speedPercent) < 0.0 and float(self.speedSens.speed.aveSpeed) < 0.0) or float(speedPercent) == 0.0 or float(self.speedSens.speed.aveSpeed) == 0.0):

			if speedPercent == '0':			
				self.pwm(self.convertToVolt(float(speedPercent)))
				self.pwmStop()

			else:
				
				self.pwm(self.convertToVolt(float(0)))
				time.sleep(0.5)
				self.pwm(self.convertToVolt(float(speedPercent)))

		else:
			
			
			
			if (float(speedPercent) < 0.0): 			

				self.pwm(self.convertToVolt(float(-100)))
				self.waitForStop()
				
				self.pwm(self.convertToVolt(float(0)))
				time.sleep(1)
				self.pwm(self.convertToVolt(float(speedPercent)))

			if (float(speedPercent) > 0.0):
				
				self.pwm(self.convertToVolt(float(100)))
				self.waitForStop()
				
				self.pwm(self.convertToVolt(float(0)))
				time.sleep(1)
				self.pwm(self.convertToVolt(float(speedPercent)))


    def waitForStop(self):
    
    	while (self.speedSens.speed.aveSpeed != 0):
			print "stopping"
			time.sleep(0.1)
    		
            
          
    def convertToVolt(self, value):
        
        if (value >= -100.0 and value < 0.0):                  
            return (((PowerEngine['backwards'] - PowerEngine['stop'])/100)*(-value))+PowerEngine['stop']
        
        elif (value <= 100.0 and value > 0.0):
            return PowerEngine['stop']-(((PowerEngine['stop'] - PowerEngine['forward'])/100)*value)
            
        else:
            return PowerEngine['stop']
            
    def alphaStop(self):
    
        pass

class SteeringEngine(Hardware):
    
    
    def __init__(self,pinsIn,pinsOut):
        super(SteeringEngine, self).__init__("pwm",pinsIn, pinsOut) 
        #self.am = AngleManager()
        self.pinsIn = pinsIn
        self.pinsOut = pinsOut
        self.p.start(100)
    	self.pwm(self.convertToVolt(0.0))
    	
    
    def convertToVolt(self, value):

		if (value >= -100.0 and value < 0.0):                  
			return (((SteeringEngine_c['left'] - SteeringEngine_c['center'])/100)*(-value))+SteeringEngine_c['center']

		elif (value <= 100.0 and value > 0.0):
			return SteeringEngine_c['center']-(((SteeringEngine_c['center'] - SteeringEngine_c['right'])/100)*value)
		
		else:
			return SteeringEngine_c['center']
    
    
    def rotate(self,angle):

        self.pwm(self.convertToVolt(-1 * angle))
        #self.am.updateByHardware(angle)        


	

