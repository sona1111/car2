from carMath import SpeedManager, DistSmoother, AngleManager
import time
import datetime
import RPi.GPIO as GPIO
from threading import Thread
import math
import timeit
import os

clear = lambda: os.system('clear')

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
#PowerEngine = {"forward":0.188,"backwards":0.325,"stop":0.257}
PowerEngine = {"forward":0.3135,"backwards":0.5775,"stop":0.462}
#PowerEngine = {"forward":0.216,"backwards":0.373,"stop":0.299}

SteeringEngine_c = {"left":0.13,"right":0.35,"center":0.208}
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

        # set specific type of hardware variables
        if (Type == "pwm"):
            self.frequency = 100
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
            
            self.p.ChangeDutyCycle(VPercent)

    def pwmStop(self):
        self.p.ChangeDutyCycle(0)


'''--------------------------------------------------------------------------------------------------------------------------'''        
'''-----------------------------------------------------Ultra Sonic Sensors--------------------------------------------------'''
'''--------------------------------------------------------------------------------------------------------------------------'''

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
                self.lastReading = float('inf')



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

'''--------------------------------------------------------------------------------------------------------------------'''
'''-----------------------------------------------------Steering Engine Class------------------------------------------'''
'''--------------------------------------------------------------------------------------------------------------------'''

class SteeringEngine(Hardware):


    def __init__(self,pinsIn,pinsOut):
        super(SteeringEngine, self).__init__("pwm",pinsIn, pinsOut)
        #self.am = AngleManager()
        self.p.start(100)                  #setting the GPIO
        self.pwm(self.convertToVolt(0.0))  #pulsing 0 volts out
        
        # engine thread initiation #
        self.timer = [0]*2                 # [0]-initial time, [1]-final time 
        self.commandsList = [[0,1],['off',1]]      # VoltagePercent, TimeFrame
        self.lastCommands = [[None,None]]*3
        self.override = False              # False-override is not needed, True-override is needed 
        self.startECE = True
        self.ECE_th = Thread(target=self.ECE)
        self.ECE_th.setDaemon(True)
        self.ECE_th.start()
        
    
    #command takes a list, the first value is speed percent and the second is direction or brake
    def override(self, command):
        
        self.commandsList = [command]    
        self.override = True
        
    def ECE(self): #engineCommandExecuter
        
        #while engineCommandExecuter is True check for engine commands
        while self.startECE:
            #print ('len of turning command list: ', len(self.commandsList), 'and it looks like', self.commandsList,) 
            
            if (self.override == True):
                print ("overriding turning")
                self.pwm(self.convertToVolt(self.commandsList.pop(0)[0]))
                self.override = False
            
            else:

                #if there is something to do 
                if (len(self.commandsList) != 0):
                    self.timer[1] = time.time()*1000
                    print ("im setting time",self.timer[1]) 
                    # checking time frame from first measured to second measured to ensure the command is executed only after the specified time
                    if (self.timer[1] - self.timer[0] > self.commandsList[0][1]):
                            print ("im poping+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
                            self.pwm(self.convertToVolt(self.commandsList.pop(0)[0]))
                            self.timer[0] = time.time()*1000 # reset the timer
                else:
                    print ('sending off turning')
                    self.pwm(self.convertToVolt('off'))
                        
                
                time.sleep(0.002) #minute sleep just so the brain can rest
                

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


    def turn(self,angle):
        print (angle)
        if ((self.lastCommands[-1][0] == angle) and (self.lastCommands[-2][0] == angle) and (self.lastCommands[-3][0] == angle)):
            #print("Repetitiveness, I'm receiving the same angle too many times. I will not add it to the commandsList. \n \t \t angle value of: ", angle)
            pass
        else:
            self.commandsList.append([angle,0])
            self.lastCommands.append([angle,0])
            self.lastCommands.pop(0)
        
'''--------------------------------------------------------------------------------------------------------------------------'''        
'''-----------------------------------------------------Power Engine Class---------------------------------------------------'''
'''--------------------------------------------------------------------------------------------------------------------------'''
            
class PowerEngine3(Hardware):

    def __init__(self,pinsIn,pinsOut):
        super(PowerEngine3, self).__init__("pwm",pinsIn, pinsOut)
        self.pinsIn = pinsIn
        self.pinsOut = pinsOut
        self.p.start(100)
        self.pwm(self.convertToVolt(0.0))
        self.speedPercent = 0.0
        
        # engine initiation
        self.timer = [0]*2 # [0]-initial time, [1]-final time 
        self.commandsList = [[0,0.1]] # VoltagePercent, TimeFrame
        self.override = False # False-override is not needed, True-override is needed 
        self.startECE = True
        self.ECE_th = Thread(target=self.ECE)
        self.ECE_th.setDaemon(True)
        self.ECE_th.start()
        self.lastCommands = [[None,None]]*3
        
        
    def newSleep(self, t):
        
        for s in (t*1000):
            if self.abortFlag == True:
                return None
            else:
                time.sleep(0.001)
        return None
    
    #command takes a list, the first value is speed percent and the second is direction or brake
    def override(self, command):
        
        self.commandsList = [command]    
        self.override = True
    
    def ECE(self): #engineCommandExecuter
        
        #while engineCommandExecuter is True check for engine commands
        while self.startECE:
            
            #print('-------------------------------------------------------------------------------------------------------')
            if (self.override == True):
                
                
                self.pwm(self.convertToVolt(self.commandsList.pop(0)[0]))
                self.override = False
            
            else:
                clear()
                print ('len of turning command list: ', len(self.commandsList), 'and it looks like', self.commandsList,) 
                print self.lastCommands
                #if there is something to do 
                if (len(self.commandsList) != 0):
               
                    self.timer[1] = time.time()*1000
                    #print ("sec diff", self.timer[1] - self.timer[0])
                    # checking time frame from first measured to second measured to ensure the command is executed only after the specified time
                    if (self.timer[1] - self.timer[0] > self.commandsList[0][1]*1000):
                            
                            
                            self.pwm(self.convertToVolt(self.commandsList.pop(0)[0]))
                            self.timer[0] = time.time()*1000 # reset the timer
                            
                            #self.commandsList.pop(0)
                
                time.sleep(0.01) #minute sleep just so the brain can rest


    def accelerateF(self, HSTAGP): #How Strong To Apply Gas Pedal
        print ("accelerating forward")
        if ((self.lastCommands[-1] == 'applyBrakes') or (self.lastCommands[-1] == 'accelerateF') or (self.lastCommands[-1] == None)): 
            print ("i can drive regularly forward")
            #self.commandsList.append([0,0.2])                      #idle command
            self.commandsList.append([HSTAGP,0.2])                      #thrust command
        if (self.lastCommands[-1] == 'accelerateB'): 
            print ("in order to drive i must first stop")
            self.applyBrakes(3)
            #self.commandsList.append([0,0.2])                      #idle command
            self.commandsList.append([HSTAGP,0.2])                      #thrust command

        self.lastCommands.pop(0)
        self.lastCommands.append('accelerateF')
            


    
    def accelerateB(self, HSTAGP):
        print ("accelerating backwards")
        if ((self.lastCommands[-1] == 'applyBrakes') or (self.lastCommands[-1] == 'accelerateB') or (self.lastCommands[-1] == None)): 
            print ("i can just drive regularly backwards")
            #self.commandsList.append([0, 0.2])                      #idle command
            self.commandsList.append([-1 * HSTAGP, 0.2])                 #backwards thrust command
        if (self.lastCommands[-1] == 'accelerateF'): 
            print ("in order to drive i must first stop")
            self.applyBrakes(3)
            #self.commandsList.append([0, 0.2])                      #idle command
            self.commandsList.append([-1 * HSTAGP, 0.2])                      #backwards thrust command
        
        self.lastCommands.pop(0)
        self.lastCommands.append('accelerateB')
    
    
    def applyBrakes(self, HLTAB): #How Long To Apply Brakes
        print ("applying brakes")
        if ((self.lastCommands[-1] == 'applyBrakes') or (self.lastCommands[-1] == None)):
            self.commandsList.append([0, 0.1])                      #idle command
            self.commandsList.append(['off', 0.1])                      #off command
            
        elif (self.lastCommands[-1] == 'accelerateF'):
            self.commandsList.append([30, 0.1])                 #forward thrust command for a fraction of a sec
            self.commandsList.append([-100, HLTAB])                 #backwards thrust command for long time to make sure we stopped
            self.commandsList.append([0, 0.1])                      #idle command
            #self.commandsList.append(['off', 0.1])                      #off command
            
        elif (self.lastCommands[-1] == 'accelerateB'):
            self.commandsList.append([-30, 0.1])                 #forward thrust command for a fraction of a sec
            self.commandsList.append([100, HLTAB])                 #backwards thrust command for long time to make sure we stopped
            self.commandsList.append([0, 0.1])                      #idle command
            #self.commandsList.append(['off', 0.1])                      #off command
            
        self.lastCommands.pop(0)
        self.lastCommands.append('applyBrakes')
        
        
    def rotate(self, command, args):
        
        print self.lastCommands
        if((self.lastCommands[-1] == command) and (self.lastCommands[-2] == command) and (self.lastCommands[-3] == command)): 
            print "i won't do a thing cause its just a repetitive job"
            
        else:
            print "lets try to:", command
            getattr(self, command)(args)
        

    def convertToVolt(self, value):
        if (value == None):
            return None
        
        if (value == 'off'):
            return 0
            
        else:
            value = float(value)
            if (value >= -100.0 and value < 0.0):
                return (((PowerEngine['backwards'] - PowerEngine['stop'])/100)*(-value))+PowerEngine['stop']
    
            elif (value <= 100.0 and value > 0.0):
                return PowerEngine['stop']-(((PowerEngine['stop'] - PowerEngine['forward'])/100)*value)
    
            else:
                return PowerEngine['stop']

        
    def Roll(self):
        pass
        

'''
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


    def printReport(self):
        for name, data in self.mSteering.iteritems():
            print name + " " + str(data)
        for name, data in self.mMotor.iteritems():
            print name + " " + str(data)

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

'''
        

''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
        
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
