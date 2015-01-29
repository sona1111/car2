import os
import time
from hardware import *
from carMath import SpeedManager
import random


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
        
        self.distMinF = 150
        self.distMinB = 50
        self.distMinL = 50
        self.distMinR = 50
        self.distMinTurn = 50
        self.speedLimit = 20
        
        print 'init'
        
        time.sleep(1)
        self.wheel.pwmStop()

        while self.running == True:
            
            
            #self.scannerTest()
            self.sillyMission3()


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

        side = random.choice(['left','right'])
        self.wheel.rotate(0)
        print "forward     "+str(self.forwardSens.getReading())
        print "back     "+str(self.backSens.getReading())
        print "left        "+str(self.leftSens.getReading())
        print "right       "+str(self.rightSens.getReading())
        
        
        '''-------------------just run---------------------------'''       
        time.sleep(0.1)
        if ((self.forwardSens.getReading() > self.distMinF) or (self.forwardSens.getReading() == -1)):
            self.wheel.rotate(0)
            self.mainEngine.set_rotate(self.speedLimit)
            print "must move on"
    
        else:
            self.mainEngine.set_rotate(0)
            time.sleep(2)
            print "can't move any more"

            '''-------------------check if you can turn forward-------'''        
      
        
            if (self.forwardSens.getReading() > self.distMinTurn):
                  
                if ((self.leftSens.getReading() > self.distMinL) or (self.rightSens.getReading() > self.distMinR)):        
                
                    direction = 'forward'
                    if (self.turnCarTo(side, direction) == False):
                        if (side == 'left'):
                            side = 'right'
                        else:
                            side = 'left'
                        return None   
                    elif (self.turnCarTo(side, direction) == False):
                        print "what the heck happened"
                        return None

            
                '''------------------check if you can turn backwards-------'''
                           
            elif (self.forwardSens.getReading() <= self.distMinTurn):     
                
                direction = 'backwards'
                if (self.backSens.getReading() > self.distMinB):
                    
                    if (self.turnCarTo(side, direction) == False):
                        if (side == 'left'):
                            side = 'right'
                        else:
                            side = 'left'
                elif (self.turnCarTo(side, direction) == False):
                    print "what the heck happened"
                        
            else:
                print ("mission is wrong. tell your boss he is wrong")
                self.mainEngine.set_rotate(0)
            
                    
    def turnCarTo(self, side, direction):
        
        if ((side == 'left') and (direction == 'forward')):
            if(self.leftSens.getReading() > self.distMinL):
                print "gonna turn left and continue forward"
                
                self.wheel.rotate(100)
                time.sleep(1)
                self.mainEngine.set_rotate(self.speedLimit)
                time.sleep(3)
                self.mainEngine.set_rotate(0)
                time.sleep(1)
                self.wheel.rotate(0)
                return True
            else:
                print "ohh mama"
                return False          
        
        if ((side == 'right') and (direction == 'forward')):
            if(self.rightSens.getReading() > self.distMinR):
                print "gonna turn right and continue forward"   
                         
                self.wheel.rotate(-100)
                time.sleep(1)
                self.mainEngine.set_rotate(self.speedLimit)
                time.sleep(3)
                self.mainEngine.set_rotate(0)
                time.sleep(1)
                self.wheel.rotate(0)
                return True
            else:
                print "ohh mama"            
                return False  
    
        if ((side == 'left') and (direction == 'backwards')):
            if(self.leftSens.getReading() > self.distMinL):
                print "gonna turn left and continue backwards"  
                          
                self.wheel.rotate(100)
                time.sleep(1)
                self.mainEngine.set_rotate(-1 * self.speedLimit)
                time.sleep(3)
                self.mainEngine.set_rotate(0)
                time.sleep(1)
                self.wheel.rotate(0)                
                return True
            else:
                print "ohh mama"
                return False
                    
        if ((side == 'right') and (direction == 'backwards')):
            if(self.rightSens.getReading() > self.distMinR):
                print "gonna turn right and continue backwards"
            
                self.wheel.rotate(-100)
                time.sleep(1)
                self.mainEngine.set_rotate(-1 * self.speedLimit)
                time.sleep(3)
                self.mainEngine.set_rotate(0)
                time.sleep(1)
                self.wheel.rotate(0)                
                return True
            else:
                print "ohh mama"            
                return False                             
            

    def sillyMission3(self):

        time.sleep(1)

        if self.direct == 'fwd':
            print self.direct
            self.mainEngine.set_rotate(35)

            while (int(self.forwardSens.getReading()) > 20) or (int(self.forwardSens.getReading()) == -1):
            	time.sleep(0.05)
            self.mainEngine.set_rotate(0)
            self.direct = 'back'
            return None

        elif self.direct == 'back':
            print self.direct
            self.mainEngine.set_rotate(-35)
            
            while (int(self.backSens.getReading()) > 20) or (int(self.backSens.getReading()) == -1):
            	time.sleep(0.05)
            self.mainEngine.set_rotate(0)
            self.direct = 'fwd'
            return None
            
            
		#self.wheel.rt()
		
		


		#print "FWD   ",

		#self.forwardSens.getReading()

		#print "RIGHT   ",
		
		
		
		
		#print "LEFT   ",

		#self.leftSens.getReading()
		
# back 32.5
# stop 24.85
# fwd 18.8


        
class Reports(object):
    
    def __init__(self):
        
        self.printReports = True
        
    def run(self, *subProcesses):
        while self.printReports == True:
            for z in subProcesses:
                z.printReport()
    #some threaded process which continually prints reports
