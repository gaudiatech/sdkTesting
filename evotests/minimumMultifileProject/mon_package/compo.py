import glvars
import katagames_sdk as katasdk

kataen = katasdk.engine

pygame = kataen.import_pygame()
EventReceiver = kataen.EventReceiver
EngineEvTypes = kataen.EngineEvTypes

class Avatar:
  def __init__(self):
    self.pos = [240, 135]
    self.direct = 0

class AvatarView(EventReceiver):
  def __init__(self, avref):
    super().__init__()
    self.avref = avref
    self.img = pygame.image.load('assets/rock.png')
    self.img.set_colorkey((255,0,255))
    self.offset = list(self.img.get_size())
    self.offset[0] -= self.offset[0]//2
    self.offset[1] -= self.offset[1]//2
    self.offset[0] *= -1
    self.offset[1] *= -1
  def proc_event(self, ev, source):
    if ev.type == EngineEvTypes.PAINT:
      ev.screen.fill(pygame.color.Color('antiquewhite2'))
      ev.screen.blit(
        self.img,
        (self.avref.pos[0]+self.offset[0], self.avref.pos[1]+self.offset[1])
      )

class AvatarCtrl(EventReceiver):
  def __init__(self, avref):
    super().__init__()
    self.avref = avref
  def proc_event(self, ev, source):
    if ev.type == EngineEvTypes.LOGICUPDATE:
      avdir = self.avref.direct
      self.avref.pos[1] = (self.avref.pos[1] + avdir) % glvars.scr_size[1]
    elif ev.type == pygame.KEYDOWN:
      if ev.key == pygame.K_UP:
        self.avref.direct = -1
      elif ev.key == pygame.K_DOWN:
        self.avref.direct = 1
    elif ev.type == pygame.KEYUP:
      prkeys = pygame.key.get_pressed()
      if not(prkeys[pygame.K_UP] or prkeys[pygame.K_DOWN]):
        self.avref.direct = 0

