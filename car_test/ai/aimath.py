import math

'''
This class takes constant input from sensors and check to see if the values are generally increasing or decreasing over time.
'''
class SlopeMonitor(object):

    def __init__(self, n):
        self.valArr = []
        self.n = n
    
    def addVal(self, val):
    
        self.valArr.insert(0,val)
        
        if len(self.valArr) >= self.n:
            self.valArr.pop()
            
    #should return either '+' or '-' to indicate that the values in the array are increasing or decreasing, or None if uneven. 
    #random outliars should be handled at the hardware level, so if the input here is not constantly decreasing or increasing monotonically, we will assume that the sensor has not yet set it's sights on the offending object (possibly turn has only been going for about 10 degrees)
    #XXX in the future we can use least squares regression
    def get(self):
    
        #check if decreasing
        if (all(x>y for x, y in zip(self.valArr, self.valArr[1:])) == True):
            return '-'
        
        #check if increasing
        elif (all(x<y for x, y in zip(self.valArr, self.valArr[1:])) == True):
            return '+'
            
        else:
            return None
        
    def reset(self):
        self.valArr = []
        
class GenericCounter(object):

    def __init__(self, n, nmax = float('inf'), nmin = float('-inf')):
        self.n = n
        self.nmax = nmax
        self.nmin = nmin
        self.is_set = False
        
    def setup(self, n, nmax = float('inf'), nmin = float('-inf')):
        self.n = n
        self.nmax = nmax
        self.nmin = nmin
        self.is_set = True
    
    def inc(self):
        self.n += 1
        if self.n >= self.nmax:
            self.is_set = False
            return False
        else:
            return True
        
    def dec(self):
        self.n -= 1
        if self.n <= self.nmin:
            self.is_set = False
            return False
        else:
            return True
