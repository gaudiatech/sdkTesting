import pyved_engine as pyv

Sprite = pyv.pygame.sprite.Sprite

FRICTION = 0.95
GRAVITY = 0.025
TERMINAL = 2


class BaseEntity(Sprite):
    def __init__(self, game, position, *groups):
        super().__init__(*groups)
        self.xpos = position[0]
        self.ypos = position[1]
        self.xvel = 0
        self.yvel = 0
        self.ani_state = 0
        self.ani_tick = 0
        self.ani_speed = 0
        self.flying = False
        self.heavy = False
        self.bounce = False
        self.etype = 'base'  # inner/game-related type

    def type_check(self, exp_type):
        return self.etype == exp_type

    def animate(self, game):
        self.ani_tick += 1
        if self.ani_tick > self.ani_speed:
            self.ani_tick = 0
            self.ani_state += 1
            if self.ani_state >= len(self.animation.frames[0]):
                self.ani_state = 0
        self.image = self.animation.frames[0][self.ani_state]

    def update(self, game):
        self.xpos += self.xvel
        self.hitbox.centerx = self.xpos
        if self.xpos > game.scene.tilemap.px_width - 1:
            self.xpos = game.scene.tilemap.px_width - 1
        if self.xpos < 0:
            self.xpos = 0
        if self.xvel > 0:
            self.hitbox.x += 1
        elif self.xvel < 0:
            self.hitbox.x -= 1
        self.collide(game, self.xvel, 0)

        if not self.flying:
            if self.type_check('power_up'):
                self.yvel += GRAVITY / 10
            else:
                self.yvel += GRAVITY
        if self.heavy:
            self.yvel += GRAVITY * 3
        if self.type_check('player'):
            if game.down:
                mv = self.max_velocity
            else:
                mv = 0
            if self.yvel > TERMINAL + mv:
                self.yvel = TERMINAL + mv
        self.ypos += self.yvel
        self.hitbox.centery = self.ypos
        if self.ypos > game.scene.tilemap.px_height - 1:
            self.ypos = game.scene.tilemap.px_height - 1
        if self.ypos < 0:
            self.ypos = 0
        if self.yvel > 0:
            self.hitbox.y += 1
        elif self.yvel < 0:
            self.hitbox.y -= 1
        self.collide(game, 0, self.yvel)
        self.rect.center = self.hitbox.center

    # TODO check if we may refactor child classes to avoid the dirty ad-hoc type check
    def collide(self, game, xvel, yvel):
        if self.type_check('battery'):
            return
        elif self.type_check('power_up'):
            if self.hitbox.colliderect(game.scene.player.hitbox):
                self.pickup(game)
                return
        elif self.type_check('enemy'):
            if self.hitbox.colliderect(game.scene.player.hitbox):
                game.scene.player.damage(game, 2)
        for cell in game.scene.tilemap.layers['lower'].collide(self.hitbox, 'barrier'):
            if xvel > 0:
                self.hitbox.right = cell.left
                self.xpos = self.hitbox.centerx
                if self.bounce:
                    self.xvel *= -1
                else:
                    xvel = 0
            elif xvel < 0:
                self.hitbox.left = cell.right
                self.xpos = self.hitbox.centerx
                if self.bounce:
                    self.xvel *= -1
                else:
                    self.xvel = 0
            if yvel > 0:
                self.hitbox.bottom = cell.top
                self.ypos = self.hitbox.centery
                self.yvel = 0
                if self.type_check('power_up'):
                    self.oscillating = False
            elif yvel < 0:
                self.hitbox.top = cell.bottom
                self.ypos = self.hitbox.centery
                self.yvel = 0
