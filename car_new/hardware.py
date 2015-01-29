from carMath import SpeedManager, DistSmoother, AngleManager
import time
import datetime
import RPi.GPIO as GPIO
from threading import Thread
import math
import timeit
import os
from adafruit.Adafruit_BMP085 import TempSens
from adafruit.Adafruit_LSM303 import Compass, Accelerometer
import logging

clear = lambda: os.system('clear')

#set GPIO mode
GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)

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
#PowerEngine = {"forward":0.188,"backwards":0.325,"stop":0.257}
PowerEngine = {"forward":0.3135,"backwards":0.5775,"stop":0.462}
#PowerEngine = {"forward":0.216,"backwards":0.373,"stop":0.299}
SteeringEngine_c = {"left":0.13,"right":0.35,"center":0.208}
SteeringEngine_dcs = {'left':1.0,'right':25.0,'center':13.0}
#Raspberry Pi Constant voltage out value
RaspberryPiVout = 3.3


'''--------------------------------------------------------------------------------------------------------------------------'''        
'''-----------------------------------------------------Hardware Parent (super) Class---------------------------------------------------'''
'''--------------------------------------------------------------------------------------------------------------------------'''

class Hardware(object):

    def __init__(self, Type, pinsIn, pinsOut):

        #set Pins array
        self.pinsIn = pinsIn
        self.pinsOut = pinsOut
        self.initPins()
        #count amount of Pins
        self.numPinsIn = len(pinsIn)
        self.numPinsOut = len(pinsOut)
        self.logr = logging.getLogger('car.hardware.Hardware')

        # set specific type of hardware variables
        if (Type == "pwm"):
            self.frequency = 100
            self.p = GPIO.PWM(self.pinsOut[0], self.frequency)
        if (Type == "sensor"):
            pass
        if (Type == "engine"):
            self.frequency = 100
            self.pwm1 = GPIO.PWM(self.pinsOut[0], self.frequency)
            self.pwm2 = GPIO.PWM(self.pinsOut[1], self.frequency)
            self.pwm3 = GPIO.PWM(self.pinsOut[2], self.frequency)
            self.pwm4 = GPIO.PWM(self.pinsOut[3], self.frequency)

    #set the values of the pins on the PI
    def initPins(self):

        for i in self.pinsIn:
            GPIO.setup(i,GPIO.IN)

        for o in self.pinsOut:
            GPIO.setup(o,GPIO.OUT)
            GPIO.output(o, GPIO.LOW)


    #sends the desired / required voltage using pulse width modulation
    def pwm(self, voltage):

        if voltage == None:
            pass
        else:
            VPercent = (voltage)*100/RaspberryPiVout

            #print "Voltage " + str(voltage)
            #print "Vpercent " + str(VPercent)
            #self.p.ChangeDutyCycle(VPercent)
            
            #s = raw_input('> ')
            
            self.p.ChangeDutyCycle(voltage)

    def pwmStop(self):
        self.p.ChangeDutyCycle(0)

'''--------------------------------------------------------------------------------------------------------------------------'''        
'''-----------------------------------------------------Power Engine Class-------------------------'''
'''--------------------------------------------------------------------------------------------------------------------------'''
            
class PowerEngine(Hardware):
    
    def __init__(self,pinsIn,pinsOut):
        super(PowerEngine, self).__init__("engine",pinsIn, pinsOut)
        self.pinsIn = pinsIn
        self.pinsOut = pinsOut
        self.pwm1.start(0)
        self.pwm2.start(0)
        self.pwm3.start(0)
        self.pwm4.start(0)
        self.speedLimit = 100.0
    	self.coast()
    	self.logr = logging.getLogger('hardware.PowerEngine')
    	
    def setGlobalSpeedLimit(self, limit):
        self.speedLimit = float(limit)
            	
    def move(self, percent):        
        
        if percent == 0.0:
            self.stop()
            
        elif percent < 0:        
            self.pwm1.ChangeDutyCycle(100.0)
            self.pwm2.ChangeDutyCycle(0.0)
            self.pwm3.ChangeDutyCycle(100.0)
            self.pwm4.ChangeDutyCycle(abs(percent))
            
        else:            
            self.pwm1.ChangeDutyCycle(100.0)
            self.pwm2.ChangeDutyCycle(100.0)
            self.pwm3.ChangeDutyCycle(0.0)
            self.pwm4.ChangeDutyCycle(abs(percent))
            
    def coast(self):
    
        self.pwm1.ChangeDutyCycle(0)
        self.pwm2.ChangeDutyCycle(0)
        self.pwm3.ChangeDutyCycle(0)
        self.pwm4.ChangeDutyCycle(0)
        
    def stop(self):
    
        self.pwm1.ChangeDutyCycle(100.0)
        self.pwm2.ChangeDutyCycle(100.0)
        self.pwm3.ChangeDutyCycle(100.0)
        self.pwm4.ChangeDutyCycle(100.0) #brake power

		
    def convert(self, value):
        return (self.convertToVolt(value))*100.0/RaspberryPiVout
          
    def convertToVolt(self, value):
        
        if (value >= -100.0 and value < 0.0):                  
            return (((PowerEngine['backwards'] - PowerEngine['stop'])/100)*(-value))+PowerEngine['stop']
        
        elif (value <= 100.0 and value > 0.0):
            return PowerEngine['stop']-(((PowerEngine['stop'] - PowerEngine['forward'])/100)*value)
            
        else:
            return PowerEngine['stop']
            

'''--------------------------------------------------------------------------------------------------------------------------'''        
'''-----------------------------------------------------Ultra Sonic Sensors--------------------------------------------------'''
'''--------------------------------------------------------------------------------------------------------------------------'''

class UsonicSens(Hardware):

    def __init__(self, pinsIn, pinsOut, length=4):        #saves the values of the pins and other constants

        super(UsonicSens, self).__init__("sensor",pinsIn, pinsOut)

        self.decPulseTrigger = 0.0001
        self.inttimeout = 2100
        #self.lastReading = 0
        #self.speed = SpeedManager()
        #self.linearDist = DistSmoother(40,20, 10)
        
        self.buffer = [0.0 for x in range(length)]
        self.logr = logging.getLogger('hardware.UsonicSens')

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
                    #time.sleep(0.1)
                    intcountdown = intcountdown - 1

                # Stop timer
                echoend = time.time()

                # Echo duration
                echoduration = echoend - echostart


                # Display distance
                if intcountdown > 0:
                    intdistance = (echoduration*1000000)/58
                    
                    self.buffer.pop(0)
                    self.buffer.append(intdistance)

            else:
                
                self.buffer.pop(0)
                self.buffer.append(500.0)



            # Wait at least .01s before re trig (or in this case .1s)
            time.sleep(0.1)

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
    
        out = 0.0
        for dist in self.buffer:
            out += dist
        return out/(float(len(self.buffer)))


    def getReadingUnbuffered(self):

        return round(self.buffer[-1],3)

'''--------------------------------------------------------------------------------------------------------------------'''
'''-----------------------------------------------------Steering Engine Class------------------------------------------'''
'''--------------------------------------------------------------------------------------------------------------------'''

class SteeringEngine(Hardware):


    def __init__(self,pinsIn,pinsOut):
        super(SteeringEngine, self).__init__("pwm",pinsIn, pinsOut)
        #self.am = AngleManager()
        self.p.start(0)                  #setting the GPIO
        self.threadRunning = False
        self.timeout = 3
        self.turn('center')  #pulsing 0 volts out
        self.currentAngle = 0.0
        # engine thread initiation #
        
        
        self.override = False              # False-override is not needed, True-override is needed 
        self.startECE = True
        #self.ECE_th = Thread(target=self.ECE)
        #self.ECE_th.setDaemon(True)
        #self.ECE_th.start()
        self.logr = logging.getLogger('hardware.SteeringEngine')
        
    
    #command takes a list, the first value is speed percent and the second is direction or brake
    def override(self, command):
        
        self.commandsList = [command]    
        self.override = True
        
    def getAngle(self):
        return self.currentAngle
                
    
    def turnOff_th(self):
        
        self.threadRunning = True
        while self.timeout > 0:
            time.sleep(0.5)
            self.timeout -= 0.5
        self.pwm(0)
        self.threadRunning = False

    def convertToVolt(self, value):
        if (value == None):
            return None
        
        elif (value == 'off'):
            return 0

        elif (value <= 100.0 and value > 0.0):
            value = float(value)
            return (((SteeringEngine_c['left'] - SteeringEngine_c['center'])/100)*(-value))+SteeringEngine_c['center']

        elif (value >= -100.0 and value < 0.0):
            value = float(value)
            return SteeringEngine_c['center']-(((SteeringEngine_c['center'] - SteeringEngine_c['right'])/100)*value)

        else:
            value = float(value)
            return SteeringEngine_c['center']


    def turn(self,direction):
        self.timeout = 3.0
        
        if direction == "left":
            self.currentAngle = -22.0
            self.pwm(SteeringEngine_dcs['left'])            
        elif direction == 'right':
            self.currentAngle = 22.0
            self.pwm(SteeringEngine_dcs['right'])
        elif direction == 'center':
            self.currentAngle = 0.0
            self.pwm(SteeringEngine_dcs['center'])
        else:
            self.logr.warning("invalid turn direction specified")
            return False
        
        if self.threadRunning == False:
            th = Thread(target=self.turnOff_th)
            th.setDaemon(True)
            th.start()
            

        
        
        

        
class Clicker(Hardware):

    def __init__(self,pinsIn,pinsOut):

        super(Clicker, self).__init__("sensor",pinsIn, pinsOut)
        self.lastReading = 0


    def sens(self, auto=True):

        while True:

            self.lastReading = GPIO.input(self.pinsIn[0])
            time.sleep(0.1)

            if auto == False:
                break

    def autoSense(self):
        th = Thread(target = self.sens)
        th.setDaemon(True)
        th.start()

    def logging(self):

        f = open('log1.txt','w')

        st = time.time()
        ct = time.time()
        current = self.lastReading

        while ct - st < 3:

            if current == self.lastReading:
                pass
            else:
                f.write(str(self.lastReading)+'       '+str(ct)+'\n')
                current = self.lastReading

            ct = time.time()

        f.close()
        print 'done writing'
