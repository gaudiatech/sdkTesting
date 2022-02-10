import random
import katagames_sdk as katasdk

if katasdk.VERSION == '0.0.6':
    import katagames_sdk.engine as kataen
    pygame = kataen.import_pygame()
else:
    kataen = katasdk.engine
    pygame = kataen.pygame

"""
--- --- ---
retro-compatibility support of this test:

         0.0.6    0.0.7
      --- --- --- --- -
local |   Y   |   Y    |
      |       |        |
      --- --- --- --- -
 web  |   Y   |   Y    |
      |       |        |
      --- --- --- --- -
"""

# const
INCREM = 3
MAXFPS = 60
SCR_W = 940//2
SCR_H = 540//2

# declare
delta_x = 0
gameover = None
txtsurf=None
txt_pos=None
clock=None
screen = None


def reroll_static_char():
    global txtsurf2
    tmp_font = pygame.font.Font(None, 44)
    txtsurf2 = tmp_font.render(chr(random.randint(97,122)),True, (87,77,115))


def _i_game_init():
    global gameover,clock,txt_pos,txtsurf, txtsurf2, screen
    gameover = False
    
    #pygame.init()
    katasdk.engine.init(kataen.OLD_SCHOOL_MODE)
    clock = pygame.time.Clock()
    
    pygame.font.init()
    tmp_font = pygame.font.Font(None, 25)

    #screen = pygame.display.set_mode((SCR_W,SCR_H))
    screen=kataen.get_screen()
    txt_pos = pygame.math.Vector2()
    txt_pos.x += SCR_W//2
    txt_pos.y += SCR_H//3
    txtsurf = tmp_font.render('X0é-hi-man', False, pygame.Color('#e9abcc'), 'navyblue')
    reroll_static_char()
    print('press LEFT/RIGHT key, or SPACE to change txt position')


def _i_game_update(infot=None):
    global delta_x, screen, txt_pos, txtsurf, gameover, txtsurf2

    for ev in pygame.event.get():
        if ev.type == pygame.QUIT:
            gameover = True
        elif ev.type == pygame.KEYDOWN:
            if ev.key == pygame.K_RIGHT:
                delta_x = INCREM
            elif ev.key == pygame.K_LEFT:
                delta_x = -1*INCREM
            elif ev.key == pygame.K_SPACE:
                reroll_static_char()
                txt_pos = pygame.math.Vector2()
                txt_pos.x = random.randrange(0,SCR_W-txtsurf.get_size()[0]-1)
                txt_pos.y = random.randrange(0,SCR_H-txtsurf.get_size()[0]-1)
        elif ev.type == pygame.KEYUP:
            delta_x = 0
        
    #update positions
    txt_pos.x += delta_x

    #update screen
    screen.fill(pygame.Color('pink'))
    screen.blit(txtsurf2, (SCR_W//2-txtsurf2.get_size()[0]//2, 99))
    
    pygame.draw.polygon(screen,'red',[
        (-2+txt_pos.x - txtsurf.get_size()[0]//2,-1+txt_pos.y - txtsurf.get_size()[1]//2),
        (+2+txt_pos.x + txtsurf.get_size()[0]//2,-1+txt_pos.y - txtsurf.get_size()[1]//2),
        (+2+txt_pos.x + txtsurf.get_size()[0]//2,+1+txt_pos.y + txtsurf.get_size()[1]//2),
        (-2+txt_pos.x - txtsurf.get_size()[0]//2,+1+txt_pos.y + txtsurf.get_size()[1]//2),
        ], 2)
                        
    screen.blit(txtsurf, (txt_pos.x - txtsurf.get_size()[0]//2,txt_pos.y - txtsurf.get_size()[1]//2))
    
    #pygame.display.flip()
    if katasdk.VERSION == '0.0.6':
        kataen.gfx_updater.display_update()
    else:
        kataen.display_update()

    clock.tick(MAXFPS)


if __name__ == '__main__':
    _i_game_init()
    while not gameover:
        _i_game_update() 
    pygame.quit()
    print('bye')


if kataen.runs_in_web():
    if katasdk.version == '0.0.6':
        def run_game():
            pt_obj = ParticleSystemTester()
            pt_obj.start()
    else:
        @katasdk.web_entry_point
        def game_init():
            _i_game_init()
        @katasdk.web_animate
        def game_update(infot=None):
            _i_game_update(infot)
