import katagames_sdk as katasdk
import random


kataen = katasdk.engine
pygame = kataen.pygame


class MyGame(katasdk.BaseGame):
    def __init__(self):
        super().__init__()
        self.mycol = pygame.Color('lightsteelblue3')
        self.positions = list()
        self._w, self._h = None, None
    
    def get_mode(self):
        return kataen.OLD_SCHOOL_MODE

    # custom
    def _add_alea(self):
        w, h = self._w, self._h
        self.positions.append(
            (random.randint(0+10,w-10,),random.randint(0+33,h-33))
        )   
    
    def pre_update(self):
        self._w, self._h = kataen.get_screen().get_size()
        
        for _ in range(8):
            self._add_alea()

    def render(self, screen):
        screen.fill(self.mycol)
        for p in self.positions:
            pygame.draw.circle(screen,(87,250,8), p, 21)

    def update(self, events, dt):
        for ev in events:
            if ev.type == pygame.MOUSEBUTTONDOWN:
                self._add_alea()
            elif ev.type == pygame.KEYDOWN and ev.key == pygame.K_SPACE:
                del self.positions[:]
                for _ in range(3):
                    self._add_alea()


# entry point, both for local & web runs
t = MyGame()
t.start()
