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
        self.mainEngine = PowerEngine3([],[Pins['CE1'][0]])
        #self.wheel = SteeringEngine([],[Pins['CE0'][0]])
        self.running = True
        
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
        
        print 'Loading Car AI...'
        
        time.sleep(1)
        self.initiateVariables()
        
        print 'Initiating Car Sensors...'
        #begin the auto sense threads. Results of each sense will be stored in each class instance. 
        self.forwardSens.autoSense()
        self.leftSens.autoSense()
        self.rightSens.autoSense()
        self.backSens.autoSense()
        #self.mainEngine.rotate('applyBrakes',0.1)
        
        #self.wheel.turn('off')
        
               
        #self.speedTable = SpeedTable(sd)
        
        # ManeuverProxy setup
        self.maneuver = ManeuverProxy({'fSens':self.forwardSens, 'bSens':self.backSens, 'lSens':self.leftSens, 'rSens':self.rightSens, 'distMinTurnB':self.distMinTurn, 'distMinTurnF':self.distMinTurn,'distMinTurnR':self.distMinTurn,'distMinTurnL':self.distMinTurn, 'speedLimit':self.speedLimit})
        #self.maneuver.setCommand("turnToAvoid")
        
        
       # print 'motor set'
        #self.mainEngine.pwm(self.mainEngine.convertToVolt(-30))
        #self.mainEngine.pwm(self.mainEngine.convertToVolt(10))
       # time.sleep(10)
        
        
        while True:
        
            time.sleep(1)
            print "Done Initiating - Let's Drive."
            self.whereToGo = 'forward'
            self.incsomething = 0
            print ("forward drive 30")
            self.mainEngine.rotate('accelerateF',70)
            
            
            time.sleep(10)
            print ("forward drive 30")
            self.mainEngine.rotate('accelerateF',70)
            
            time.sleep(10)

            print ("Backwards drive 20")        
            self.mainEngine.rotate('accelerateB',70)
            
            time.sleep(2)
            print ("Backwards drive 30")        
            self.mainEngine.rotate('accelerateB',90)
            self.scannerTest()
            time.sleep(5)

            print("hi")
            self.mainEngine.rotate('applyBrakes',5)
            
            time.sleep(2)
        
        
        
        while self.running == True:
            
            self.scannerTest()

            time.sleep(1)
        
        
        
            #self.sillyMission2()


    def scannerTest(self):
        
        #self.mainEngine.pwmStop()
        clear()
        print "forward     "+str(self.forwardSens.getReading())
        print "back     "+str(self.backSens.getReading())
        print "left        "+str(self.leftSens.getReading())
        print "right       "+str(self.rightSens.getReading())
        
        #print "one     "+str(self.clicker1.lastReading)
        #print "two     "+str(self.clicker2.lastReading)
        
        
        




    def sillyMission2(self):
        #self.incsomething += 0.1
        #self.wheel.turn(self.incsomething)
        
        #clear()
        
        print (self.mainEngine.commandsList)
        if(self.whereToGo == 'forward'):
            if((self.forwardSens.getReading() >= self.distMinF) or (self.forwardSens.getReading() == 'inf')):
                
                self.mainEngine.rotate('accelerateF', 30)
            else:
                self.mainEngine.rotate('applyBrakes', 2)
                self.whereToGo = 'backwards'

            
        if(self.whereToGo == 'backwards' ):
            if((self.backSens.getReading() >= self.distMinF) or (self.backSens.getReading() == 'inf')):
                
                self.mainEngine.rotate('accelerateB', 30)
            else:
                
                self.mainEngine.rotate('applyBrakes', 2)
                self.whereToGo = 'forward'


            
    def sillyMission(self):

        req = self.maneuver.getResult()
        
        print "forward     "+str(self.forwardSens.getReading())
        print "back     "+str(self.backSens.getReading())
        print "left        "+str(self.leftSens.getReading())
        print "right       "+str(self.rightSens.getReading())
        
        
        '''-------------------just run---------------------------'''       
        
        #if nothing blocking and no other command, go forward
        if ((self.forwardSens.getReading() > self.distMinF) and (self.maneuver.currentCommand == None)):
            self.wheel.rotate(0)
              
            self.mainEngine.rotate('accelerateF',self.speedLimit)
            print "must move on"
    
        #set the command when you see a wall
        elif ((self.forwardSens.getReading() > self.distMinTurn) and (self.maneuver.currentCommand == None)):
            
            side = random.choice(['left','right'])
            #if you have dist to turn, init the maneuver engine
            self.maneuver.setCommand(['turnToAvoid',{'side':side}])
            
        #follow the command after you set it
        elif ((self.maneuver.currentCommand != None) and (req['altCommandRequest'] == None)):
        
            #set the steering
            self.wheel.turn(req['turnRequest'])
            #set the motor
            self.mainEngine.rotate('accelerateF',req['speedRequest'])
            
        #if the brain has another request, consider that instead
        elif ((req['altCommandRequest'] != None)):
            
            if (req['altCommandRequest'] == 'moveBack'):
                self.maneuver.setCommand(['smoothBack',{}])
            elif (req['altCommandRequest'] == 'turnLeft'):
                self.maneuver.setCommand(['turnToAvoid',{'side':'left'}])
            elif (req['altCommandRequest'] == 'turnRight'):
                self.maneuver.setCommand(['turnToAvoid',{'side':'left'}])
                
    def oldMission(self):
            
            
        
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
            
         
        #self.forwardSens.speed.printSpeed()
        #time.sleep(4)
        
        #self.wheel.pwm(SteeringEngine_c['center'])

        #self.mainEngine.pwm(3.3)

        #while (int(self.forwardSens.getReading()) > 90) or (int(self.forwardSens.getReading()) == -1):
        #	time.sleep(0.05)

            '''
        self.mainEngine.set_rotate(0)
        print "gonna start in 4"
        time.sleep(1)
        print "gonna start in 3"
        time.sleep(1)
        print "gonna start in 2"
        time.sleep(1)
        print "gonna start in 1"
        time.sleep(1)
            '''
        
        
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
