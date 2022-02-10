import random
import katagames_sdk as katasdk
kataen = katasdk.engine
EventReceiver = kataen.EventReceiver
EngineEvTypes = kataen.EngineEvTypes
pygame = kataen.import_pygame()
gfxd = kataen.import_gfxdraw()


class SimpV(EventReceiver):
    def __init__(self):
        super().__init__()
        w, h = kataen.get_screen().get_size()
        self.p = pygame.Vector2((w//2, h//2))

    def proc_event(self, ev, source):
        if ev.type == EngineEvTypes.PAINT:
            ev.screen.fill('#fcaa13')
            gfxd.filled_circle(ev.screen, int(self.p.x), int(self.p.y), 55, (255, 8, 8, 53))
            gfxd.filled_circle(ev.screen, int(self.p.x-77), int(self.p.y), 55, (255, 8, 8, 200))
        elif ev.type == EngineEvTypes.LOGICUPDATE:
            tmp = list(self.p)
            if random.random() < 0.5:
                tmp[0] += 1
            else:
                tmp[0] -= 1
            if random.random() < 0.5:
                tmp[1] += 1
            else:
                tmp[1] -= 1
            self.p.update(*tmp)


def run_game():
    kataen.init(kataen.HD_MODE)
    v = SimpV()
    gctrl = kataen.get_game_ctrl()

    v.turn_on()
    gctrl.turn_on()
    gctrl.loop()

    kataen.cleanup()


if __name__ == '__main__':
    run_game()
