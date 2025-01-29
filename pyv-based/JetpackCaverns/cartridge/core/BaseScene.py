import pyved_engine as pyv

mixer = pyv.pygame.mixer
sprite = pyv.pygame.sprite


class BaseScene:
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
