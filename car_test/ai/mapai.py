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

        self.mapArr = []
        
    #this takes the current known map and a goal location (tuple of x,y)
    #the goal location may be overloaded in the future to allow a relative goal instead of an absolute one
    #(for example, go 10 meters to the left of your current location)
    def calculateBestPath(self, x, y, currentMap):
    
        self.mapArr = currentMap
    
        #make something which keeps track of the possible paths
        q = queue(y,x)
        
        #set yourself as a blocked spot to avoid backtracking
        self.mapArr[y][x] = 1
        
        while q.length() != 0:
        
            #grab the next space to be tested
            current = q.take()
            cy = current[0][0]
            cx = current[0][1]
            path = current[1]
            
            
            #check each position around the current position to see if it is viable
            
            #up
            if (cy > 0) and (self.mapArr[cy-1][cx] != 1):
                                
                #make a new possibility for each direction
                possiblePath = list(path)
                
                #you have arrived, and found the best path.
                if self.mapArr[cy-1][cx] == 3:
                    
                    #don't forget to append the last move before returning
                    possiblePath.append('up')
                    return possiblePath
                    
                else:
                    #set the open space to a 'blocked' status. Ensures that no looping happens
                    self.mapArr[cy-1][cx] = 1
                    #set the current space as a path possibility. it will be checked in the next loop
                    possiblePath.append('up')
                    q.put([[cy-1,cx],possiblePath])
                
            #down
            if (cy+1 < len(self.mapArr)) and (self.mapArr[cy+1][cx] != 1):
               
                possiblePath = list(path)
                
                if self.mapArr[cy+1][cx] == 3:
                    
                    possiblePath.append('down')
                    return possiblePath
                    
                else:                    
                    self.mapArr[cy+1][cx] = 1
                    possiblePath.append('down')
                    q.put([[cy+1,cx],possiblePath])
                
            #left
            if (cx > 0) and (self.mapArr[cy][cx-1] != 1):
               
                possiblePath = list(path)
                
                if self.mapArr[cy][cx-1] == 3:
                   
                    possiblePath.append('left')
                    return possiblePath
                    
                else:                    
                    self.mapArr[cy][cx-1] = 1
                    possiblePath.append('left')
                    q.put([[cy,cx-1],possiblePath])
                
            #right
            if (cx+1 < len(self.mapArr[0])) and (self.mapArr[cy][cx+1] != 1):
                
                possiblePath = list(path)
                
                if self.mapArr[cy][cx+1] == 3:
                    
                    possiblePath.append('right')
                    return possiblePath
                    
                else:                    
                    self.mapArr[cy][cx+1] = 1
                    possiblePath.append('right')
                    q.put([[cy,cx+1],possiblePath])
        
        #if the program gets to this point without returning, it means that no path to the goal has been found
        return False


