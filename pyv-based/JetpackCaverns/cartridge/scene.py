import pyved_engine as pyv
from pygame import *

from . import audio
from . import entity
from . import hud
from . import maptools
from . import tmx


class Scene:
	def __init__(self, game):
		self.pause = False
		#if game.music:
		mixer.music.stop()
		self.ui_elements = []
		self.ui_dict = {}
		self.ui = sprite.LayeredUpdates()
		self.mouseover = None
		self.done = False
		self.initialized = False
		self.ox = 0
		self.oy = 0
		self.rumbler = None

	def render(self, game):
		#if game.settings['smoothing']:
		#	scaled = transform.smoothscale(game.screenbuffer, game.screen.get_size())
		#else:
		#	scaled = transform.scale(game.screenbuffer, game.screen.get_size())

		# game.screen.blit(scaled, (self.ox*game.scalar,self.oy*game.scalar))

		# game.screen.blit(scaled, (self.ox * game.scalar, self.oy * game.scalar))
		self.ox = self.oy = 0

	def update(self, game):
		pass
		'''
		for rumbler in self.rumblers:
			rumbler.update(game)
		'''

class TitleScreen(Scene):
	def __init__(self, game, *args):
		Scene.__init__(self, game)
		game.music = None
		self.bg = pyv.vars.images['title_001']

	def input(self, game):
		if game.leftclick:
			game.scenes.append(Gameplay(game))
			self.done = True

	def render(self, game):
		blittingsurface = game.screen
		pyv.vars.screen.blit(self.bg, (0,0))
		Scene.render(self, game)
		#bgcolor = (128,128,128)
		#game.screen.fill(bgcolor)

	def update(self, game):
		self.input(game)
		Scene.update(self, game)
		return self.done

class Gameplay(Scene):
	def __init__(self, game, *args):
		Scene.__init__(self, game)
		game.music = audio.PlayMusic(game, 'audio/music/ld48_001.ogg')
		self.sprites = tmx.SpriteLayer()
		self.enemies = sprite.Group()
		self.behind = tmx.SpriteLayer()
		if args:
			stage = args[0]
		else:
			stage = 'test_002.tmx'
		# maps are in the current directory afaik
		# stage = '../maps/' + stage
		self.tilemap = tmx.load(stage, game.settings['screenbuffer'])
		self.tilemap.layers.append(self.sprites)
		self.tilemap.layers.append(self.behind)
		self.load_spawners(game)
		self.load_batteries(game)
		self.tilemap.set_focus(0,0)
		self.timers = maptools.find_timers(self.tilemap)

		# self.player = entity.Player(game, (game.screenbuffer.get_width() / 2, 16), self.sprites)
		self.player = entity.Player(game, (pyv.vars.screen.get_width() / 2, 16), self.sprites)
		self.hud = hud.HUD(game, self.player, self.ui)
		exit = self.tilemap.layers['triggers'].find('victory')[0]
		entity.Exit(game, (exit.px, exit.py), self.sprites)

	def load_batteries(self, game):
		for battery in self.tilemap.layers['lower'].find('battery'):
			entity.Battery(game, battery.rect.center, None, (self.enemies, self.sprites))

	def load_spawners(self, game):
		self.spawners = []
		for spawner in self.tilemap.layers['triggers'].find('enemy'):
			enemy = spawner['enemy']
			cooldown = int(spawner['cooldown'])
			continuous = int(spawner['continuous'])
			maxspawn = int(spawner['maximum'])
			offscreen = int(spawner['offscreen'])
			self.spawners.append(entity.Spawner(game, (spawner.px, spawner.py), enemy, cooldown, continuous, maxspawn, offscreen))

	def input_init(self):
		pass

	def camera(self):
		p = self.player.rect
		self.tilemap.set_focus(p.centerx, p.centery)

	def input(self, game):
		pass

	def render(self, game):
		#blittingsurface = game.screenbuffer
		blittingsurface = pyv.vars.screen

		self.tilemap.layers['lower'].draw(blittingsurface)
		#self.highlight_tile(game)
		self.behind.draw(blittingsurface)
		self.sprites.draw(blittingsurface)
		self.ui.draw(blittingsurface)

		Scene.render(self, game)  # calling the super class

	def update(self, game):
		self.input(game)
		Scene.update(self, game)
		for spawner in self.spawners:
			spawner.update(game)
		self.behind.update(game)
		self.sprites.update(game)
		self.ui.update(game)
		#self.player.damage(game, randint(-3,3))
		maptools.pipe_timers(game, self.tilemap, self.timers)
		self.camera()
		if self.rumbler:
			self.rumbler.update(game)
		return self.done