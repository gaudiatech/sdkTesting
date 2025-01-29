import math
from random import randint


class Rumbler:
    def __init__(self, power=8):
        self.power = power
        self.angle = math.radians(randint(0, 360))

    def update(self, game):
        v = game.scene.tilemap.viewport
        self.angle += (180 + randint(-60, 60))
        ox = math.sin(self.angle) * self.power
        oy = math.cos(self.angle) * self.power
        game.scene.tilemap.set_focus(v.centerx + ox, v.centery + oy)
        self.power *= 0.9
        if self.power < 1:
            game.scene.rumbler = None
