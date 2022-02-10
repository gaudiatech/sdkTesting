import katagames_sdk as katasdk
import glvars
from mon_package.compo import Avatar, AvatarView, AvatarCtrl


kataen = katasdk.engine
pygame = kataen.import_pygame()

def run_game():
  kataen.init(kataen.OLD_SCHOOL_MODE)
  snd = pygame.mixer.Sound('assets/bensound-punky.ogg')
  snd.set_volume(0.28)
  snd.play(-1)
  print()
  print('** tester **')
  print('u should hear some music...')
  print('and be able to move a rock using UP/DOWN arrow keys')
  
  glvars.scr_size = kataen.get_screen().get_size()
  av = Avatar()
  li_recv = [kataen.get_game_ctrl(), AvatarView(av), AvatarCtrl(av)]
  for recv_obj in li_recv:
    recv_obj.turn_on()
  li_recv[0].loop()
  kataen.cleanup()

if __name__=='__main__':
  run_game()
