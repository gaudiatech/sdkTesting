# contact: thomas@gaudia-tech.com
# thema for this gist= INFINITY

# demo tested with libraries:
# katasdk 0.0.5 & python3.8.10

# "pip install katasdk" if needed

from math import cos, sin, pi
import katagames_sdk as katasdk

kataen = katasdk.engine

EventReceiver = kataen.EventReceiver
EngineEvTypes = kataen.EngineEvTypes

pygame = kataen.import_pygame()

# constants
MAX_FPS = 65
N_PIX = 8
BG_COLOR_DESC = 'lightblue'

# glvars
bg_color = None
scr_size = [0, 0]


class Player:
    """models a moving player representation that can move left or right"""
    BASECOLOR = pygame.Color('darkred')
    SIZE = 16

    def __init__(self, x_init, y_init, ref_terrain):
        self.vx, self.vy = 0., 0.
        self.x, self.y = float(x_init), float(y_init)
        self.color = Player.BASECOLOR
        self.moving_left = self.moving_right = False
        self.stuck = False
        self.terrain = ref_terrain

    def push_right(self):
        self.moving_right = True

    def push_left(self):
        self.moving_left = True

    def freeze(self):
        if self.moving_right:
            self.moving_right = False
        if self.moving_left:
            self.moving_left = False
        self.terrain.scrolling_stop()

    def update(self):
        global scr_size
        if not (self.moving_right or self.moving_left):
            self.vx = 0.
        else:
            if self.moving_right:
                self.vx = float(N_PIX)
            if self.moving_left:
                self.vx = -float(N_PIX)

        if self.x + self.vx > (2. / 3) * scr_size[0]:
            if not self.terrain.is_scrolling():
                self.terrain.scroll_left()  # scroll in the inverse direction of player mov. to make it happen
            self.stuck = True
        elif self.x + self.vx < (1. / 3) * scr_size[0]:
            if not self.terrain.is_scrolling():
                self.terrain.scroll_right()
            self.stuck = True
        else:
            self.stuck = False

        if not self.stuck:
            self.x += self.vx
        self.y = int(scr_size[1] - self.terrain.l_heights[int(self.x)] - Player.SIZE)

    def draw(self, surface):
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), Player.SIZE, 0)  # width is req. for katasdk0.0.5


class Terrain:
    def __init__(self):
        global scr_size
        self.dist = 0

        # the magic (terrain-gen) is done by this function
        self.height_func = lambda x: 228 + 128 * cos(0.0002 * x) + 32 * sin(0.01 * x) + 64 * sin(
            pi / 800 * x) + 16 * abs(sin(0.02 * x + (pi / 2)))

        self.l_heights = list()
        for i in range(scr_size[0]):
            self.l_heights.append(self.height_func(i))
        self.color = pygame.Color('darkgreen')
        self.moving_right = self.moving_left = False

    def is_scrolling(self):
        return self.moving_right or self.moving_left

    def scroll_right(self):
        self.moving_right = True

    def scroll_left(self):
        self.moving_left = True

    def scrolling_stop(self):
        self.moving_left = self.moving_right = False

    def update(self):
        global scr_size
        # refresh terrain heights
        if self.moving_right:
            for i in range(N_PIX):
                self.dist -= 1
                self.l_heights.pop()
                self.l_heights.insert(0, self.height_func(self.dist))

        elif self.moving_left:
            for i in range(N_PIX):
                self.dist += 1
                self.l_heights.pop(0)
                self.l_heights.append(self.height_func(self.dist + scr_size[0] - 1))

    def draw(self, surface):
        h = surface.get_size()[1]
        for ind in range(len(self.l_heights)):
            h_val = self.l_heights[ind]
            p1 = (ind, h - 1)
            p2 = (ind, h - 1 - h_val)
            pygame.draw.line(surface, self.color, p1, p2)

class GameManager(EventReceiver):
    def __init__(self, pl_obj, terrain):
        super().__init__()
        self.pl_obj = pl_obj
        self.terrain = terrain
        
    def proc_event(self, ev, source):
        global bg_color
        if ev.type == EngineEvTypes.LOGICUPDATE:  # game logic
            self.pl_obj.update()
            self.terrain.update()
            
        elif ev.type == EngineEvTypes.PAINT:  # gfx rendering
            ev.screen.fill(bg_color)
            self.terrain.draw(ev.screen)
            self.pl_obj.draw(ev.screen)
            
        elif ev.type == pygame.KEYDOWN:  # events
            if ev.key == pygame.K_RIGHT:
                self.pl_obj.push_right()
            elif ev.key == pygame.K_LEFT:
                self.pl_obj.push_left()
        elif ev.type == pygame.KEYUP:
            if ev.key in (pygame.K_RIGHT, pygame.K_LEFT):
                self.pl_obj.freeze()


def run_game():
    global scr_size, bg_color
    kataen.init(kataen.HD_MODE)
    scr_size = kataen.get_screen().get_size()

    bg_color = pygame.Color(BG_COLOR_DESC)
    terrain = Terrain()
    pl_obj = Player(scr_size[0] // 2, scr_size[1]//2, terrain)
    
    m = GameManager(pl_obj, terrain)
    gctrl = kataen.get_game_ctrl()
    m.turn_on()
    gctrl.turn_on()

    gctrl.loop()
    kataen.cleanup()

if __name__=='__main__':
    run_game()
