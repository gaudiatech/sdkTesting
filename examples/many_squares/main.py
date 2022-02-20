import katagames_sdk as katasdk
import random
katasdk.bootstrap(1)

kataen = katasdk.import_kengi()
pygame = kataen.pygame
doprojection = kataen.core.proj_to_vscreen


clock = screen = None
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
    col_a = pygame.colordict.THECOLORS['steelblue']
    col_b = pygame.colordict.THECOLORS['orange']
    omega_color_names = ['salmon', 'yellow', 'maroon4', 'lightsteelblue3', 'darkred', 'plum', 'paleturquoise']
    assoc_obj_position.clear()

    carres = [pygame.Surface((SQ_SIZE, SQ_SIZE)) for _ in range(16)]
    movables.clear()
    for elt in carres:
        elt.fill(pygame.color.THECOLORS[random.choice(omega_color_names)])

        if random.random() < 0.77:
            if random.random() < 0.5:
                pygame.draw.rect(elt, col_a, ((3, 5), (33, 15)), 0)
                tmptmp = pygame.surface.Surface((3, 127))
                tmptmp.fill('purple')
                elt.blit(tmptmp, (7 + random.randint(2, 13), random.randint(25, 40)))
                movables.add(elt)
            else:
                pygame.draw.circle(elt, col_b, (SQ_SIZE // 2, SQ_SIZE // 2), 21, 7)
        assoc_obj_position[elt] = (random.random() * (W - 64), random.random() * (H - 64))


@katasdk.web_entry_point
def i_init_soft():
    global gameover, screen, clock
    kataen.core.init('old_school')
    clock = pygame.time.Clock()
    screen = kataen.core.get_screen()
    gen_carres()
    gameover = False


@katasdk.web_animate
def i_update_loop(infot=None):
    global dragging, gameover, carres, assoc_obj_position

    for ev in pygame.event.get():
        if ev.type == pygame.QUIT:
            gameover = True
        elif ev.type == pygame.MOUSEBUTTONDOWN:
            for elt in carres:
                if elt in assoc_obj_position:
                    p = assoc_obj_position[elt]
                    if elt in movables:
                        mx, my = doprojection(ev.pos)
                        if p[0] < mx < p[0] + SQ_SIZE:
                            if p[1] < my < p[1] + SQ_SIZE:
                                # click
                                dragging = elt
                                break
        elif ev.type == pygame.MOUSEBUTTONUP:
            dragging = None
        elif ev.type == pygame.MOUSEMOTION:
            if dragging:
                mx, my = doprojection(ev.pos)
                assoc_obj_position[dragging] = (mx - SQ_SIZE // 2, my - SQ_SIZE // 2)
        elif ev.type == pygame.KEYDOWN:
            if ev.key == pygame.K_SPACE:
                gen_carres()
            elif ev.key == pygame.K_RETURN:
                print(' - ENTER PRESSED - ')
                return [2, 'main2']  # another game
        # - fin proc event

    # draw the bg
    screen.fill((77, 122, 80))
    for elt in carres:
        screen.blit(elt, assoc_obj_position[elt])
    kataen.core.display_update()

    clock.tick(60)


if __name__ == '__main__':
    i_init_soft()
    while not gameover:
        i_update_loop()
    kataen.core.cleanup()
