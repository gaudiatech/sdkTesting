import math
from random import randint, choice

# from pygame import *

from . import audio
from . import maptools
from . import rumble
from . import scene
import pygame

GRAVITY = 0.025
TERMINAL = 2
FRICTION = 0.95

'''
Entities ---------------------------------------------------------------------
'''


class Entity(pygame.sprite.Sprite):
    def __init__(self, game, position, *groups):
        pygame.sprite.Sprite.__init__(self, *groups)
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
            if isinstance(self, PowerUp):
                self.yvel += GRAVITY / 10
            else:
                self.yvel += GRAVITY
        if self.heavy:
            self.yvel += GRAVITY * 3
        if isinstance(self, Player):
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

    def collide(self, game, xvel, yvel):
        if isinstance(self, Battery):
            return
        elif isinstance(self, PowerUp):
            if self.hitbox.colliderect(game.scene.player.hitbox):
                self.pickup(game)
                return
        elif isinstance(self, Enemy):
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
                if isinstance(self, PowerUp):
                    self.oscillating = False
            elif yvel < 0:
                self.hitbox.top = cell.bottom
                self.ypos = self.hitbox.centery
                self.yvel = 0


class Player(Entity):
    def __init__(self, game, position, *groups):
        Entity.__init__(self, game, position, *groups)
        # self.image = Surface((16,16)).convert()
        # self.image.fill((255,0,0))
        self.animation = game.graphics['sprite_hero_001']
        self.image = self.animation.frames[0][0]
        self.rect = self.image.get_rect(center=position)
        self.hitbox = pygame.rect.Rect(0, 0, 12, 12)
        self.hitbox.center = self.rect.center
        self.acceleration = 0.1
        self.max_velocity = 2
        self.charge = 0
        self.charge_max = 120
        self.health = 15
        self.aiming = 2
        self.facing = 0
        self.flashing = 0
        self.spread = 0
        self.grenade = 0

    def damage(self, game, amount):
        if not self.flashing:
            if amount > 0:
                audio.PlaySounds(game, game.sounds['sfx_hurt_001'])
            self.health -= amount
            self.flashing = 45
            if self.health >= 15:
                self.health = 15
            if self.health <= 0:
                self.health = 0
            game.scene.hud.healthbar.set_health(game, self)
            if self.health <= 0:
                game.scene.done = True
                game.scenes.insert(0, scene.TitleScreen(self))

    def animate(self, game):
        angle = -1
        if (game.right or game.left or game.up or game.down) and not game.frame_counter % 6:
            audio.PlaySounds(game, game.sounds['sfx_thrust_001'], 4)
        if game.right:
            if game.up:
                angle = 225
            elif game.down:
                angle = 135
            else:
                angle = 180
        elif game.left:
            if game.up:
                angle = 315
            elif game.down:
                angle = 45
            else:
                angle = 0
        elif game.up:
            angle = 270
        elif game.down:
            angle = 90
        if angle != -1:
            Effect(game, self.hitbox.center, 'effect_explosion_002', game.scene.behind, angle=angle)

        if self.flashing:
            flashcolor = (0, 0, 0)
            if self.flashing % 2:
                self.image = self.animation.frames[self.facing][self.aiming]
            else:
                tempimage = self.image.copy()
                newsurface = color_surface(tempimage, flashcolor, (255, 255, 255))
                del tempimage
                self.image = newsurface
                self.image.set_colorkey((0, 255, 0))
            self.flashing -= 1
        elif self.charge > 10:
            flashcolor = (0, 0, 0)
            if self.charge >= 60:
                modulus = 4
                newcolor = (252, 56, 0)
            else:
                modulus = 8
                newcolor = (252, 184, 0)
            if self.charge % modulus:
                self.image = self.animation.frames[self.facing][self.aiming]
            else:
                tempimage = self.image.copy()
                newsurface = color_surface(tempimage, flashcolor, newcolor)
                del tempimage
                self.image = newsurface
                self.image.set_colorkey((0, 255, 0))

    def update(self, game):
        if self.spread:
            self.spread -= 1
        if self.grenade:
            self.grenade -= 1
        mx, my = game.mouse_pos
        mx += game.scene.tilemap.viewport.x
        my += game.scene.tilemap.viewport.y
        aim = get_angle(self.hitbox.center, (mx, my))
        if aim <= 90:
            self.facing = 0
        elif aim >= 270:
            self.facing = 0
        else:
            self.facing = 1
        if aim <= 22.5:
            self.aiming = 2
        elif aim <= 67.5:
            self.aiming = 1
        elif aim <= 112.5:
            self.aiming = 0
        elif aim <= 157.5:
            self.aiming = 1
        elif aim <= 202.5:
            self.aiming = 2
        elif aim <= 247.5:
            self.aiming = 3
        elif aim <= 292.5:
            self.aiming = 4
        elif aim <= 337.5:
            self.aiming = 3
        else:
            self.aiming = 2
        self.image = self.animation.frames[self.facing][self.aiming]
        if game.up:
            self.yvel = max(-self.max_velocity, self.yvel - self.acceleration)
        elif game.down:
            self.yvel = min(self.max_velocity + TERMINAL, self.yvel + self.acceleration)
        if game.left:
            if self.xvel > 0:
                self.xvel *= FRICTION
            self.xvel = max(-self.max_velocity, self.xvel - self.acceleration)
        elif game.right:
            if self.xvel < 0:
                self.xvel *= FRICTION
            self.xvel = min(self.max_velocity, self.xvel + self.acceleration)
        else:
            self.xvel *= FRICTION
            if -0.1 < self.xvel < 0.1:
                self.xvel = 0
        if game.leftmouse:
            self.charge = min(self.charge + 1, self.charge_max)
        if game.leftclick:
            if self.charge >= 60 or self.grenade:
                mx = game.mouse_pos[0] + game.scene.tilemap.viewport.x
                my = game.mouse_pos[1] + game.scene.tilemap.viewport.y
                angle = get_angle(self.rect.center, (mx, my))
                audio.PlaySounds(game, game.sounds['sfx_shoot_004'], 2)
                if self.charge == self.charge_max:
                    Bomb(game, (self.xpos, self.ypos), game.scene.sprites, energy=4, angle=angle)
                else:
                    Bomb(game, (self.xpos, self.ypos), game.scene.sprites, energy=1, angle=angle)
                    if self.spread:
                        Bomb(game, (self.xpos, self.ypos), game.scene.sprites, energy=1, angle=angle + 15)
                        Bomb(game, (self.xpos, self.ypos), game.scene.sprites, energy=1, angle=angle - 15)
            # self.image.fill((255,0,0))
            else:
                x = int(self.xpos)
                # r = 4
                # x = randint(x-r, x+r)
                mx = game.mouse_pos[0] + game.scene.tilemap.viewport.x
                my = game.mouse_pos[1] + game.scene.tilemap.viewport.y
                angle = get_angle(self.rect.center, (mx, my))
                Bullet(game, (x, self.ypos), game.scene.behind, angle=angle)
                s = randint(1, 3)
                audio.PlaySounds(game, game.sounds['sfx_shoot_00' + str(s)], 2)
                if self.spread:
                    Bullet(game, (x, self.ypos), game.scene.behind, angle=angle - 15)
                    Bullet(game, (x, self.ypos), game.scene.behind, angle=angle + 15)
            self.charge = 0
        if game.rightclick and self.charge >= 10:
            energy = self.charge
            energy = energy // 10
            Bomb(game, (self.xpos, self.ypos), game.scene.behind, energy=energy)
            self.charge = 0
        Entity.update(self, game)
        self.animate(game)


class Bullet(Entity):
    def __init__(self, game, position, *groups, angle=270, velocity=6, owner='player'):
        Entity.__init__(self, game, position, *groups)
        if owner == 'enemy':
            self.animation = game.graphics['sprite_bullet_003']
        else:
            self.animation = game.graphics['sprite_bullet_002']
        self.ani_speed = 4
        self.image = self.animation.frames[0][0]
        self.rect = self.image.get_rect(center=position)
        self.hitbox = self.rect.copy()
        self.velocity = velocity
        self.angle = angle
        self.xvel, self.yvel = get_vector(self.angle, self.velocity)
        self.owner = owner

    def update(self, game):
        # Entity.update(self, game)
        self.xpos += self.xvel
        self.ypos += self.yvel
        self.hitbox.center = (self.xpos, self.ypos)
        self.collide(game)
        self.rect.center = self.hitbox.center

        if game.scene.tilemap.viewport.collidepoint((self.xpos, self.ypos)):
            pass
        else:
            self.kill()

        self.animate(game)

    def collide(self, game):
        if self.owner == 'player':
            for enemy in game.scene.enemies:
                if enemy.hitbox.collidepoint(self.hitbox.center):
                    enemy.damage(game, 1)
                    self.remove(game)
                    return
        elif self.owner == 'enemy':
            if game.scene.player.hitbox.collidepoint(self.hitbox.center):
                game.scene.player.damage(game, 1)
                self.remove(game)
                return
        for cell in game.scene.tilemap.layers['lower'].collide(self.hitbox, 'barrier'):
            if 'battery' in cell.tile.properties:
                break
            if 'indestructible' in cell.tile.properties:
                self.remove(game, indestructible=True)
                break
            self.remove(game)

            '''
			if 'health' in cell.tile.properties:
				if 'turret' in cell.tile.properties:
					if (cell.x-1, cell.y) in game.scene.tilemap.layers['lower'].cells:
						if 'pipe' in game.scene.tilemap.layers['lower'].cells[cell.x-1, cell.y].tile.properties:
							return
					if (cell.x+1, cell.y) in game.scene.tilemap.layers['lower'].cells:
						if 'pipe' in game.scene.tilemap.layers['lower'].cells[cell.x+1, cell.y].tile.properties:
							return
					if (cell.x, cell.y-1) in game.scene.tilemap.layers['lower'].cells:
						if 'pipe' in game.scene.tilemap.layers['lower'].cells[cell.x, cell.y-1].tile.properties:
							return
					if (cell.x, cell.y+1) in game.scene.tilemap.layers['lower'].cells:
						if 'pipe' in game.scene.tilemap.layers['lower'].cells[cell.x, cell.y+1].tile.properties:
							return
				cell['health'] -= 1
				print('Health:', cell['health'])
				if cell['health'] <= 0:
					if 'turret' in cell.tile.properties:
						cell.tile = game.scene.tilemap.tilesets[42]
					else:
						maptools.breakbattery(game, game.scene.tilemap, cell.x, cell.y)
			'''

    def remove(self, game, indestructible=False):
        if indestructible:
            audio.PlaySounds(game, game.sounds['sfx_impact_005'], 1)
        else:
            x = randint(1, 3)
            audio.PlaySounds(game, game.sounds['sfx_impact_00' + str(x)], 1)
        Effect(game, self.rect.center, 'effect_explosion_001', game.scene.sprites, stationary=True)

        self.kill()


class Bomb(Entity):
    def __init__(self, game, position, *groups, energy=0, angle=270):
        Entity.__init__(self, game, position, *groups)
        # self.image = Surface((4,4)).convert()
        # self.image.fill((0,255,255))
        self.animation = game.graphics['sprite_bullet_001']
        self.ani_speed = 4
        self.image = self.animation.frames[0][0]
        self.rect = self.image.get_rect(center=position)
        self.hitbox = self.rect.copy()
        self.energy = energy
        if self.energy == 1:
            self.velocity = 4
        elif self.energy == 4:
            self.velocity = 4
        self.angle = angle
        self.xvel, self.yvel = get_vector(self.angle, self.velocity)

    def animate(self, game):
        Effect(game, self.rect.center, 'effect_explosion_003', game.scene.behind, stationary=False,
               angle=int(self.angle + 180))
        Entity.animate(self, game)

    def update(self, game):
        # Entity.update(self, game)
        if self.energy <= 0:
            self.kill()
        self.xpos += self.xvel
        self.ypos += self.yvel
        self.hitbox.center = (self.xpos, self.ypos)
        self.collide(game)
        self.rect.center = self.hitbox.center
        if game.scene.tilemap.viewport.collidepoint((self.xpos, self.ypos)):
            pass
        else:
            self.kill()
        self.animate(game)

    def collide(self, game):
        for enemy in game.scene.enemies:
            if enemy.hitbox.collidepoint(self.hitbox.center):
                enemy.damage(game, 4)
                self.remove(game)

                return
        for cell in game.scene.tilemap.layers['lower'].collide(self.hitbox, 'barrier'):
            if cell.rect.collidepoint(self.hitbox.center):
                if 'indestructible' in cell.tile.properties:
                    self.remove(game, indestructible=True)
                else:
                    if self.energy >= 1:
                        self.energy -= 1
                        self.velocity -= 1
                        self.xvel, self.yvel = get_vector(self.angle, self.velocity)
                        maptools.breaktile(game, game.scene.tilemap, cell.x, cell.y)
                        for x in range(4):
                            Effect(game, cell.rect.center, 'effect_dust_001', game.scene.behind, angle=randint(0, 360),
                                   speed=8)

    def remove(self, game, indestructible=False):
        if indestructible:
            audio.PlaySounds(game, game.sounds['sfx_impact_005'], 1)
        else:
            audio.PlaySounds(game, game.sounds['sfx_impact_004'], 1)
        for x in range(8):
            Effect(game, self.hitbox.center, 'effect_explosion_003', game.scene.behind, angle=randint(0, 360), speed=8)
        self.kill()


'''
Enemies
'''


class Spawner():
    def __init__(self, game, position, enemy, cooldown, continuous, maxspawn, offscreen):
        self.continuous = continuous
        self.maxcooldown = cooldown
        self.cooldown = 0
        self.maxspawn = maxspawn
        self.currentspawn = 0
        self.offscreen = offscreen
        self.xpos = position[0]
        self.ypos = position[1]
        self.rect = pygame.rect.Rect(position, (16, 16))
        self.enemy = enemy
        self.suppress = False
        self.children = []

    def update(self, game):
        if not self.suppress:
            v = game.scene.tilemap.viewport.copy()
            v.inflate_ip(128, 128)
            if self.currentspawn < self.maxspawn:
                if not v.collidepoint(self.rect.center) or self.continuous:
                    self.cooldown -= 1
                    if self.cooldown < 0:
                        self.cooldown = 0
                    if self.cooldown <= 0:
                        if self.continuous and (v.collidepoint(self.rect.center) or self.offscreen):
                            self.currentspawn += 1
                            self.cooldown = self.maxcooldown
                            spawnenemy(self.enemy)(game, self.rect.center, self,
                                                   (game.scene.enemies, game.scene.sprites))
                        elif not self.continuous:
                            self.currentspawn += 1
                            self.cooldown = self.maxcooldown
                            spawnenemy(self.enemy)(game, self.rect.center, self,
                                                   (game.scene.enemies, game.scene.sprites))
        if self.currentspawn < 0:
            self.currentspawn = 0


class Enemy(Entity):
    def __init__(self, game, position, spawner, *groups):
        Entity.__init__(self, game, position, *groups)
        self.spawner = spawner
        self.current_behavior = 0
        self.behavior = []
        self.flashing = 0
        self.offscreen = False
        self.flying = False
        self.power = 0
        if self.spawner:
            self.spawner.children.append(self)

    def damage(self, game, amount):
        audio.PlaySounds(game, game.sounds['sfx_hurt_001'])
        self.health -= amount
        self.flashing = 10
        if self.health <= 0:
            self.destroy(game)

    def destroy(self, game):
        s = randint(1, 3)
        audio.PlaySounds(game, game.sounds['sfx_explosion_00' + str(s)], 3)
        if self.spawner:
            self.spawner.children.remove(self)
            self.spawner.currentspawn = len(self.spawner.children)
        for x in range(8):
            Effect(game, self.hitbox.center, 'effect_explosion_002', game.scene.behind, angle=randint(0, 360), speed=4)
            Effect(game, self.hitbox.center, 'effect_explosion_004', game.scene.behind, angle=randint(0, 360), speed=4)
        if self.power:
            game.scene.rumbler = rumble.Rumbler(power=self.power)
        if not randint(0, 360) % 3:
            spawn_pickup(game, self.hitbox.center)
        self.kill()

    def execute_behavior(self, game):
        v = game.scene.tilemap.viewport.copy()
        v.inflate_ip(64, 64)
        if v.collidepoint(self.hitbox.center) or self.offscreen:
            override = False
            if self.current_behavior >= len(self.behavior):
                self.current_behavior = 0
            b = self.behavior[self.current_behavior]
            if b[0] == 'wait':
                b[2] = randint(75, 135)
            elif b[0] == 'shoot':
                angle = get_angle(self.hitbox.center, game.scene.player.hitbox.center)
                Bullet(game, self.hitbox.center, game.scene.behind, angle=angle, owner='enemy', velocity=2.5)
            elif b[0] == 'fly towards player':
                rotate_angle(self, game.scene.player, b[3])
                self.velocity = min(self.velocity + self.acceleration, self.max_velocity)
                self.xvel, self.yvel = get_vector(self.angle, self.velocity)

            elif b[0] == 'decelerate':
                if self.velocity > 0:
                    self.velocity -= self.acceleration
                    self.xvel, self.yvel = get_vector(self.angle, self.velocity)
                    override = True
                else:
                    self.velocity = 0
                    self.xvel, self.yvel = get_vector(self.angle, self.velocity)

            if not override:
                b[1] += 1
                if b[1] > b[2]:
                    b[1] = 0
                    self.current_behavior += 1

    def animate(self, game):
        Entity.animate(self, game)
        flashcolor = (0, 0, 0)
        if self.flashing:
            if self.flashing % 2:
                self.image = self.animation.frames[0][self.ani_state]
            else:
                tempimage = self.image.copy()
                newsurface = color_surface(tempimage, flashcolor, (255, 255, 255))
                del tempimage
                self.image = newsurface
                self.image.set_colorkey((0, 255, 0))
            self.flashing -= 1

    def update(self, game):
        if self.behavior:
            self.execute_behavior(game)
        Entity.update(self, game)
        self.animate(game)


class Battery(Enemy):
    def __init__(self, game, position, spawner, *groups):
        Enemy.__init__(self, game, position, spawner, *groups)
        self.maxhealth = 10
        self.health = self.maxhealth
        self.animation = game.graphics['sprite_battery_001']
        self.image = self.animation.frames[0][0]
        self.rect = self.image.get_rect(center=position)
        self.hitbox = self.rect.copy()
        self.ani_speed = 8
        self.behavior = []
        self.flying = True
        self.angle = 0
        self.velocity = 0
        self.max_velocity = 0
        self.acceleration = 0

    def destroy(self, game):
        Enemy.destroy(self, game)
        x = int(self.hitbox.centerx / 16)
        y = int(self.hitbox.centery / 16)
        maptools.breakbattery(game, game.scene.tilemap, x, y)


class Buzzard(Enemy):
    def __init__(self, game, position, spawner, *groups):
        Enemy.__init__(self, game, position, spawner, *groups)
        self.maxhealth = 4
        self.health = self.maxhealth
        self.animation = game.graphics['sprite_buzzard_001']
        self.image = self.animation.frames[0][0]
        self.rect = self.image.get_rect(center=position)
        self.hitbox = self.rect.copy()
        self.ani_speed = 8
        self.behavior = [['wait', 0, 90], ['fly towards player', 0, 180, 2], ['decelerate', 0, 1]]
        self.flying = True
        self.angle = randint(0, 360)
        self.velocity = 0
        self.max_velocity = 2
        self.power = 4
        self.acceleration = 0.05


class Walker(Enemy):
    def __init__(self, game, position, spawner, *groups):
        Enemy.__init__(self, game, position, spawner, *groups)
        self.maxhealth = 1
        self.health = self.maxhealth
        self.animation = game.graphics['sprite_walker_001']
        self.image = self.animation.frames[0][0]
        self.rect = self.image.get_rect(center=position)
        self.hitbox = self.rect.copy()
        self.ani_speed = 8
        self.behavior = [['wait', 0, 90], ['shoot', 0, 1], ['wait', 0, 90], ['wait', 0, 90]]
        self.direction = choice((-1, 1))
        self.heavy = True
        self.bounce = True
        self.power = 1
        self.xvel = self.direction * 0.25


'''
Powerups --------------------------------------------------------------------
'''


class PowerUp(Entity):
    def __init__(self, game, position, *groups):
        Entity.__init__(self, game, position, *groups)
        self.ani_speed = 8
        self.duration = 720
        self.oscillate = 0
        self.oscillating = True

    def update(self, game):
        if self.oscillating:
            self.oscillate += 3
            self.xvel = math.sin(math.radians(self.oscillate)) / 2
        else:
            self.xvel = 0
        Entity.update(self, game)
        self.duration -= 1
        if self.duration == 0:
            self.kill()
        self.animate(game)


class Exit(PowerUp):
    def __init__(self, game, position, *groups):
        PowerUp.__init__(self, game, position, *groups)
        self.animation = game.graphics['sprite_victory_001']
        self.image = self.animation.frames[0][0]
        self.rect = self.image.get_rect(center=position)
        self.hitbox = self.rect.copy()
        self.duration = -1

    def pickup(self, game):
        audio.PlaySounds(game, game.sounds['sfx_heart_001'])
        game.scene.done = True
        game.scenes.insert(0, scene.TitleScreen(self))
        self.kill()


class Heart(PowerUp):
    def __init__(self, game, position, *groups):
        PowerUp.__init__(self, game, position, *groups)
        self.animation = game.graphics['sprite_heart_001']
        self.image = self.animation.frames[0][0]
        self.rect = self.image.get_rect(center=position)
        self.hitbox = self.rect.copy()

    def pickup(self, game):
        audio.PlaySounds(game, game.sounds['sfx_heart_001'])
        game.scene.player.damage(game, -1)
        self.kill()


class Spread(PowerUp):
    def __init__(self, game, position, *groups):
        PowerUp.__init__(self, game, position, *groups)
        self.animation = game.graphics['sprite_spread_001']
        self.image = self.animation.frames[0][0]
        self.rect = self.image.get_rect(center=position)
        self.hitbox = self.rect.copy()

    def pickup(self, game):
        audio.PlaySounds(game, game.sounds['sfx_powerup_001'])
        game.scene.player.spread = 360
        self.kill()


class Grenade(PowerUp):
    def __init__(self, game, position, *groups):
        PowerUp.__init__(self, game, position, *groups)
        self.animation = game.graphics['sprite_bomb_001']
        self.image = self.animation.frames[0][0]
        self.rect = self.image.get_rect(center=position)
        self.hitbox = self.rect.copy()

    def pickup(self, game):
        audio.PlaySounds(game, game.sounds['sfx_powerup_001'])
        game.scene.player.grenade = 360
        self.kill()


'''
Effects ----------------------------------------------------------------------
'''


class Effect(Entity):
    def __init__(self, game, position, animation, *groups, repeat=False, flip=False, variance=45, stationary=False,
                 speed=1, angle=0):
        Entity.__init__(self, game, position, *groups)
        self.repeat = repeat
        self.ani_speed = speed
        self.animation = game.graphics[animation]
        self.image = self.animation.frames[0][0]
        self.rect = self.image.get_rect(center=position)
        self.hitbox = self.rect.copy()
        if flip:
            angle = angle + 180
        self.angle = randint(angle - variance, angle + variance)
        if not stationary:
            self.velocity = randint(5, 25)
            self.velocity = self.velocity / 20
        else:
            self.velocity = 0
        self.xvel, self.yvel = get_vector(self.angle, self.velocity)

    def animate(self, game):
        Entity.animate(self, game)
        if not self.repeat:
            if not self.ani_state and not self.ani_tick:
                self.kill()

    def update(self, game):
        self.xpos += self.xvel
        self.hitbox.centerx = self.xpos
        self.ypos += self.yvel
        self.hitbox.centery = self.ypos
        self.rect.center = self.hitbox.center
        self.animate(game)


'''
Helpers ----------------------------------------------------------------------
'''


def spawn_pickup(game, position):
    x = randint(1, 10)
    if x <= 4:
        Heart(game, position, game.scene.sprites)
    elif x <= 7:
        Spread(game, position, game.scene.sprites)
    elif x <= 10:
        Grenade(game, position, game.scene.sprites)


def color_surface(source, color, new_color):
    if len(color) == 3:
        pxarray = pygame.PixelArray(source)
        pxarray.replace(color, new_color)
        pxarray = pxarray.make_surface()
        newsurface = pygame.Surface(source.get_size())
        newsurface.blit(pxarray, (0, 0))
    if color == 'colorize':
        pxarray.replace((128, 128, 128), new_color)

    return newsurface


def spawnenemy(enemy):
    enemies = {
        'buzzard': Buzzard,
        'walker': Walker,
    }

    return enemies[enemy]


def get_vector(angle, velocity):
    xvel = velocity * math.cos(math.radians(angle))
    yvel = -(velocity * math.sin(math.radians(angle)))
    return xvel, yvel


def rotate_angle(source, target, rotation):
    x = target.hitbox.centerx - source.hitbox.centerx
    # x = closest.hitbox.centerx - bullet.rect.centerx
    if x == 0: x = 0.01
    y = target.hitbox.centery - source.hitbox.centery
    angle = -(math.degrees(math.atan(y / x)))
    source.angle = source.angle % 360
    if source.angle < 0: source.angle += 360
    if x < 0 and y > 0: angle += 180
    if x < 0 and y < 0: angle += 180
    if angle < 0: angle += 360

    # rotation = 2
    difference = abs(source.angle - angle)
    if difference < rotation: rotation = difference
    if difference < 180 and angle > source.angle:
        source.angle += rotation
    elif difference < 180 and angle < source.angle:
        source.angle -= rotation
    elif difference > 180 and angle > source.angle:
        source.angle -= rotation
    elif difference > 180 and angle < source.angle:
        source.angle += rotation
    elif difference == 180 or difference == 0:
        source.angle += rotation


def get_angle(source, target):
    dx = target[0] - (source[0])
    dy = target[1] - (source[1])

    if dx == 0:
        if dy < 0:
            return 90
        elif dy > 0:
            return 270
        else:
            return 90

    if dy == 0:
        if dx > 0:
            return 0
        elif dx < 0:
            return 180

    angle = -(math.degrees(math.atan(dy / dx)))

    if dx < 0 and dy > 0: angle += 180
    if dx < 0 and dy < 0: angle += 180

    if angle < 0: angle += 360
    if angle > 360: angle -= 360

    return angle
