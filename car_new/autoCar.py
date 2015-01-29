import os
import time
from hardware import *
from carMath import SpeedManager
import random
#from ai.maneuverai import *
from net.Network import NetworkCommandListner
from rightturn import MissionCommandListner
import logging 


pinAssignBoard = {'FrontSensor':Pins['P0'][0]}

clear = lambda: os.system('clear')

class autoCar(object):
    
    def __init__(self):
        
        #pinsIn = echo, pinsOut = trig
        
        self.logr = logging.getLogger('car.autoCar')
        self.logr.info('Initiating Car Hardware Drivers...')
        
        self.forwardSens = UsonicSens([Pins['P5'][0]],[Pins['P4'][0]])
        self.backSens = UsonicSens([Pins['P7'][0]],[Pins['P6'][0]])
        self.leftSens = UsonicSens([Pins['CE0'][0]],[Pins['CE1'][0]])
        self.rightSens = UsonicSens([Pins['MOSI'][0]],[Pins['MISO'][0]])        
        self.mainEngine = PowerEngine([],[Pins['P0'][0],Pins['P1'][0],Pins['P2'][0],Pins['P3'][0]])
        self.wheel = SteeringEngine([],[Pins['SCLK'][0]])
        self.tempSens = TempSens()
        self.compass = Compass()
        self.accel = Accelerometer()
        self.running = True
        self.CPUTime = 0.03
        
        
        self.forwardSens.autoSense()
        self.leftSens.autoSense()
        self.rightSens.autoSense()
        self.backSens.autoSense()

        self.logr.info('Setting up mission command')
        self.missionCmd = MissionCommandListner({
            'fsens':self.forwardSens,
            'bsens':self.backSens,
            'lsens':self.leftSens,
            'rsens':self.rightSens,
            'mainEngine':self.mainEngine,
            'wheel':self.wheel,
            'compass':self.compass})
            
        self.logr.info('Setting up network commend')
        self.netCmd = NetworkCommandListner({
            'fsens':self.forwardSens,
            'bsens':self.backSens,
            'lsens':self.leftSens,
            'rsens':self.rightSens,
            'mainEngine':self.mainEngine,
            'tempsens':self.tempSens,
            'wheel':self.wheel},
            gridmap = self.missionCmd.map)
        
        
        #self.clicker1 = Clicker([Pins['P0'][0]],[])
        #self.clicker2 = Clicker([Pins['P1'][0]],[])
        #self.speed = SpeedManager()
        #self.mainEngine = PowerEngine2([],[Pins['CE1'][0]], self.forwardSens)
        
        
    def initiateVariables(self):
        #program constants        
        #min distances before evasive action
        self.distMinF = 150
        self.distMinB = 50
        self.distMinL = 50
        self.distMinR = 50
        
        #min distance to take evasive maneuvers
        self.distMinTurn = 50
        
        #global speed limit
        self.speedLimit = 10
        sd = {'0-50':10,'50-100':20,'100-150':30,'150-200':40,'200-*':50} 
    
    def Run(self):
        
        self.logr.info('Loading Car AI...')
        
        #time.sleep(0.5) #lol
        #self.initiateVariables()
        
        
        self.logr.info("Entering main loop now!")
        # ManeuverProxy setup
        

        self.missionCmd.start()
        self.missionCmd.map.setGoal(20,30)
        
        while self.running == True:
        
            #print self.compass.getHeading2()
            #print self.leftSens.getReading()
        
            if self.netCmd.hasRequest() == True:
                
                self.missionCmd.hold()
                
            if self.missionCmd.hasRequest() == True:
            
                self.missionCmd.unHold()
                
            #else:
                
                #self.logr.info("no mission and no network command - nothing to do")
                #self.mainEngine.stop()
                
                
                #speed = raw_input("> ")
                #speed = speed.split(',')
                #self.wheel.turn(float(speed[3]))
                #self.mainEngine.test(float(speed[0]),float(speed[1]),float(speed[2]))
                #self.mainEngine.move(float(speed))
                #self.scannerTest()
            
            #time.sleep(90)
                
        
        
        
        time.sleep(self.CPUTime)
            #time.sleep(0.1)
            



    def scannerTest(self):
        
        clear()
        print "forward     "+str(self.forwardSens.getReading())
        print "back     "+str(self.backSens.getReading())
        print "left        "+str(self.leftSens.getReading())
        print "right       "+str(self.rightSens.getReading())
        


