# TECH-DEMO1.py | revision: oct.07 - 2021
# showcases how the Kata engine works
# (tested with v0.0.6)

# Visit https://kata.games to learn more!
# source-code by "wkta-tom" | MIT License

# https://github.com/wkta
# thomas@gaudia-tech.com

import math
import random
import katagames_sdk as katasdk

kataen= katasdk.engine

pygame = kataen.pygame
# or pygame = kataen.import_pygame()

MyEvTypes = kataen.enum_for_custom_event_types(
    'PlayerChanges',  # contains: newx, newy, angle
)
Vector2 = pygame.math.Vector2
CogObject = kataen.CogObject
EventReceiver = kataen.EventReceiver
EngineEvTypes = kataen.EngineEvTypes
CgmEvent = kataen.CgmEvent


def deg(radvalue):
    return radvalue * (180 / math.pi)


class RocksModel:
    INIT_NB = 7

    def __init__(self):
        self.contents = list()
        self.scr_size = kataen.get_screen().get_size()
        for i in range(self.INIT_NB):
            rand_pos = [random.randint(0, self.scr_size[0] - 1), random.randint(0, self.scr_size[1] - 1)]
            rand_size = random.randint(8, 55)
            rand_angle = random.uniform(0, 2 * math.pi)
            rand_speed_val = random.uniform(4, 32)
            speedvect = Vector2()
            speedvect.from_polar((1, deg(rand_angle)))
            speedvect *= rand_speed_val
            self.contents.append(
                [rand_pos, rand_size, speedvect]
            )

    @staticmethod
    def _adjust_for_torus(coordx, coordy, scr_size):
        resx, resy = coordx, coordy
        if coordx < 0:
            resx = coordx + scr_size[0]
        elif coordx >= scr_size[0]:
            resx = coordx - scr_size[0]
        if coordy < 0:
            resy = coordy + scr_size[1]
        elif coordy >= scr_size[1]:
            resy = coordy - scr_size[1]
        return resx, resy

    def update(self, time_elapsed):
        for i in range(len(self.contents)):
            speedvect = self.contents[i][2]
            self.contents[i][0][0] += time_elapsed * speedvect.x
            self.contents[i][0][1] += time_elapsed * speedvect.y
            self.contents[i][0][0], self.contents[i][0][1] = RocksModel._adjust_for_torus(
                self.contents[i][0][0], self.contents[i][0][1], self.scr_size
            )


class ShipModel(CogObject):
    DASH_DISTANCE = 55
    DELTA_ANGLE = 0.04
    SPEED_CAP = 192

    def __init__(self):
        super().__init__(explicit_id=1)
        self.scr_size = kataen.get_screen().get_size()
        rand_pos = (random.randint(0, self.scr_size[0] - 1), random.randint(0, self.scr_size[1] - 1))
        self._position = Vector2(*rand_pos)
        self._angle = 0
        self._speed = Vector2()

    def _commit_new_pos(self):
        tmpsize = self.scr_size
        if self._position.x < 0:
            self._position.x += tmpsize[0]
        elif self._position.x >= tmpsize[0]:
            self._position.x -= tmpsize[0]
        if self._position.y < 0:
            self._position.y += tmpsize[1]
        elif self._position.y >= tmpsize[1]:
            self._position.y -= tmpsize[1]
        self.pev(MyEvTypes.PlayerChanges, newx=self._position.x, newy=self._position.y, angle=self._angle)

    def _update_speed_vect(self):
        lg = self._speed.length()
        self._speed = Vector2()
        self._speed.from_polar((lg, deg(self._angle)))

    def ccw_rotate(self):
        self._angle -= self.__class__.DELTA_ANGLE
        self._update_speed_vect()

    def cw_rotate(self):
        self._angle += self.__class__.DELTA_ANGLE
        self._update_speed_vect()

    def get_orientation(self):
        return self._angle

    def accel(self):
        if self._speed.length() == 0:
            self._speed = Vector2()
            self._speed.from_polar((5, deg(self._angle)))
        else:
            speedv_now = self._speed.length()
            speedv_now += 1
            if speedv_now > self.SPEED_CAP:
                speedv_now = self.SPEED_CAP
            self._speed = Vector2()
            self._speed.from_polar((speedv_now, deg(self._angle)))

    def brake(self):
        speedv_now = self._speed.length()
        speedv_now = speedv_now * 0.96
        if speedv_now < 5:
            self._speed = Vector2()
        else:
            self._speed = Vector2()
            self._speed.from_polar((speedv_now, deg(self._angle)))

    def get_position(self):
        return self._position

    def get_scr_pos(self):
        return int(self._position.x), int(self._position.y)

    def set_position(self, new_pos):
        self._position.x, self._position.y = new_pos
        self._commit_new_pos()

    def update(self, temps_passe):
        self._position.x += temps_passe * self._speed.x
        self._position.y += temps_passe * self._speed.y
        self._commit_new_pos()

    def dash(self):
        tmp = Vector2()
        tmp.from_polar((self.DASH_DISTANCE, deg(self._angle)))
        self._position += tmp
        self._commit_new_pos()


class ShipCtrl(EventReceiver):
    def __init__(self, ref_mod, rocksm):
        super().__init__()
        self._ref_ship = ref_mod
        self._ref_rocks = rocksm
        self.last_tick = None

    def proc_event(self, ev, source):
        if ev.type == EngineEvTypes.LOGICUPDATE:
            ba = pygame.key.get_pressed()
            if ba[pygame.K_UP]:
                self._ref_ship.accel()
            if ba[pygame.K_DOWN]:
                self._ref_ship.brake()
            if ba[pygame.K_RIGHT]:
                self._ref_ship.cw_rotate()
            if ba[pygame.K_LEFT]:
                self._ref_ship.ccw_rotate()
            if self.last_tick:
                tmp = ev.curr_t - self.last_tick
            else:
                tmp = 0
            self.last_tick = ev.curr_t
            self._ref_ship.update(tmp)
            self._ref_rocks.update(tmp)
        elif ev.type == pygame.KEYDOWN:
            if ev.key == pygame.K_SPACE:
                self._ref_ship.dash()


class TinyWorldView(EventReceiver):
    RAD = 5
    BG_COLOR = (16, 4, 43)
    LINE_COLOR = (119, 255, 0)

    def __init__(self, ref_mod, rocksm):
        super().__init__()
        self.curr_pos = ref_mod.get_scr_pos()
        self.curr_angle = ref_mod.get_orientation()
        self.ref_rocksm = rocksm

    def proc_event(self, ev, source):
        if ev.type == EngineEvTypes.PAINT:
            ev.screen.fill(self.BG_COLOR)
            self._draw_player(ev.screen)
            self._draw_rocks(ev.screen)
        elif ev.type == MyEvTypes.PlayerChanges:
            self.curr_angle = ev.angle
            self.curr_pos = Vector2(ev.newx, ev.newy)

    def _draw_rocks(self, refscreen):
        for rockinfo in self.ref_rocksm.contents:
            pos = (int(rockinfo[0][0]), int(rockinfo[0][1]))
            size = rockinfo[1]
            pygame.draw.circle(refscreen, self.LINE_COLOR, pos, size, 2)

    def _draw_player(self, surface):
        
        orientation = -self.curr_angle
        pt_central = self.curr_pos
        a, b, c = Vector2(), Vector2(), Vector2()
        a.from_polar((1, deg(orientation - (2.0 * math.pi / 3))))
        b.from_polar((1, deg(orientation)))
        c.from_polar((1, deg(orientation + (2.0 * math.pi / 3))))
        temp = [a, b, c]
        
        for tv in temp:
            tv.y *= -1
        temp[0] = (1.2 * self.RAD) *temp[0]
        temp[1] = (3 * self.RAD) *temp[1]
        temp[2] = (1.2 * self.RAD) *temp[2]
        pt_li = [Vector2(*pt_central),
                 Vector2(*pt_central),
                 Vector2(*pt_central)]
        for i in range(3):
            pt_li[i] += temp[i]
        for pt in pt_li:
            pt.x = round(pt.x)
            pt.y = round(pt.y)
        
        
        # fix ds 0.0.7 TODO
        pt_li.reverse()
        pygame.draw.polygon(surface, self.LINE_COLOR, pt_li, 2)

        # fix ds 0.0.7 TODO
        #pygame.draw.rect(surface, self.LINE_COLOR, (tuple(temp[0]), (8,8)), 0)
        
        #pygame.draw.rect(surface, pygame.Color(self.LINE_COLOR), (tuple(pt_li[0]),(8,8)), 0 )
        

def print_mini_tutorial():
    howto_infos = """HOW TO PLAY:
    * use arrows to move
    * use SPACE to use a wormhole!"""
    print('-' * 32)
    for line in howto_infos.split('\n'):
        print(line)
    print('-' * 32)


def run_game():
    kataen.init(kataen.OLD_SCHOOL_MODE)
    # MVC architecture rocks
    model_objs = [ShipModel(), RocksModel()]
    li_recv = [
        TinyWorldView(*model_objs),
        ShipCtrl(*model_objs),
        kataen.get_game_ctrl()
    ]
    for recv in li_recv:
        recv.turn_on()
    # launching game
    print_mini_tutorial()
    li_recv[-1].loop()
    kataen.cleanup()


if __name__ == '__main__':
    run_game()

# ----------------------
# -- web kataSDK0.0.7 --
# ----------------------
wanted_mode = None
game_mger = None
paint_ev = CgmEvent(kataen.EngineEvTypes.PAINT, screen=None)
lu_ev = CgmEvent(kataen.EngineEvTypes.LOGICUPDATE, curr_t=None)
def game_web_ctx():
    global game_mger, wanted_mode,lu_ev
    kataen.init(wanted_mode)
    # MVC architecture rocks
    model_objs = [ShipModel(), RocksModel()]
    li_recv = [
        TinyWorldView(*model_objs),
        ShipCtrl(*model_objs),
        kataen.get_game_ctrl()
    ]
    for recv in li_recv:
        recv.turn_on()
    # launching game
    print_mini_tutorial()

    game_mger = kataen.EventManager.instance()
    #paint_ev.screen=kataen.get_screen()


def kata_animate(infot, painting):
    global game_mger, paint_ev, lu_ev
    lu_ev.curr_t = infot
    game_mger.post(lu_ev)

    game_mger.post(paint_ev)
    pass
    game_mger.update()


