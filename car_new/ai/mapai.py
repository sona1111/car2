import copy
import logging
logr = logging.getLogger('car.mapai')

#compile similar directions into a shorter series of instructions
def compact(path):    
    commandList = []
    path.insert(0,'')
    path.append('')
    
    i = 1
    for n, direc in enumerate(path):
        if n == 0:
            pass
        else:            
            if direc == path[n-1]:
                i = i + 1
            else:
                commandList.append((path[n-1],i))
                i = 1
    commandList.pop(0)
    return commandList


class queue(object):

    def __init__(self, y, x):
    
        self.nodes = [[[y,x],[]]]
        
    def take(self):
        return self.nodes.pop()
    
    def put(self, node):
        #very important to put the element at the beginning of the list here, not append
        self.nodes.insert(0,node)
        
    def length(self):
        return len(self.nodes)

class PathCalc(object):

    def __init__(self):

        currentMap = []
        
    #this takes the current known map and a goal location (tuple of x,y)
    #the goal location may be overloaded in the future to allow a relative goal instead of an absolute one
    #(for example, go 10 meters to the left of your current location)
    def calculateBestPath(self, x, y, currentMap):
    
        #print currentMap
    
        #make something which keeps track of the possible paths
        q = queue(y,x)
        
        #set yourself as a blocked spot to avoid backtracking
        currentMap[y][x] = 1
        
        while q.length() != 0:
        
            #grab the next space to be tested
            current = q.take()
            cy = current[0][0]
            cx = current[0][1]
            path = current[1]
            
            
            #check each position around the current position to see if it is viable
            
            #up
            if (cy > 0) and (currentMap[cy-1][cx] != 1):
                                
                #make a new possibility for each direction
                possiblePath = list(path)
                
                #you have arrived, and found the best path.
                if currentMap[cy-1][cx] == 3:
                    
                    #don't forget to append the last move before returning
                    #possiblePath.append('f')
                    return compact(possiblePath)
                    
                else:
                    #set the open space to a 'blocked' status. Ensures that no looping happens
                    currentMap[cy-1][cx] = 1
                    #set the current space as a path possibility. it will be checked in the next loop
                    possiblePath.append('f')
                    q.put([[cy-1,cx],possiblePath])
                
            #down
            if (cy+1 < len(currentMap)) and (currentMap[cy+1][cx] != 1):
               
                possiblePath = list(path)
                
                if currentMap[cy+1][cx] == 3:
                    
                    #possiblePath.append('b')
                    return compact(possiblePath)
                    
                else:                    
                    currentMap[cy+1][cx] = 1
                    possiblePath.append('b')
                    q.put([[cy+1,cx],possiblePath])
                
            #left
            if (cx > 0) and (currentMap[cy][cx-1] != 1):
               
                possiblePath = list(path)
                
                if currentMap[cy][cx-1] == 3:
                   
                    #possiblePath.append('l')
                    return compact(possiblePath)
                    
                else:                    
                    currentMap[cy][cx-1] = 1
                    possiblePath.append('l')
                    q.put([[cy,cx-1],possiblePath])
                
            #right
            if (cx+1 < len(currentMap[0])) and (currentMap[cy][cx+1] != 1):
                
                possiblePath = list(path)
                
                if currentMap[cy][cx+1] == 3:
                    
                    #possiblePath.append('r')
                    return compact(possiblePath)
                    
                else:                    
                    currentMap[cy][cx+1] = 1
                    possiblePath.append('r')
                    q.put([[cy,cx+1],possiblePath])
        
        #if the program gets to this point without returning, it means that no path to the goal has been found
        return False


if __name__ == "__main__":

    mapArr =[[0,0,0,0,0,0,0,0,0,0],
             [0,0,0,0,0,0,0,0,0,0],
             [0,0,0,0,0,0,0,0,0,0],
             [0,0,0,0,0,0,0,0,0,0],
             [0,0,0,0,0,0,0,0,0,0],
             [0,1,1,0,0,0,0,0,0,0],
             [0,0,1,0,0,0,0,0,0,0],
             [0,0,1,1,0,0,0,0,0,0],
             [0,3,0,1,1,1,0,0,0,0],
             [0,0,0,0,0,0,0,0,0,0]] 
    p = PathCalc()
    print p.calculateBestPath(5,5,mapArr)
    
    

