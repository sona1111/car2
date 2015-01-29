import pygame
import time
import numpy as np

class LineObject(object):

    def __init__(self, p1, p2):
        
        self.p1 = p1
        self.p2 = p2
        
    def getPoints(self):
        return (self.p1,self.p2,)






# Return true if line segments AB and CD intersect
# expects to receive two line objects
def intersect(l1,l2):


    def ccw(A,B,C):
        return (C[1]-A[1]) * (B[0]-A[0]) > (B[1]-A[1]) * (C[0]-A[0])
    
    return ccw(l1.p1,l2.p1,l2.p2) != ccw(l1.p2,l2.p1,l2.p2) and ccw(l1.p1,l1.p2,l2.p1) != ccw(l1.p1,l1.p2,l2.p2)
    




l1 = LineObject((50,50,),(100,100,))
l2 = LineObject((70,50,),(200,200,))

class MainScreen(object):

    def __init__(self):
    
        width = 400
        height = 400
        self.screen = pygame.display.set_mode((width, height))
        self.screen.set_at((50, 50), (20, 255, 20))
        #pygame.display.flip()
        
        
        
    def clear(self):
        self.screen.fill((0,0,0))
        
    def draw(self, thing):
    
        if thing.__class__.__name__ == "LineObject":

            pygame.draw.line(self.screen, (255, 255, 255), *thing.getPoints())
            pygame.display.flip()
        #pygame.draw.line(screen, (255, 255, 255), *l1.getPoints())
        #pygame.draw.line(screen, (255, 255, 255), *l2.getPoints())



print "intersect", intersect(l1, l2)

class Map(object):

    def __init__(self):
        
        self.x = 0
        self.y = 0
        
    def prox(r):
        pass
        

scr = MainScreen()
scr.draw(l1)

time.sleep(4)

#this might be used if we need to find the intersect point
'''
def line_intersection(line1, line2):
    xdiff = (line1[0][0] - line1[1][0], line2[0][0] - line2[1][0])
    ydiff = (line1[0][1] - line2[1][1], line2[0][1] - line2[1][1])

    def det(a, b):
        return a[0] * b[1] - a[1] * b[0]

    div = det(xdiff, ydiff)
    if div == 0:
       raise Exception('lines do not intersect')

    d = (det(*line1), det(*line2))
    x = det(d, xdiff) / div
    y = det(d, ydiff) / div
    return x, y
'''


    
