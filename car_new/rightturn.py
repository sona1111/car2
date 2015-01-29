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
    
        print "mission1 thread - started"
        time.sleep(1)
        whereToGo = 'forwards'
        turningMin = 50.0
        distMin = 100.0
        cycles = 0           
            
        
        self.hw['wheel'].turn('center')
        
        
        while self.exitFlag == False: #and cycles < 100000 
        
        
            self.map.plot('forward',self.hw['fsens'].getReading())
            self.map.plot('backward',self.hw['bsens'].getReading())
            self.map.plot('left',self.hw['lsens'].getReading())
            self.map.plot('right',self.hw['rsens'].getReading())
        
            if self.hold == True:
                #time.sleep(1)
                pass
            else:
                #mp = self.map.getCombined()
                mp = self.map.prox()
                
                if(whereToGo == 'forwards'):
                    if(mp[self.map.carPos-1][self.map.carPos] == 1 
                    or mp[self.map.carPos-2][self.map.carPos] == 1
                    or mp[self.map.carPos-3][self.map.carPos] == 1
                    or mp[self.map.carPos-4][self.map.carPos] == 1):
                        self.hw['mainEngine'].move(8.0)
                        print "front stop"
                        time.sleep(0.2)
                        whereToGo = 'right'
                        self.hw['wheel'].turn('left')
                    else:
                        self.hw['mainEngine'].move(8.0)
                        print "full speed ahead"
                        
                        
                elif(whereToGo == 'backwards'):
                    if(mp[self.map.carPos+1][self.map.carPos] == 1 
                    or mp[self.map.carPos+2][self.map.carPos] == 1
                    or mp[self.map.carPos+3][self.map.carPos] == 1
                    or mp[self.map.carPos+4][self.map.carPos] == 1):
                        self.hw['mainEngine'].move(10.0)
                        print "backwards stop"
                        time.sleep(0.2)
                        whereToGo = 'forwards'
                        self.hw['wheel'].turn('center')
                    else:
                        self.hw['mainEngine'].move(-8.0)
                        print "Backwardswards + dan doesnt do anything"
                        
                elif(whereToGo == 'right'):
                      self.hw['mainEngine'].move(8.0)
                      print "Right turn with straight pl0x"
                      self.hw['wheel'].turn('center')
                      time.sleep(1.0)
                      print "Wheel go straight plz"
                      whereToGo = 'fowards'  
                        
                #if(whereToGo == 'turning'):
                #    if(
                #    #self.hw['mainEngine'].move(100.0)
                #    self.hw['wheel'].move(100.0)
                #    time.sleep(0.5)
                #    print "turning wheels and moving forward"
                #    
                #    if((self.hw['rsens'].getReading() >=  turningMin) or (self.hw['rsens'].getReading() == 'inf')):
                #        #self.hw['mainEngine'].move(100.0)
                #        self.hw['wheel'].move(-100.0)
                #        time.sleep(2)
                #        whereToGo = 'forward'
                #        print "done turning back on track"
                #    else:
                #        #self.hw['mainEngine'].move(100.0)
                #        self.hw['wheel'].move(0.0)
                #        print "waiting to turn"
                    
                        
   
                #    else:
                #        self.hw['mainEngine'].stop()
                #        whereToGo = 'backwards'
                #
                #    
                #if(self.whereToGo == 'backwards' ):
                #    if((self.hw['bsens'].getReading() >= distMin) or (self.hw['bsens'].getReading() == 'inf')):
                #        
                #        self.hw['mainEngine'].move(-30.0)
                #    else:
                #        
                #        self.hw['mainEngine'].stop()
                #        whereToGo = 'forward'
                
                time.sleep(0.04)
                #cycles += 1
            
        self.missionComplete == True
        print "mission1 thread - stopped"
