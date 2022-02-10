import random
import katagames_sdk as katasdk



if katasdk.VERSION == '0.0.6':
    import katagames_sdk.engine as kataen
    pygame = kataen.import_pygame()
else:
    kataen = katasdk.engine
    pygame = kataen.pygame

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
    Modifications by wkta-tom

--- --- ---
retro-compatibility support of this test:

         0.0.6    0.0.7
      --- --- --- --- -
local |   y   |   Y    |
      |       |        |
      --- --- --- --- -
 web  |   N   |   Y    |
      |       |        |
      --- --- --- --- -
"""


SCR_W,SCR_H, LIM_MAP_X, LIM_MAP_Y= None,None,None,None
screen = None
info_ft, background = None, None
gameover = False
clock=None
cam, p = None,None


def _i_init_game():
    global SCR_W,SCR_H,screen,info_ft,LIM_MAP_X,LIM_MAP_Y,background,clock,cam,p
    
    kataen.init(kataen.OLD_SCHOOL_MODE)
    screen = kataen.get_screen()
    SCR_W,SCR_H = screen.get_size()
    info_ft = pygame.font.Font(None, 16)
    LIM_MAP_X,LIM_MAP_Y = 4*SCR_W,2*SCR_H
    background = pygame.Surface((LIM_MAP_X, LIM_MAP_Y))
    for _ in range(98877):
        background.set_at((random.randint(0,LIM_MAP_X-1),random.randint(0,LIM_MAP_Y-1)),'purple')

    clock = pygame.time.Clock()
    cam={"x":0, "y":0}
    p={"x":120, "y":68}


def pynative_clip(x, a, b):
    if a > b:
        binf, bsup = b, a
    else:
        binf, bsup = a, b
    if x < binf:
        return binf
    if x > bsup:
        return bsup
    return x


def _i_update_game(info_t=None):
    global gameover,info_ft,SCR_W,SCR_H

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

    # logic update,
    # has been re-implemented without using numpy...
    
    a = (1-0.05)*cam["x"] + 0.05*((SCR_W//2)-p["x"])
    themin = -(pygame.Surface.get_size(background)[0]-SCR_W)
    cam["x"]=pynative_clip(a, themin, 0)
    ##    cam["x"]=numpy.clip(
    ##        (1-0.05)*cam["x"] + 0.05*((//2)-p["x"]),
    ##        -(pygame.Surface.get_size(background)[0]-pygame.display.get_surface().get_size()[0]),
    ##        0
    ##    )
    a = (1-0.05)*cam["y"] + 0.05*((SCR_H//2)-p["y"])
    themin = -(pygame.Surface.get_size(background)[1]-SCR_H)
    cam["y"]=pynative_clip(a, themin, 0)

    # display
    screen.fill([0,0,0])
    screen.blit(background,[cam['x'],cam['y']])
    pygame.draw.rect(
        screen,pygame.Color('orange'),
        [p['x']+cam['x'],p['y']+cam['y'],8,8]
    )
    screen.blit(info_ft.render("{}, {}".format(p['x'],p['y']),False,[255,255,255]),[0,0])
    screen.blit(info_ft.render("{}, {}".format(cam['x'],cam['y']),False,[255,255,255]),[0,16])
    
    # pygame.display.flip()
    if katasdk.VERSION == '0.0.6':
        kataen.gfx_updater.display_update()
    else:
        kataen.display_update()
    clock.tick(60)


# -- entry pt for local execution
if __name__ == '__main__':
    _i_init_game()
    gameover=False
    while not gameover:
        _i_update_game()
    kataen.cleanup()
    print('bye!')


# /!\ will not run in web ctx for katasdk v0.0.6
if kataen.runs_in_web():
    @katasdk.web_entry_point
    def game_init():
        _i_init_game()
    @katasdk.web_animate
    def game_update(infot=None):
        _i_update_game(infot)

