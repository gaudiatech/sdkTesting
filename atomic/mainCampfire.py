"""
original demo made by:
 * tank king#8395  (pygame community, discord)

upgraded and converted to KataSDK by:
 * wkta-tom (github.com/wkat)

"""
import time
import random
import katagames_sdk as katasdk


kataen = katasdk.engine
pygame = kataen.import_pygame()

FPS = 60
SCREEN_WIDTH, SCREEN_HEIGHT = 960//2, 540//2
BGCOLOR = pygame.Color('#100600')  # quasi black
Y_FIRE_POS = SCREEN_HEIGHT-96
ANIM_SPEED = 25

EngineEvTypes = kataen.EngineEvTypes
clock = pygame.time.Clock()
flames = screen = None


class FlameParticle:
    alpha_layer_qty = 2
    alpha_glow_difference_constant = 2

    def __init__(self, x=SCREEN_WIDTH // 2, y=SCREEN_HEIGHT // 2, r=5):
        self.x = x
        self.y = self.org_y = y
        self.r = r
        self.first_r = r
        self.original_r = r
        self.alpha_layers = FlameParticle.alpha_layer_qty
        self.alpha_glow = FlameParticle.alpha_glow_difference_constant
        max_surf_size = 2 * self.r * self.alpha_layers * self.alpha_layers * self.alpha_glow
        self.surf = pygame.Surface((max_surf_size, max_surf_size))  # TODO fix (pygame.SRCALPHA makes sdk0.0.6 crash)
        self.burn_rate = 0.028 + random.random()/3.14
    
    def update(self):
        self.original_r -= self.burn_rate * self.first_r
        self.r = int(self.original_r)
        if self.r <= 0:
            self.r = 1
        
        self.x += random.randint(-1, 1)
        
        # orange-like particle detection, see draw algorithm...
        if (abs(self.org_y-self.y) < 29) and not(abs(self.org_y-self.y) < 14 and (self.original_r > 3.5)):
            self.y -= 2
        else:
            self.y -= 3
    
    def draw(self):
        max_surf_size = (self.original_r + 2 * 2 * 3.33) * 2
        self.surf = pygame.Surface((max_surf_size, max_surf_size), pygame.SRCALPHA)  # TODO same problem as above
        retrait = {
            2: 245,
            1: 175,
            0: 144
        }
        
        for i in range(self.alpha_layers, -1, -1):
            alpha = 255 - retrait[i]
            if alpha <= 0:
                alpha = 0
            xx = self.original_r + i * i * 3.33
            if xx > 25:
                radius = 20  # cap size
            else:
                radius = int(xx*0.8)

            # color attribution
            if abs(self.org_y-self.y) < 29:
                if abs(self.org_y-self.y) < 14 and (self.original_r > 3.5):
                    r, g, b = 255, 35, 0  # red, pretty much
                else:
                    r, g, b = 255, 129, 0  # orange
            elif (abs(self.org_y-self.y) < 50) or (self.original_r > 1.8):
                r, g, b = 255, 180, 0  # yellow
            else:
                r, g, b = (88, 88, 88)
            color = (r, g, b, alpha)
            pygame.draw.circle(self.surf, color, (self.surf.get_width() // 2, self.surf.get_height() // 2), radius)
        
        screen.blit(self.surf, self.surf.get_rect(center=(self.x, self.y)))


class Flame:
    def __init__(self, x=SCREEN_WIDTH // 2, y=SCREEN_HEIGHT // 2, anim_speed=15):
        self.x = x
        self.y = y
        self.flame_intensity = 2
        self.flame_particles = []
        for i in range(self.flame_intensity * 25):
            self.flame_particles.append(
                FlameParticle(self.x + random.randint(-4, 4), self.y, 4+random.random()*3)
            )
            
        self.move_dt_threshold = 1.0/ anim_speed
        self.stacked_dur = 0.0
        self._cache = list()
    
    def update_flame(self, dt):
        self.stacked_dur += dt
        if self.stacked_dur > self.move_dt_threshold:
            self.stacked_dur = 0.0
            # animate by modifying particles
            del self._cache[:]
            for part_obj in self.flame_particles:
                part_obj.update()
                if part_obj.original_r > 0:
                    self._cache.append(part_obj)
                else:
                    self._cache.append(
                        FlameParticle(self.x + random.randint(-4, 4), self.y, 4+random.random()*3)
                    )
            # swap variable content
            tmp = self._cache
            self._cache = self.flame_particles
            self.flame_particles = tmp
    
    def draw_flame(self):
        for i in self.flame_particles:
            i.draw()


class EvChecker(kataen.EventReceiver):
    def __init__(self):
        super().__init__()
        self.paused=False
        self.last_t = time.time()
        
    def proc_event(self, ev, src):
        if ev.type == EngineEvTypes.LOGICUPDATE:
            if not self.paused:
                flames[0].update_flame(ev.curr_t-self.last_t)
                flames[1].update_flame(ev.curr_t-self.last_t)
                self.last_t = ev.curr_t
        elif ev.type == EngineEvTypes.PAINT:
            ev.screen.fill(BGCOLOR)
            for f in flames:
                f.draw_flame()
        elif ev.type == pygame.QUIT:
            self.pev(kataen.EngineEvTypes.GAMEENDS)
        elif ev.type == pygame.KEYDOWN and ev.key == pygame.K_SPACE:
            if self.paused:
                self.paused=False
                print('resume simulation -> ok')
            else:
                self.paused=True
                print('simulation paused')


def run_game():
    global flames, screen
    kataen.init(kataen.OLD_SCHOOL_MODE)
    screen = kataen.get_screen()
    flames = [
        Flame(x=SCREEN_WIDTH//2, y=Y_FIRE_POS, anim_speed=ANIM_SPEED),
        Flame(x=15+SCREEN_WIDTH//2, y=Y_FIRE_POS, anim_speed=ANIM_SPEED),
    ]
       
    ec = EvChecker()
    ec.turn_on()
    gctrl = kataen.get_game_ctrl()
    gctrl.turn_on()
    gctrl.loop()
    kataen.cleanup()


if __name__=='__main__':
    run_game()
