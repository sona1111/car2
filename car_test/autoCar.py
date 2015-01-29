import os
import time
from hardware import *
from carMath import SpeedManager
import random
from ai.maneuverai import *

pinAssignBoard = {'FrontSensor':Pins['P0'][0]}

clear = lambda: os.system('clear')

class autoCar(object):
    
    def __init__(self):
        
        #pinsIn = echo, pinsOut = trig
        self.forwardSens = UsonicSens([Pins['P2'][0]],[Pins['P3'][0]])
        self.backSens = UsonicSens([Pins['P0'][0]],[Pins['P1'][0]])
        self.leftSens = UsonicSens([Pins['P4'][0]],[Pins['P5'][0]])
        self.rightSens = UsonicSens([Pins['P6'][0]],[Pins['P7'][0]])        
        #self.mainEngine = PowerEngine2([],[Pins['CE1'][0]], self.forwardSens)
        self.mainEngine = PowerEngine3([],[Pins['CE1'][0]])
        
        #self.clicker1 = Clicker([Pins['P0'][0]],[])
        #self.clicker2 = Clicker([Pins['P1'][0]],[])
        self.wheel = SteeringEngine([],[Pins['CE0'][0]])
        self.running = True
        #self.speed = SpeedManager()
        
        
        
        self.direct = 'fwd'
        
        
        
    
    def Run(self):
        
        #begin the auto sense threads. Results of each sense will be stored in each class instance. 
        self.forwardSens.autoSense()
        self.leftSens.autoSense()
        self.rightSens.autoSense()
        self.backSens.autoSense()
        #self.clicker1.autoSense()
        
        self.wheel.rotate(0)
        
        self.distMinF = 100
        self.distMinB = 50
        self.distMinL = 50
        self.distMinR = 50
        self.distMinTurn = 90
        self.speedLimit = 30
        self.maneuver = ManeuverProxy({'fSens':self.forwardSens, 'bSens':self.backSens, 'lSens':self.leftSens, 'rSens':self.rightSens, 'distMinTurnB':self.distMinTurn, 'distMinTurnF':self.distMinTurn,'distMinTurnR':self.distMinTurn,'distMinTurnL':self.distMinTurn, 'speedLimit':self.speedLimit})
        print 'init'
        
        time.sleep(1)

        while self.running == True:
            
            
            #self.scannerTest()
            self.sillyMission()


    def scannerTest(self):
    
        #self.mainEngine.pwmStop()
        print "forward     "+str(self.forwardSens.getReading())
        print "back     "+str(self.backSens.getReading())
        print "left        "+str(self.leftSens.getReading())
        print "right       "+str(self.rightSens.getReading())
        
        #print "one     "+str(self.clicker1.lastReading)
        #print "two     "+str(self.clicker2.lastReading)
        
        
        time.sleep(1)
        clear()

            
    def sillyMission(self):

        req = self.maneuver.getResult()
        clear()
        print req
        
        #print "forward     "+str(self.forwardSens.getReading())
        #print "back     "+str(self.backSens.getReading())
        #print "left        "+str(self.leftSens.getReading())
        #print "right       "+str(self.rightSens.getReading())
        
        
        '''-------------------just run---------------------------'''       
        
        #if nothing blocking and no other command, go forward
        if ((self.forwardSens.getReading() > self.distMinF) and (self.maneuver.currentCommand == None)):
            self.wheel.rotate(0)
              
            self.mainEngine.set_rotate(self.speedLimit)
            print "must move on"
    
        #set the command when you see a wall
        elif ((self.forwardSens.getReading() > self.distMinTurn) and (self.maneuver.currentCommand == None)):
            
            side = random.choice(['left','right'])
            #if you have dist to turn, init the maneuver engine
            self.maneuver.setCommand(['turnToAvoid',{'side':side}])
            
        #follow the command after you set it
        elif ((self.maneuver.currentCommand != None) and (req['altCommandRequest'] == None)):
            print '---------------------------------------------------'
            #set the steering
            self.wheel.rotate(req['turnRequest'])
            #set the motor
            self.mainEngine.set_rotate(req['speedRequest'])
            self.maneuver.maneuver.altCommandRequest = None
        #if the brain has another request, consider that instead
        elif ((req['altCommandRequest'] != None)):
            
            if (req['altCommandRequest'] == 'moveBack'):
                self.maneuver.setCommand(['smoothBack',{}])
            elif (req['altCommandRequest'] == 'turnLeft'):
                self.maneuver.setCommand(['turnToAvoid',{'side':'left'}])
            elif (req['altCommandRequest'] == 'turnRight'):
                self.maneuver.setCommand(['turnToAvoid',{'side':'left'}])

        time.sleep(1)

        
class Reports(object):
    
    def __init__(self):
        
        self.printReports = True
        
    def run(self, *subProcesses):
        while self.printReports == True:
            for z in subProcesses:
                z.printReport()
    #some threaded process which continually prints reports
