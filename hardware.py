import time
import RPi.GPIO as GPIO

#Defining Costants
Pins = {'P0':(11,17),'P1':(12,18),'P2':(13,21),'P3':(15,22),'P4':(16,23),'P5':(18,24),'P6':(22,25),'P7':(7,4),
'CE1':(26,0),'CE0':(24,0),'SCLK':(23,0),'MISO':(21,0),'MOSI':(19,0),'RDX':(10,0),'TDX':(8,0),'SCL':(5,0),'SDA':(3,0)}
GPIO.setmode(GPIO.BCM)




class Sensors(object):
    
    def __init__(self,pinOut,PinIn):
        #saves the values of the pins and other constants
        self.pinOut = pinOut
        self.pinIn = pinIn
        decPulseTrigger = 0.0001 
                
        #set the values of the pins on the PI
        GPIO.setup(self.pinOut,GPIO.OUT)
        GPIO.setup(self.pinIn,GPIO.IN)
        GPIO.output(self.pinOut, GPIO.LOW)
        time.sleep(0.3)
        
        
    def Sens(self):
    	self.reading = GPIO.setup(PinIn,GPIO.IN)
    
    
    
    
    def printReport(self):
        for name, data in self.externalSns.iteritems():
            print name + " " + str(data)
        for name, data in self.internalSns.iteritems():
            print name + " " + str(data)
            
        
class Dynamics(object):
    
    def __init__(self):
        pass
#        self.mSteering = {'status':gpio3, 'angle':45.7}
#        self.mMotor = {'status':gpio4,'speed':100}
        
    def printReport(self):
        for name, data in self.mSteering.iteritems():
            print name + " " + str(data)
        for name, data in self.mMotor.iteritems():
            print name + " " + str(data)
