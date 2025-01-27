import os
import pyved_engine as pyv

# import pygame as pg
# from pygame import *

from . import animation
from . import scene as scene_module

pyv.bootstrap_e()
pygame = pyv.pygame
image = pygame.image
mixer = pygame.mixer
mouse = pygame.mouse


class Game:
    def __init__(self):
        self.load_settings()
        self.scalar = int(self.settings['resolution'][0] / self.settings['screenbuffer'][0])
        self.video_init()  # also inits pyved
        self.input_init()
        self.music = None

        self.gameover = False

        # MANDATORY! Otherwise we cant play sprite animations
        self.frame_counter = 1
        # for god knows what reason, not having fps defined here will prevent hud (health) display from working
        self.fps = 60.0

        self.clock = pyv.vars.clock  # pygame.time.Clock()
        self.pause = False
        self.step_size = 16

        self.scenes = None  # will be updated from outside
        self.scene = None  # idem

    def load_settings(self):
        # TODO fix this,
        # what would be the "pyved-way" to handle this ??!

        f = open('cartridge/settings.ini', 'r')
        settings_list = []
        rgb_tuple = (
            'window_color',
            'window_color_b',
            'highlight',
            'active',
            'text',
            'button_color',
            'button_text',
            'disabled',
            'shadow',
        )

        for line in f:
            settings_list.append(line.split(' '))
        for setting in settings_list:
            if setting[0] in rgb_tuple:
                setting[1] = setting[1].rstrip('\n')
            else:
                setting[1] = int(setting[1].rstrip('\n'))
            try:
                setting[2] = int(setting[2].rstrip('\n'))
            except IndexError:
                pass
        f.close()
        self.settings = {}
        for setting in settings_list:
            if len(setting) > 2:
                temp_setting = []
                for i in setting[1:]:
                    temp_setting.append(i)
                self.settings[setting[0]] = temp_setting
            elif setting[0] in rgb_tuple:
                i = setting[1]
                r = int(i[0:3])
                g = int(i[3:6])
                b = int(i[6:9])
                temp_setting = (r, g, b)
                self.settings[setting[0]] = temp_setting
            else:
                self.settings[setting[0]] = setting[1]

    def video_init(self):
        # - deprecated code (pre-pyved port)
        # os.environ['SDL_VIDEO_CENTERED'] = '1'
        # pg.init()
        size = self.settings['resolution']
        # flags = 0
        # if self.settings['borderless']:
        #     flags = NOFRAME
        # if self.settings['fullscreen']:
        #     flags = FULLSCREEN | HWSURFACE
        # depth = self.settings['depth']
        # self.screen = display.set_mode(size, flags, depth)
        # self.screenbuffer = Surface(self.settings['screenbuffer']).convert()
        pyv.init(mode=0, forced_size=size)
        self.screen= pyv.vars.screen

        # self.screenbuffer = pygame.surface.Surface(self.settings['screenbuffer']).convert()

        # debug how pygame has initialized the display sub-module
        # print(display.Info())

    def input_init(self):
        mouse.set_visible(True)
        self.mouse_pos = mouse.get_pos()
        self.leftclick = False
        self.leftmouse = False
        self.rightclick = False
        self.rightmouse = False
        self.left = False
        self.right = False
        self.up = False
        self.down = False

    def input(self):
        self.mouse_pos = mouse.get_pos()
        self.mouse_pos = (int(self.mouse_pos[0] / self.scalar), int(self.mouse_pos[1] / self.scalar))
        self.rightclick = False
        self.leftclick = False
        for e in pyv.evsys0.get():
            if e.type == pyv.evsys0.QUIT:
                self.quit()
            if e.type == pyv.evsys0.KEYDOWN:
                if e.key == pyv.evsys0.K_ESCAPE:
                    self.reset()
                if e.key == pyv.evsys0.K_a:
                    self.left = True
                if e.key == pyv.evsys0.K_d:
                    self.right = True
                if e.key == pyv.evsys0.K_w:
                    self.up = True
                if e.key == pyv.evsys0.K_s:
                    self.down = True
            if e.type == pyv.evsys0.KEYUP:
                if e.key == pyv.evsys0.K_a:
                    self.left = False
                if e.key == pyv.evsys0.K_d:
                    self.right = False
                if e.key == pyv.evsys0.K_w:
                    self.up = False
                if e.key == pyv.evsys0.K_s:
                    self.down = False
            if e.type == pyv.evsys0.MOUSEBUTTONDOWN:
                pygame.event.set_grab(1)  # TODO find out what this does and replace...
                if e.button == 1:
                    self.leftmouse = True
                if e.button == 3:
                    self.rightmouse = True
            elif e.type == pyv.evsys0.MOUSEBUTTONUP:
                if e.button == 1:
                    if self.leftmouse:
                        self.leftclick = True
                    self.leftmouse = False
                if e.button == 3:
                    if self.rightmouse:
                        self.rightclick = True
                    self.rightmouse = False

                pyv.evsys0.event.set_grab(0)  # TODO same as before

    def reset(self):
        if isinstance(self.scene, scene_module.TitleScreen):
            self.quit()
        else:
            self.scenes = [scene_module.TitleScreen(self)]

    def quit(self):
        self.screen.fill((0, 0, 0))
        pyv.flip()
        # display.flip()
        self.gameover = True

    #def execute_scene(self):
    #    self.now = pygame.time.get_ticks()
    #    while not self.done:

    # old fully deprec code
    #         if self.scenes:
    #
	# 			scene_done = False
	# 			self.scene = self.scenes[-1]
	# 			self.t = time.get_ticks()
	# 			#self.update_caption()
	# 			while self.t - self.now >= self.step_size:
	# 				self.frame_counter += 1
	# 				if self.frame_counter > self.fps:
	# 					self.frame_counter = 1
	# 				self.input()
	# 				if not self.pause:
	# 					scene_done = self.scene.update(self)
	# 				self.now += self.step_size
	# 				n = self.t - self.now
	# 				if n:
	# 					display.set_caption('FPS: ' + str(1000 / n))
	# 			self.scene.render(self)
	# 			display.update()
    #
	# 			if scene_done:
	# 				self.scenes.remove(self.scene)


def load_graphics(g_ref: Game):
    g_ref.graphics = {
        'effect_dust_001': animation.Animation(pyv.vars.images['effect-dust_001'], 'effect_dust_001',
                                               (16, 16)),
        'effect_explosion_001': animation.Animation(pyv.vars.images['effect-explosion_001'],
                                                    'effect_explosion_001', (8, 8)),
        'effect_explosion_002': animation.Animation(pyv.vars.images['effect-explosion_002'],
                                                    'effect_explosion_002', (8, 8)),
        'effect_explosion_003': animation.Animation(pyv.vars.images['effect-explosion_003'],
                                                    'effect_explosion_003', (8, 8)),
        'effect_explosion_004': animation.Animation(pyv.vars.images['effect-explosion_004'],
                                                    'effect_explosion_004', (8, 8)),

        'gui_health_001': animation.Animation(pyv.vars.images['gui-health_001'], 'gui_health_001',
                                              (4, 6)),
        'gui_healthbar_001': animation.Animation(pyv.vars.images['gui-healthbar_001'],
                                                 'gui_healthbar_001', (64, 18)),

        'sprite_battery_001': animation.Animation(pyv.vars.images['spr-battery_001'],
                                                  'sprite_battery_001', (16, 16)),
        'sprite_bomb_001': animation.Animation(pyv.vars.images['spr-bomb_001'], 'sprite_bomb_001',
                                               (12, 12)),
        'sprite_bullet_001': animation.Animation(pyv.vars.images['spr-bullet_001'],
                                                 'sprite_bullet_001', (8, 8)),
        'sprite_bullet_002': animation.Animation(pyv.vars.images['spr-bullet_002'],
                                                 'sprite_bullet_002', (4, 4)),
        'sprite_bullet_003': animation.Animation(pyv.vars.images['spr-bullet_003'],
                                                 'sprite_bullet_003', (4, 4)),
        'sprite_buzzard_001': animation.Animation(pyv.vars.images['spr-buzzard_001'],
                                                  'sprite_buzzard_001', (24, 24)),
        'sprite_heart_001': animation.Animation(pyv.vars.images['spr-heart_001'], 'sprite_heart_001',
                                                (8, 8)),
        'sprite_hero_001': animation.Animation(pyv.vars.images['spr-hero_001'], 'sprite_hero_001',
                                               (16, 16)),
        'sprite_spread_001': animation.Animation(pyv.vars.images['spr-spread_001'],
                                                 'sprite_spread_001', (12, 12)),
        'sprite_victory_001': animation.Animation(pyv.vars.images['spr-victory_001'],
                                                  'sprite_victory_001', (32, 32)),
        'sprite_walker_001': animation.Animation(pyv.vars.images['spr-walker_001'],
                                                 'sprite_walker_001', (16, 16))
    }


def load_sounds(g_ref: Game):
    g_ref.sounds = {
        'sfx_explosion_001': mixer.Sound('audio/sfx/explosion_001.wav'),
        'sfx_explosion_002': mixer.Sound('audio/sfx/explosion_002.wav'),
        'sfx_explosion_003': mixer.Sound('audio/sfx/explosion_003.wav'),
        'sfx_heart_001': mixer.Sound('audio/sfx/heart_001.wav'),
        'sfx_hurt_001': mixer.Sound('audio/sfx/hurt_001.wav'),
        'sfx_impact_001': mixer.Sound('audio/sfx/impact_001.wav'),
        'sfx_impact_002': mixer.Sound('audio/sfx/impact_002.wav'),
        'sfx_impact_003': mixer.Sound('audio/sfx/impact_003.wav'),
        'sfx_impact_004': mixer.Sound('audio/sfx/impact_004.wav'),
        'sfx_impact_005': mixer.Sound('audio/sfx/impact_005.wav'),
        'sfx_powerup_001': mixer.Sound('audio/sfx/powerup_001.wav'),
        'sfx_shoot_001': mixer.Sound('audio/sfx/shoot_001.wav'),
        'sfx_shoot_002': mixer.Sound('audio/sfx/shoot_002.wav'),
        'sfx_shoot_003': mixer.Sound('audio/sfx/shoot_003.wav'),
        'sfx_shoot_004': mixer.Sound('audio/sfx/shoot_004.wav'),
        'sfx_thrust_001': mixer.Sound('audio/sfx/thrust_001.wav'),
    }


g_obj = None


def init(vm_state):
    global g_obj
    g_obj = Game()
    load_graphics(g_obj)
    load_sounds(g_obj)
    g_obj.scenes = [
        scene_module.TitleScreen(g_obj)
    ]
    g_obj.scene = g_obj.scenes[-1]


def update(t_info):
    while not g_obj.gameover:
        scene_done = False
        g_obj.scene = g_obj.scenes[-1]

        # this line has been removed,
        #  since pyv.flip already handles the frame rate control
        # ticker = self.clock.tick_busy_loop(self.fps)

        # debug info removed as well
        # self.frame_counter += 1
        # if self.frame_counter > self.fps:
        #    self.frame_counter = 1
        # pygame.display.set_caption('FPS: ' + str(self.clock.get_fps()))
        g_obj.input()
        if not g_obj.pause:
            scene_done = g_obj.scene.update(g_obj)
        g_obj.scene.render(g_obj)
        pyv.flip()
        # pygame.display.update()
        if scene_done:
            g_obj.scenes.remove(g_obj.scene)
    else:
        g_obj.quit()


def close(vm_state):
    pyv.quit()  # pg.quit()


# since we're using the launcher you must not
# use your own game loop...

# init()
# while True:
#     update(0.0)
# close()
