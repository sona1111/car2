from hardware import *
import math

class AngleManager(object):

    def __init__(self, sm, timeInt):
    
        self.sm = sm
        self.a2 = hardware.asub2sq
        self.l = hardware.carlensq
        self.angle = 0
        self.timeInt = timeInt
        self.wheelAngle = 0
        
    def calculate_th(self):
    
        self.angle = ((self.sm.aveSpeed * self.timeInt)/(math.sqrt(self.a2 + (self.l * math.cot(self.wheelAngle)))))
        
    def updateByHardware(self, newWheelAngle):
    
        #convert the input angle to the actual angle
        w = (100*maxAngle)/newWheelAngle
        
        self.wheelAngle = newWheelAngle
        
    def printAngle(self):
    
        print self.angle

class SpeedManager(object):

	def __init__(self, n = 5):
		
		self.distArr = [[0,0],[0,0]]
		self.rawSpeed = 0
		self.speedArr = [0] * n		
		self.aveSpeed = 0


	def updateBySensor(self, newDist, newTime):
		
		self.distArr[0][0] = self.distArr[0][1]
		self.distArr[1][0] = self.distArr[1][1]
		
		self.distArr[0][1] = newDist
		self.distArr[1][1] = newTime
		
		self.rawSpeed = (-1)*(self.getSlope(self.distArr[1][1], self.distArr[0][1], self.distArr[1][0], self.distArr[0][0]))
		
		#self.speedArr.pop(0)
		#self.speedArr.append(self.rawSpeed)
		#self.aveSpeed = self.lowRounder(self.average(self.speedArr),10)
		self.aveSpeed = self.lowRounder(self.rawSpeed,8)
		
	def average(self, arr):
		
		
		tot = 0
		n = len(arr)
		if n == 0:
			return False
		else:
			for speed in arr:
				tot += speed
			return (tot/n)
	
	def getSlope(self, x1, y1, x2, y2):		
		
		try:
			out = ((y2-y1)/(x2-x1))
			return out
		except:
			return False
	
	def lowRounder(self, num, ranger):
		return (int(num/ranger))*ranger
		
			
	def printSpeed(self):
		
		print "speed = " + str(round(self.aveSpeed,2))
		
class DistSmoother(object):

    def __init__(self, outliarThreshold, confirmThreshold, n = 3):

        self.outliarThreshold = float(outliarThreshold)
        self.confirmThreshold = float(confirmThreshold)
        self.distArr = [0] * n			
        self.outliar = None


    def updateBySensor(self, newDist):

        #if the new value is 100% different or more from the average of the rest of the array, drop it, but add a note incase the next value agrees. 
        
        oldDist = self.average(self.distArr)
        difference = ((abs(newDist-oldDist))/((newDist+oldDist)/2))

        if self.outliar == None:

            if (difference > self.outliarThreshold):

                self.outliar = oldDist

            else:    

                #update the array
                self.distArr.insert(0,newDist)
                self.distArr.pop()
                
        else:

            differenceOutliar = ((abs(newDist-self.outliar))/((newDist+self.outliar)/2))

            #if the outliars agree, they are not outliars
            if (differenceOutliar < self.confirmThreshold):

                self.distArr.insert(0,outliar)
                self.distArr.insert(0,newDist)
                self.distArr.pop()
                self.distArr.pop()

            #if not, drop the outliar completely
            else:
                self.distArr.insert(0,newDist)
                self.distArr.pop()
            
            self.outliar = None	
                
	
    def average(self, arr):
	
	
	    tot = 0
	    n = len(arr)
	    if n == 0:
		    return False
	    else:
		    for speed in arr:
			    tot += speed
		    return (tot/n)
			
    def getDist(self):
        return self.average(self.distArr)
        
class FileWriter(object):

    def __init__(self):
        pass
		

		
