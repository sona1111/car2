import time
from threading import Thread
from aimath import *


'''
Maneuver: perform a turn or move in a predefined path with conditions.

This is a mid-level class which accepts some kind of maneuver as input and returns a recommend action which the wheels and motor should be doing. Only one instance should be needed for normal operation. This class is NOT meant for actually making decisions about a path to take, and the return values are suggestions only to the brain and not direct connections to the low level classes. 

For example: a 'turn' method will, under normal circumstances, inform the brain of the degrees the wheels should be turned and the speed that the mainengine will be moving, but it will also take note of the sensor data to make sure that the turn does not being the car too close to an object, and it will tell the brain to stop unless an override argument is given. Despite this, it should usually be the main job of the brain to keep out of the way of objects without relying on this class. It only provides another level of protection

Some commands require that something different be done if the command is being called from the brain or if the command is just continuing to run from previously. This is actually quite a challenge to get right. For now I am using a proxy class to manage it. The proxy class adds one more layer of abstraction, and contains the thread mechanics
'''
class ManeuverProxy(object):
    
    def __init__(self, inputs):
        
        self.maneuver = ManeuverAI(inputs)
        self.currentCommand = None
        self.th = Thread(target = self.maneuver_th)
        self.th.setDaemon(True)
        self.th.start()
        
    #This thread keeps going. There is a small amount of sleep when no commands are being processed so that we don't waste too much cpu time on the thread. self.currentCommand is only true the first time getattr is called, as it should be.
    def maneuver_th(self):
    
        while True:
            
            if (self.currentCommand == None):
                time.sleep(0.05)
                
            else:
                getattr(self.maneuver, self.currentCommand[0])(self.currentCommand[1])
                self.maneuver.newCommand = False
            
    #remember to set command back to None in the parent object when we dont need to process anything
    def setCommand(self,command):
        
        if (self.currentCommand != command):
            self.maneuver.newCommand = True
            self.currentCommand = command
            self.maneuver.altCommandRequest = None
        
    #returns what the maneuver things we should do to complete the action
    def getResult(self):
    
        return {'turnRequest':self.maneuver.turnRequest,'speedRequest':self.maneuver.speedRequest, 'altCommandRequest':self.maneuver.altCommandRequest}

class ManeuverAI(object):

    def __init__(self, inputs):
        
        
        self.fSens = inputs.get('fSens', dummySensor('fSens'))
        self.bSens = inputs.get('bSens', dummySensor('bSens'))
        self.lSens = inputs.get('lSens', dummySensor('lSens'))
        self.rSens = inputs.get('rSens', dummySensor('rSens'))
        self.distMinTurnF = inputs.get('distMinTurnF', 100)
        self.distMinTurnB = inputs.get('distMinTurnB', 100)
        self.distMinTurnL = inputs.get('distMinTurnL', 100)
        self.distMinTurnR = inputs.get('distMinTurnR', 100)
        self.speedLimit = inputs.get('speedLimit', 30)
        
        #we constantly request a speed and turn direction which the brain can choose to follow
        self.turnRequest = 0
        self.speedRequest = 0
        
        #if we need to execute a different maneuver based on the conditions, we set the name of the action (one of the method names of this object) in this variable.
        self.altCommandRequest = None
        
        self.turnCounter = GenericCounter(0, 0, 0)
        self.turnSlope = SlopeMonitor(5)
        self.newCommand = False
        
        
    '''
    a general turning function which will not turn for a specific time or anount, but rather will continue to turn until the distance from the sidesensor levels off and begins to increase (in other words, slightly further than needed) Accepts the preferred starting direction: to the left or to the right. 
    '''
    def turnToAvoid(self, force = False, **args):
    
        side = args.get('side','left')
    
        #begin by checking surroundings to make sure we have enough space in front
        if ((self.fSens.getReading() <=  self.distMinTurnF) and (force == False)):
        
            self.turnRequest = 0
            self.speedRequest = 0
            self.altCommandRequest = 'moveBack'
            
        #special case, the user wants to invoke the turn logic without worrying about problems
        elif (force == True):
            self.turnToAvoid_f(side)
            
        #otherwise continue with the turn logic itself
        else:
    
            if side == 'left':
                #proceed to check for issues blocking the left side
                if False: #(self.lSens.getReading() <= self.distMinTurnL):
                
                    self.altCommandRequest = 'turnRight'
                    
                else:
                    
                    #do the actual turn
                    self.turnRequest = 100 # full left turn
                    self.speedRequest = self.speedLimit
                    
                    #wait a few counts before judging distance based on the sensor
                    #this gives time for the slope monitor to get some values to judge
                    #IDEALLY THE TURNCOUNTER SHOULD BE AS LONG AS THE TURNSLOPE ARRAY (but it is not mandatory)
                    if self.newCommand == True:
                        self.turnCounter.setup(0,5,0)
                        self.turnSlope.reset()
                        
                    wait = self.turnCounter.inc()
                    self.turnSlope.addVal(self.rSens.getReading())
                    
                    #as long as the counter has expired, we can start checking for changes from the rightsensor
                    if wait == False:
                        
                        #we wait for the slopemonitor to change from decreasing distance to increasing
                        if self.turnSlope.get() == '+':
                        
                            #the turn is complete
                            self.turnRequest = 0
                            self.speedRequest = 0
                        
            #all the same as above but for right turn
            if side == 'right':
                if False:#(self.rSens.getReading() <= self.distMinTurnR):
                    self.altCommandRequest = 'turnLeft'
                else:
                    self.turnRequest = -100
                    self.speedRequest = self.speedLimit
                    if self.newCommand == True:
                        self.turnCounter.setup(0,5,0)
                        self.turnSlope.reset()
                    wait = self.turnCounter.inc()
                    self.turnSlope.addVal(self.lSens.getReading())
                    if wait == False:
                        if self.turnSlope.get() == '+':
                            self.turnRequest = 0
                            self.speedRequest = 0
                        
    #same function as above without chekcing sensors.
    #XXX place the force functions into yet another class? I don't know.
    def turnToAvoid_f(self, side):
    
            if side == 'left':
                self.turnRequest = 100
                self.speedRequest = self.speedLimit
                if self.newCommand == True:
                    self.turnCounter.setup(0,5,0)
                    self.turnSlope.reset()
                wait = self.turnCounter.inc()
                self.turnSlope.addVal(self.rSens.getReading())
                if wait == False:
                    if self.turnSlope.get() == '+':
                        self.turnRequest = 0
                        self.speedRequest = 0

            if side == 'right':
                self.turnRequest = -100
                self.speedRequest = self.speedLimit
                if self.newCommand == True:
                    self.turnCounter.setup(0,5,0)
                    self.turnSlope.reset()
                wait = self.turnCounter.inc()
                self.turnSlope.addVal(self.lSens.getReading())
                if wait == False:
                    if self.turnSlope.get() == '+':
                        self.turnRequest = 0
                        self.speedRequest = 0

'''
This object avoids errors if a sensor is unspecified, allows the Maneuverclass to continue just in case
'''
class dummySensor(object):
    
    def __init__(self, debug):
        print 'A dummy sensor was created! Position: %s' % (debug)
    
    def getReading(self):
        return 0
    
