from pygame import *


class HUD:
	def __init__(self, game, player, *groups):
		self.healthbar = Healthbar(game, player, (7,7), *groups)

	def update(self, game):
		self.healthbar.update(game)


class Healthbar(sprite.Sprite):
	def __init__(self, game, player, position, *groups):
		sprite.Sprite.__init__(self, *groups)
		self.animation = game.graphics['gui_healthbar_001']
		self.set_health(game, player)
		self.beat = False
		self.image = self.images[self.beat]
		self.rect = self.image.get_rect(topleft=position)

	def set_health(self, game, player):
		beat1 = self.animation.frames[0][0].copy()
		beat2 = self.animation.frames[0][1].copy()
		x = 12
		y = 6
		h = player.health
		print('new player health:', h)
		hp = game.graphics['gui_health_001'].frames[0][0]
		while h > 0:
			h -= 1
			x += 3
			beat1.blit(hp, (x,y))
			beat2.blit(hp, (x,y))
		self.images = [beat1, beat2]

	def update(self, game):
		if not game.frame_counter % 15:
			self.beat = not self.beat
			self.image = self.images[self.beat]