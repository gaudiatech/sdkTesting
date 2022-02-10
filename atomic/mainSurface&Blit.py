import random
import katagames_sdk as katasdk


"""
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

if katasdk.VERSION == '0.0.6':
    import katagames_sdk.engine as kataen

    pygame = kataen.import_pygame()
else:
    kataen = katasdk.engine
    pygame = kataen.pygame


THECOLORS = pygame.colordict.THECOLORS
print("welcome!\nPress space to regen squares, mouse to drag n drop some of em")
clock = pygame.time.Clock()
kataen.init(kataen.OLD_SCHOOL_MODE)
screen = kataen.get_screen()
W, H = 960 // 2, 540 // 2
carres = list()
assoc_obj_position = dict()
dragging = None
movables = set()
SQ_SIZE = 64
gameover = None


def gen_carres():
    global carres, assoc_obj_position, movables, dragging
    dragging = None
    col_a = THECOLORS['steelblue']
    col_b = THECOLORS['orange']
    omega_color_names = ['salmon', 'yellow', 'maroon4', 'lightsteelblue3', 'darkred', 'plum', 'paleturquoise']

    carres = [pygame.Surface((SQ_SIZE, SQ_SIZE)) for _ in range(16)]
    movables.clear()
    for elt in carres:
        elt.fill(THECOLORS[random.choice(omega_color_names)])

        if random.random() < 0.77:
            if random.random() < 0.5:
                pygame.draw.rect(elt, col_a, ((3, 5), (33, 15)), 0)
                tmptmp = pygame.surface.Surface((3, 127))
                tmptmp.fill('purple')
                elt.blit(tmptmp, (7 + random.randint(2, 13), random.randint(25, 40)))
                movables.add(elt)
            else:
                pygame.draw.circle(elt, col_b, (SQ_SIZE // 2, SQ_SIZE // 2), 21, 7)


def _i_init_soft():
    global gameover
    gen_carres()
    gameover = False


def _i_update_loop(infot=None):
    global dragging, gameover, carres, assoc_obj_position

    for ev in pygame.event.get():
        if ev.type == pygame.QUIT:
            gameover = True
        elif ev.type == pygame.MOUSEBUTTONDOWN:
            for elt in carres:
                if elt in assoc_obj_position:
                    p = assoc_obj_position[elt]
                    if elt in movables:
                        mx, my = kataen.proj_to_vscreen(ev.pos)
                        if p[0] < mx < p[0] + SQ_SIZE:
                            if p[1] < my < p[1] + SQ_SIZE:
                                # click
                                dragging = elt
                                break
        elif ev.type == pygame.MOUSEBUTTONUP:
            dragging = None
        elif ev.type == pygame.MOUSEMOTION:
            if dragging:
                mx, my = kataen.proj_to_vscreen(ev.pos)
                assoc_obj_position[dragging] = (mx - SQ_SIZE // 2, my - SQ_SIZE // 2)
        elif ev.type == pygame.KEYDOWN:
            if ev.key == pygame.K_SPACE:
                gen_carres()

        # draw the bg
        screen.fill((77, 122, 80))

        for elt in carres:
            if elt in assoc_obj_position:
                pos = assoc_obj_position[elt]
            else:
                pos = (random.random() * (W - 64), random.random() * (H - 64))
                assoc_obj_position[elt] = pos

            screen.blit(elt, pos)

        # pygame.display.flip()
        if katasdk.VERSION == '0.0.6':
            kataen.gfx_updater.display_update()
        else:
            kataen.display_update()

        clock.tick(60)


if __name__ == '__main__':
    _i_init_soft()
    while not gameover:
        _i_update_loop()
    kataen.cleanup()

# /!\ will not run in web ctx for katasdk v0.0.6
if kataen.runs_in_web():
    @katasdk.web_entry_point
    def game_init():
        _i_init_soft()


    @katasdk.web_animate
    def game_update(infot=None):
        _i_update_loop(infot)
