import numpy as np
import math
from threading import Thread
from mapMath import AngleManager
import time
import scipy.ndimage
import logging
from mapai import PathCalc
#logging.config.fileConfig("carLog.ini")

import copy

SENSOR_MAX_DISTANCE = 400

np.set_printoptions(threshold='nan')


#handles mapping out the area. stores an array of constant size with the car always represented in the center 
class AreaMap(object):

    def __init__(self, compass, unitWidth = 5):
        
        
        self.logr = logging.getLogger('map.AreaMap')
        #self.angleManager = AngleManager()  
        #self.angleManager.startRecording()   
        #amount of square cm each array element represents
        self.unitWidth = unitWidth
        #the number of array elements across one array parallel
        self.arrWidth = SENSOR_MAX_DISTANCE / self.unitWidth / 2
        #generate the main map
        self.mapArr = np.array([[0 for x in xrange(self.arrWidth)] for x in xrange(self.arrWidth)])
        
        self.pc = PathCalc()
        
        #set the position of the car to the center of the array
        self.carPos = self.arrWidth/2
        self.mapArr[self.carPos][self.carPos] = 2
                
        self.goal = [0,0]
        self.dataBeforeFrame = 4
        self.frameBuffer = queue(self.mapArr, compass, length=4)
        
        #self.th = Thread(target=self.makeFrame_th)
        #self.th.setDaemon(True)
        #self.th.start()

    def getCombined(self):
    
        return self.frameBuffer.getCombined()
        
    #generate the next frame and add it to the frameBuffer. Angle is calculated with the angle manager class
    def makeFrame_th(self):    
                
        while True:            
            
            self.frameBuffer.put(self.mapArr)                     
            self.clear()
            time.sleep(0.1)
    
    def count1s(self, arr):
        num1s = 0
        if arr != None:
            for row in arr:
                for col in row:
                    if col == 1:
                        num1s += 1
        return num1s
        
    #take one old map and the current turn angle and calculate the position of all of the new elements on the array
    def ajustPosition_old(self, oldMap): 
        #print "calling ajustposition"       
        #deltaAngle = self.angleManager.getDeltaAngle()
        deltaAngle = math.pi/16
        valuesToAdd = []
        valuesToRemove = []
        for y, row in enumerate(oldMap):
            for x, val in enumerate(row):                
                if val == 1: # 1; an obstacle                    
                    x1 = x - (self.carPos)
                    y1 = y - (self.carPos)
                    x2 = int((x1 * math.cos(deltaAngle)) - (y1 * math.sin(deltaAngle)) + (self.carPos))
                    y2 = int((x1 * math.sin(deltaAngle)) + (y1 * math.cos(deltaAngle)) + (self.carPos))
                    #x2 = (x * math.cos(deltaAngle)) - (y * math.sin(deltaAngle))
                    #y2 = (x * math.sin(deltaAngle)) + (y * math.cos(deltaAngle))
                    h = math.sqrt(x2**2 + y2**2)
                    #oa = self.calcAngle(float(x1), float(y1))
                    #x2 = (h * math.cos(oa+deltaAngle))+self.carPos
                    #y2 = (h * math.sin(oa+deltaAngle))+self.carPos
                    #self.logr.info(self.carPos)
                    self.logr.info("h:%f" % (h))
                    valuesToRemove.append((y,x,))
                    valuesToAdd.append((y2,x2,))                    
        for val in valuesToRemove:
            oldMap[val[0]][val[1]] = 0
        for val in valuesToAdd:
            oldMap[val[0]][val[1]] = 1
        
              
        return oldMap
    
    
    
#     def calcAngle(self, x, y):        
#         
#         if x == 0 and y < 0:            
#             out = math.pi + math.pi/2
#         elif x == 0 and y > 0:            
#             out = math.pi/2
#         elif y == 0 and x < 0:            
#             out = math.pi
#         elif y == 0 and x > 0:            
#             out = 0                         
#         elif x > 0 and y > 0:            
#             out = abs(math.atan(y/x))
#         elif x < 0 and y < 0:            
#             out = math.pi + abs(math.atan(y/x))
#         elif x < 0 and y > 0:           
#             out = math.pi/2 + abs(math.atan(y/x))        
#         elif x > 0 and y < 0:               
#             out = math.pi + math.pi/2 + abs(math.atan(y/x))
#         
#         
#         else:            
#             out = 0
#         return out
    
    #return a map of the immediate area only
    #value of r is currently in array unit scale, not CM
    def prox(self, r=999999999):
        #return self.mapArr
        #return self.addDirections()
        return self.frameBuffer.getLast()
        #self.mapArr = self.sition(self.mapArr)
        
        #the MAX builtin is required to make sure no negative array indicies are requested
        #print self.mapArr[(max(0,self.carPos-r)):(self.carPos+r),(max(0,self.carPos-r)):(self.carPos+r)]
 
    #convert any units the car provides into units based on the map array
    def scale(self, val):
        
        try:
            out = int((float(val)/float(self.arrWidth)))
        except:
            out = 99999999999 #almost inf
        return out
    
    #this function adds a known obstacle to the map array
    #this assumes we have 4 sensors on the car
    #the cardinal specifies the direction of the sensor as a string, "left", "right", "forward", or "backward"
    #direction finds the current rotation of the vehicle (in degrees), which should be kept track of by the position object
    #this assumes that the default direction of the car when it begins moving is looking DOWN the array. 
    #distance is the raw reading from the sensor
    def plot_old(self, cardinal, direction, distance):
        
        if cardinal == "forward":
            cx = round(self.scale(distance*(math.sin(math.radians(direction)))),1)
            cy = round(self.scale(distance*(math.cos(math.radians(direction)))),1)
            
        elif cardinal == "backward":
            cx = round(self.scale(distance*(math.sin(math.radians(direction+180)))),1)
            cy = round(self.scale(distance*(math.cos(math.radians(direction+180)))),1)
            
        elif cardinal == "left":
            cx = round(self.scale(distance*(math.sin(math.radians(direction+90)))),1)
            cy = round(self.scale(distance*(math.cos(math.radians(direction+90)))),1)
            
        elif cardinal == "right":
            cx = round(self.scale(distance*(math.sin(math.radians(direction-90)))),1)
            cy = round(self.scale(distance*(math.cos(math.radians(direction-90)))),1)
            
        #this is a temporary solution. Really the map should expand as we travel
        try:
            self.mapArr[(self.arrWidth/2)+cy][(self.arrWidth/2)+cx] = 1
        except:
            self.logr.warning("plot was outside of array range")
            
    #the new plot assumes that the car is always fixed and the map "moves"
    def plot(self, cardinal, distance):
        
        distance = float(distance + self.arrWidth)
        
        
        if cardinal == "forward":
            cx = self.carPos
            cy = round(self.carPos - self.scale(distance),1)
            
        elif cardinal == "backward":
            cx = self.carPos
            cy = round(self.carPos + self.scale(distance),1)
            
        elif cardinal == "left":
            cx = round(self.carPos - self.scale(distance),1)
            cy = self.carPos
            
        elif cardinal == "right":
            cx = round(self.carPos + self.scale(distance),1)
            cy = self.carPos
            
        #this is a temporary solution. Really the map should expand as we travel
        try:            
            self.mapArr[cy][cx] = 1
            
        except:
            self.logr.warning("plot was outside of array range")
        else:
            self.dataBeforeFrame -= 1
            if self.dataBeforeFrame == 0:
                self.frameBuffer.put(self.mapArr)
                
                self.clear()
                
                self.dataBeforeFrame = 4
            
    def addDirections(self):
    
        
        mapthing = self.frameBuffer.getCombined()
        searched = copy.deepcopy(mapthing)
        directions = self.pc.calculateBestPath(self.carPos,self.carPos,searched)
        
        #self.logr.info(directions)
        
        if directions != False:
            currentPos = [self.carPos,self.carPos]
            for direct in directions:
                if direct[0] == 'f':
                    for i in range(direct[1]):                
                        currentPos[0] -= 1
                        try:
                            mapthing[currentPos[0]][currentPos[1]] = 4
                        except:
                            pass
                elif direct[0] == 'b':
                    for i in range(direct[1]):                
                        currentPos[0] += 1
                        try:
                            mapthing[currentPos[0]][currentPos[1]] = 4
                        except:
                            pass
                elif direct[0] == 'l':
                    for i in range(direct[1]):                
                        currentPos[1] -= 1
                        try:
                            mapthing[currentPos[0]][currentPos[1]] = 4
                        except:
                            pass
                else:
                    for i in range(direct[1]):                
                        currentPos[1] += 1
                        try:
                            mapthing[currentPos[0]][currentPos[1]] = 4
                        except:
                            pass
        #self.logr.info(self.mapArr)
        return mapthing
         
            
    def clear(self):
        self.mapArr = np.array([[0 for x in xrange(self.arrWidth)] for x in xrange(self.arrWidth)])
        self.mapArr[self.carPos][self.carPos] = 2
        self.mapArr[self.goal[0]][self.goal[1]] = 3
        
    def setGoal(self,x,y):
        self.mapArr[x][y] = 3
        self.goal = [x,y]
    
        
        
        
        
        

def prettyDirections(directions):
    print directions
    new = ""
    directions.insert(0,'')
    i = 1
    for n, direc in enumerate(directions):
        if n == 0:
            pass
        else:            
            if direc == directions[n-1]:
                i = i + 1
            else:
                new = new + (directions[n-1]+' x'+str(i)+', ')
                i = 1
    return new[5:]
        
class queue(object):

    def __init__(self, first, compass, length=2):
    
        self.logr = logging.getLogger('map.queue')
        self.nodes = []
        self.nodes.append((first, compass.getHeading()))
        self.compass = compass
        self.len = length
      
    
    def getLast(self):
        
        
        return self.nodes[-1][0]
        

        
    def take(self):
        if self.length() > 0:
            return self.nodes.pop()
        else:
            return None
    
    def put(self, node):
        
        self.nodes.append((tuple(node),self.compass.getHeading()))
        if len(self.nodes) >= self.len:
            self.nodes.pop(0)
        #print [x for x in self.nodes]
        #for n in xrange(len(self.nodes)-1, 0, -1):            
        #    self.nodes[n-1] = self.ajustAndCombine(self.nodes[n], deltaAngle)
        #self.nodes[-1] = node        
        
    def length(self):
        return len(self.nodes)
        
    def getCombined(self):
        
        outmap = copy.deepcopy(self.nodes[0][0])        
            
        
        for grid in self.nodes[1:]:
            if grid != None:
                for yn, y in enumerate(grid[0]):
                    for xn, x in enumerate(y):
                        if x == 1:
                            outmap[yn][xn] = 1
                        elif x == 3:
                            outmap[yn][xn] = 3
                        elif x == 2:
                            outmap[yn][xn] = 2
                            
        return outmap
    
    def ajustAndCombine(self, oldMap, angle):
        if angle != 0:
            newMap = scipy.ndimage.interpolation.rotate(input=oldMap, angle=math.degrees(angle), reshape=False, order=0)
        else:
            newMap = oldMap
        for yn, y in enumerate(oldMap):
            for xn, x in enumerate(y):
                if x == 1:
                    newMap[yn][xn] = 1        
        return newMap



if __name__ == "__main__":
    
    

    
    tinst = AreaMap({'steeringEngine':wheel}, 20)
    tinst.angleManager.changeSpeed(1.0)
    #tinst.initTestMap()
    #tinst.setPosition(50,50)
    #tinst.plot('right',90)
        
    tinst.plot('forward',200)
    
    tinst.prox(100)
    #pathfinder = ai.PathCalc()
    #result = pathfinder.calculateBestPath(tinst.x, tinst.y, tinst.mapArr)
    print 'waiting...'
    time.sleep(10)
    for thing in tinst.frameBuffer.nodes:
        print '..................'
        print thing
        
