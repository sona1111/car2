from threading import Thread
import time
#import logging as logr
import os
import logging
from ai.map import AreaMap


clear = lambda: os.system('clear')

class dummyWheel(object):
        
        def getAngle(self):
            return 0.0

class MissionCommandListner(object):

    def __init__(self, hardware):
        
        self.logr = logging.getLogger('car.mission')
        self.hw = hardware
        self.missionComplete = False
        self.exitFlag = False
        self.onHold = False
        wheel2 = dummyWheel()
        self.map = AreaMap(self.hw['compass']) #self.hw['wheel']

        
        
    def hold(self):
        self.onHold = True
        
    def unHold(self):
        self.onHold = False
        
    def hasRequest(self):
        if self.missionComplete == False:
            return True
        else:
            return False
            
    def start(self):
    
        self.th = Thread(target=self.mission1)
        self.th.setDaemon(True)
        self.th.start()
        
    def stop(self):
    
        self.exitFlag = True
            
    def mission1(self):
    
        
        self.logr.info("mission1 thread - started")
        time.sleep(1)
        
        
        whereToGo = 'forward'
        distMin = 50.0
        cycles = 0       
        
        enginePower = 7.0
        self.exitFlag = False
        while self.exitFlag == False: #and cycles < 100000
            
            if self.onHold == True:
                time.sleep(1)
            else:
                
                #clear()
                #self.map.clear()
                #self.map.plot('forward',self.hw['fsens'].getReading())
                #self.map.plot('backward',self.hw['bsens'].getReading())
                #self.map.plot('left',self.hw['lsens'].getReading())
                #self.map.plot('right',self.hw['rsens'].getReading())
                #self.map.prox(100)
                #self.hw['wheel'].turn('center')
                self.logr.info(whereToGo)
                #print self.hw['fsens'].getReading()
                #print self.hw['bsens'].getReading()
                if(whereToGo == 'forward'):
                    if(self.hw['fsens'].getReading() >= distMin):
                        
                        self.hw['mainEngine'].move(enginePower)
                    elif(self.hw['bsens'].getReading() >= distMin):
                        self.hw['mainEngine'].stop()
                        time.sleep(0.1)
                        self.hw['mainEngine'].move(-enginePower)
                        whereToGo = 'backwards'
                    else:
                        self.hw['mainEngine'].move(0.0)

                    
                if(whereToGo == 'backwards' ):
                    if(self.hw['bsens'].getReading() >= distMin):
                        
                        self.hw['mainEngine'].move(-enginePower)
                    elif(self.hw['fsens'].getReading() >= distMin):
                        self.hw['mainEngine'].stop()
                        time.sleep(0.1)
                        self.hw['mainEngine'].move(enginePower)                      
                        
                        whereToGo = 'forward'
                    else:
                        self.hw['mainEngine'].move(0.0)
                
                time.sleep(0.5)
                cycles += 1
               
        self.missionComplete == True
        self.logr.info("mission1 thread - stopped")
