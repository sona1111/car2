import pygame
  
pygame.init()
  
window = pygame.display.set_mode((800,600))
  
pygame.display.set_caption("Window")
  
black = (0,0,0)
white=(255,255,255)

  
x,y=0,0
print ("lets see")
moveX,moveY=0,0
  
clock = pygame.time.Clock()
  
gameLoop=True
while gameLoop:
    
  
    for event in pygame.event.get():

        if (event.type==pygame.QUIT):
  
            gameLoop=False
  
        if (event.type==pygame.KEYDOWN):
            print ("letfasdfasdfasdfasdfasdfasdfasdfasdfasdfasdfasdfasdfasdfasdfasdfasdfasdfasdfasdfasdf")
            if (event.key==pygame.K_LEFT):
                print ("letf")
                moveX = -5
  
            if (event.key==pygame.K_RIGHT):
                print ("right")
                moveX = 5
  
            if (event.key==pygame.K_UP):
                print ("up")
                moveY = -5
  
            if (event.key==pygame.K_DOWN):
                print ("down")  
                moveY = 5
  
        if (event.type==pygame.KEYUP):
  
            if (event.key==pygame.K_LEFT):

                moveX=0
  
            if (event.key==pygame.K_RIGHT):
  
                moveX=0
  
            if (event.key==pygame.K_UP):
  
                moveY=0
  
            if (event.key==pygame.K_DOWN):
  
                moveY=0
  
    #window.fill(black)
  
    x+=moveX
    y+=moveY
  
    #pygame.draw.rect(window,white,(x,y,50,50))
  
    clock.tick(50)
  
    #pygame.display.flip()
  
pygame.quit() 
