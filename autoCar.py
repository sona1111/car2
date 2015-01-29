import time
from hardware import *

pinAssignBoard = {'FrontSensor':Pins['P0'][0]}


class autoCar(object):
    
    def __init__(self):
        
        
        self.FSens = Sensors(pinAssignBoard['FrontSensor'])
        self.dynamics = Dynamics()
        self.running = True
        print pinAssignBoard['FrontSensor']
    
    def Run(self):
        
        while self.running == True:
            
            self.setMission()
            self.Brains()
            
            
    def setMission(self):
        print "what are we going to do today?"
        print "how far to drive?"
        self.mission = {}
        self.mission['distance'] = raw_input("distance> ")
        print "how fast you wanna go?"
        self.mission['speed'] = raw_input("speed> ")
        
        
    def Brains(self):
        if(self.Lsens.clear()==True):
            self.dynamics.mMotor
            
        

        
        
class Reports(object):
    
    def __init__(self):
        
        self.printReports = True
        
    def run(self, *subProcesses):
        while self.printReports == True:
            for z in subProcesses:
                z.printReport()
    #some threaded process which continually prints reports
