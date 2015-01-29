import math
import datetime
import time
from threading import Thread

import logging
#logging.config.fileConfig("../carLog.ini")
logr = logging.getLogger('car.mapMath')

#I dont actually know what this is
WHEEL_MAX_ANGLE = 30
#distance from back axle to center of mass, in m
asub2 = 0.135
asub2sq = 182.25
#distance from front to back axle, in m
carlen = 0.325
carlensq = 1056.25

class AngleManager(object):

    #steeringInstance: the instance of the currently used steeringengine class (to get current angle)
    def __init__(self, steeringInstance, updateInterval = 0.4):
    
        #self.logr = logging.getLogger('car.mapMath.AngleMAnager')
        self.updateInterval = updateInterval
        self.a2 = asub2sq
        self.l = carlensq
        self.angleDelta = 0.0     
        self.wheelAngle = 0.0
        self.currentSpeed = 0.0
        self.currentTime = None
        self.lastTime = None
        self.exitFlag = False
        self.steeringInstance = steeringInstance
        
    def startRecording(self):
        self.exitFlag = False
        self.lastTime = datetime.datetime.now()
        self.th = Thread(target=self.updateAngle_th)
        self.th.setDaemon(True)
        self.th.start()
        
        
    def stopRecording(self):
        self.lastTime = 0.0
        self.exitFlag = True
            
    def changeSpeed(self, speed):
        self.currentSpeed = speed
        
    def deltaAngle(self, speed, timeInt, wheelAngle):
        if wheelAngle < 0:
            out = -1*((speed * timeInt)/(math.sqrt(self.a2 + (self.l * (1/math.tan(abs(wheelAngle)))))))
        else:
            #out = ((speed * timeInt)/(math.sqrt(self.a2 + (self.l * (1/math.tan(wheelAngle))))))
            #angular velocity = linear velocity * tan (wheel angle) / wheelbase (carlen)
            #thus, angular position = \int[linear velocity * tan (wheel angle) / wheelbase] (initial condition, 0)
            out = ((speed * timeInt * math.tan(math.radians(wheelAngle)))/(carlen))
        return out
        
    #speed: the approximate speed, in m/s
    def updateAngle_th(self):
        while self.exitFlag == False:
            
            self.currentTime = datetime.datetime.now()            
            deltaT = (self.currentTime - self.lastTime).microseconds / 1000000.0
            self.wheelAngle = self.steeringInstance.getAngle()
            angleDeltaPhi = self.deltaAngle(self.currentSpeed, deltaT, self.wheelAngle)
            self.angleDelta += angleDeltaPhi
            self.lastTime = datetime.datetime.now()
            #print "Thread run: deltaT: %d, wheelAngle: %d, angleDeltaPhi: %d" % (deltaT, self.wheelAngle, angleDeltaPhi)
            time.sleep(self.updateInterval)
            
    def getDeltaAngle(self):
        retAngle = self.angleDelta
        self.angleDelta = 0.0
        return retAngle
    
        
    def printAngle(self):
    
        print self.angle

if __name__ == "__main__":
    class dummyWheel(object):
        
        def getAngle(self):
            return 30.0 # 30 degree turn in rad
    
    wheel = dummyWheel()
    
    test = AngleManager(wheel)
    logr.info("The starting car angle is %f" % (test.getDeltaAngle()))
    test.changeSpeed(1.0)
    test.startRecording()
    for i in xrange(75):
        time.sleep(2)
        logr.info("%d ms*10, angle is %f degrees" % (i, (math.degrees(test.getDeltaAngle()))))
        
           
