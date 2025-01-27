from pygame import *

class PlaySounds:
	mixer.init(44100, -16, 1, 1024)
	channel_01= mixer.Channel(1) #bullet impact
	mixer.set_reserved(1)
	channel_02 = mixer.Channel(2)
	mixer.set_reserved(2)
	channel_03 = mixer.Channel(3)
	mixer.set_reserved(3)
	channel_04 = mixer.Channel(4)
	mixer.set_reserved(4)

	def __init__(self, game, sound, numberCheck=0):
		sounds_on = game.settings['sound']
		if sounds_on:
			volume = game.settings['s_vol']
			volume = volume / 100
			sound.set_volume(volume)
			if numberCheck == 1:
				self.channel_01.play(sound)
			elif numberCheck == 2:
				self.channel_02.play(sound)
			elif numberCheck == 3:
				self.channel_03.play(sound)
			elif numberCheck == 4:
				self.channel_04.play(sound)
			else:
				sound.play()

class PlayMusic:
	def __init__(self, game, music):
		volume = game.settings['m_vol']
		volume = volume / 100
		mixer.music.set_volume(volume)
		mixer.music.load(music)
		mixer.music.play(-1, 0.0)
		self.volume(game)

	def volume(self, game):
		volume = game.settings['m_vol']
		volume = volume / 100
		mixer.music.set_volume(volume)
		if game.settings['music'] == 0:
			mixer.music.pause()
		else: mixer.music.unpause()