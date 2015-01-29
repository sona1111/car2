import numpy as np
import math
import ai



#handles mapping out the area (another object will keep track of the position)
class AreaMap(object):

    def __init__(self, x, y):
        
        #self.mapArr = np.zeros((10,10))
        
        #amount of square cm each array element represents
        self.arrWidth = 10
        
        self.x = self.scale(x)
        self.y = self.scale(y)
        
        
        
    def initTestMap(self):
    
        self.mapArr = np.array( [    [0,0,0,0,0,0,0,0,0,0],
                                     [0,0,0,0,0,0,0,0,0,0],
                                     [0,0,0,0,0,0,0,0,0,0],
                                     [0,0,0,0,0,0,0,0,0,0],
                                     [0,0,0,0,0,0,0,0,0,0],
                                     [0,1,1,0,0,0,0,0,0,0],
                                     [0,0,1,0,0,0,0,0,0,0],
                                     [0,0,1,1,0,0,0,0,0,0],
                                     [0,3,0,1,1,1,0,0,0,0],
                                     [0,0,0,0,0,0,0,0,0,0]] )
        
    
    #return a map of the immediate area only
    #value of r is currently in array unit scale, not CM
    def prox(self, r):
    
        #the MAX builtin is required to make sure no negative array indicies are requested

        print self.mapArr[(max(0,self.y-r)):(self.y+r),(max(0,self.x-r)):(self.x+r)]
        
    #update the car's current position on the map
    def setPosition(self, x, y):
    
        self.x = self.scale(x)
        self.y = self.scale(y)
    
        #nifty feature from numpy. Find and remove the existing position
        self.mapArr[self.mapArr == 2] = 0
        self.mapArr[self.y][self.x] = 2
        
        
    #convert any units the car provides into units based on the map array
    def scale(self, val):
    
        out = int((float(val)/float(self.arrWidth)))
        return out
    
    #this function adds a known obstacle to the map array
    #this assumes we have 4 sensors on the car
    #the cardinal specifies the direction of the sensor as a string, "left", "right", "forward", or "backward"
    #direction finds the current rotation of the vehicle (in degrees), which should be kept track of by the position object
    #this assumes that the default direction of the car when it begins moving is looking DOWN the array. 
    #distance is the raw reading from the sensor
    def plot(self, cardinal, direction, distance):
        
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
            self.mapArr[self.y+cy][self.x+cx] = 1
        except:
            print "plot was outside of array range"
        
    
        
        
        
        
        

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
        
tinst = AreaMap(0,0)
tinst.initTestMap()
tinst.setPosition(50,50)
tinst.plot('right',-45,30)
tinst.prox(5)
pathfinder = ai.PathCalc()
result = pathfinder.calculateBestPath(tinst.x, tinst.y, tinst.mapArr)
'''
tinst.prox(3)
result = tinst.calculateBestPath()
'''
print "--------------------------------------------------------"
print result
print "--------------------------------------------------------"

#tinst.setPosition(50,50)
#print tinst.mapArr
#tinst.prox(3)



