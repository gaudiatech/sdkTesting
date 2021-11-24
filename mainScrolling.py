import pygame
import random

"""
 FORK of a work shared by Kyuchumimo#3941
 or maybe Blaatand29#0070 ?
 I don't really know who was the original author...

 shared via the pygame community discord server

 ---------------
  demo of a camera scrolling,
  just like particle systems this can
  can also pinpoint various performance issues
 ---------------
"""

# TODO:plz avoid numpy (->future katasdk compatibility)
import numpy as np


pygame.init()
pygame.display.set_caption("Camera example")

# scaledmode ?
# screen = pygame.display.set_mode([240,136],pygame.SCALED)

SCR_W,SCR_H = 640,480
screen =pygame.display.set_mode((SCR_W,SCR_H))

clock = pygame.time.Clock()

cam={"x":0, "y":0}
p={"x":120, "y":68}

info_font = pygame.font.Font(None, 16)

LIM_MAP_X,LIM_MAP_Y = 4*SCR_W,2*SCR_H
background = pygame.Surface((LIM_MAP_X, LIM_MAP_Y))
for _ in range(98877):
    background.set_at((random.randint(0,LIM_MAP_X-1),random.randint(0,LIM_MAP_Y-1)),'purple')

gameover = False

while not gameover:

    for ev in pygame.event.get():
        if ev.type==pygame.QUIT:
            gameover=True
        elif ev.type==pygame.KEYDOWN and ev.key==pygame.K_ESCAPE:
            gameover=True
    if pygame.key.get_pressed()[pygame.K_UP]:
        p['y']-=3
    elif pygame.key.get_pressed()[pygame.K_DOWN]:
        p['y']+=3
    elif pygame.key.get_pressed()[pygame.K_LEFT]:
        p['x']-=3
    elif pygame.key.get_pressed()[pygame.K_RIGHT]:
        p['x']+=3

    # TODO: plz re-implement this without using numpy!
    cam["x"]=np.clip((1-0.05)*cam["x"] + 0.05*((pygame.display.get_surface().get_size()[0]//2)-p["x"]),-(pygame.Surface.get_size(background)[0]-pygame.display.get_surface().get_size()[0]),0)
    cam["y"]=np.clip((1-0.05)*cam["y"] + 0.05*((pygame.display.get_surface().get_size()[1]//2)-p["y"]),-(pygame.Surface.get_size(background)[1]-pygame.display.get_surface().get_size()[1]),0)

    # display
    screen.fill([0,0,0])
    screen.blit(background,[cam['x'],cam['y']])
    pygame.draw.rect(screen,[255,255,255],[p['x']+cam['x'],p['y']+cam['y'],8,8])
    screen.blit(info_font.render("{}, {}".format(p['x'],p['y']),False,[255,255,255]),[0,0])
    screen.blit(info_font.render("{}, {}".format(cam['x'],cam['y']),False,[255,255,255]),[0,16])
    
    pygame.display.flip()
    clock.tick(60)


pygame.quit()
print('bye!')
