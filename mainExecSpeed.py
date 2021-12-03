
import math
from math import cos, pi, sin
from random import choice, gauss, randint, random, uniform
from time import time
from typing import Callable, Generic, Tuple, TypeVar, Union
import time
import collections


"""
/!\ this is not original work written for the KataSDK
it is a modified version of a component found in the
game project "Flyre" (for more info. you can visit
https://cozyfractal.com) by CozyFractal#6978

Discord Community server:
https://discord.gg/ZuB2RySPRJ

--- --- ---
retro-compatibility support of this test:

         0.0.6    0.0.7
      --- --- --- --- -
local |   Y   |   Y    |
      |       |        |
      --- --- --- --- -
 web  |   Y   |   Y    |
      |       |        |
      --- --- --- --- -
"""

import katagames_sdk as katasdk
if katasdk.VERSION != '0.0.6':
    kataen = katasdk.engine
    pygame = kataen.pygame

else:
    import katagames_sdk.engine as kataen
    pygame = kataen.import_pygame()


EventReceiver = kataen.EventReceiver
EngineEvTypes = kataen.EngineEvTypes


def bounce(x, f=0.2, k=60):
    """Easing function that bonces over 1 and then stabilises around 1.
    Graph:
         │   /^\
        1│  /   `------
        0│ /
         ┼———————————————
           0 f        1
    Args:
        x: The time to animate, usually between 0 and 1, but can be greater than one.
        f: Time to grow to 1
        k: Strength of the bump after it has reached 1
    """
    s = max(x - f, 0.0)
    return min(x * x / (f * f), 1 + (2.0 / f) * s * exp(-k * s))


def random_in_rect(rect: pygame.Rect, x_range=(0.0, 1.0), y_range=(0.0, 1.0)):
    """
    Return a random point inside a rectangle.
    If x_range or y_range are given, they are interpreted as relative to the size of the rectangle.
    For instance, a x_range of (-1, 3) would make the x range in a rectangle that is 3 times wider,
    but still centered at the same position. (-2, 1) you expand the rectangle twice its size on the
    left.
    """
    w, h = rect.size

    return (
        uniform(rect.x + w * x_range[0], rect.x + w * x_range[1]),
        uniform(rect.y + h * y_range[0], rect.y + h * y_range[1]),
    )


def exp_impulse(x, k):
    """
    Easing function that rises quickly to one and slowly goes back to 0.

    Graph:
        1│   /^\
         │  /    \
        0│ /      `-_
         ┼————┼——————————
           0  │    1
              ╰ 1/k

    Args:
        x: The time to animate, usually between 0 and 1, but can be greater than one.
        k: Control the stretching of the function

    Returns: a float between 0 and 1.
    """
    h = k * x
    return h * exp(1.0 - h)


pygame = kataen.import_pygame()
Vector2 = pygame.Vector2
gfxd = kataen.import_gfxdraw()
SCR_SIZE = None
particles = gctrl = frame = None
EventReceiver = kataen.EventReceiver

__all__ = [
    "ParticleSystem",
    "ParticleFountain",
    "Particle",
    "DrawnParticle",
    "PolygonParticle",
    "ImageParticle",
    "CircleParticle",
    "LineParticle",
    "SquareParticle",
    "ShardParticle",
]

DEGREES = float
VEC2D = Union[Tuple[float, float], Vector2]
P = TypeVar("P", bound="Particle")
radians = pi / 180
DEFAULT_FONT = None
frame = 0


def clamp(x, mini=0.0, maxi=1.0):
    if x < mini:
        return mini
    if x > maxi:
        return maxi
    return x


def vec2int(vec):
    return (int(vec[0]), int(vec[1]))


def polar(r, phi: DEGREES):
    v = Vector2()
    v.from_polar((r, phi))
    return v


def rrange(nb: float):
    qte = int(nb)
    proba = nb - qte
    if random() < proba:
        return range(qte + 1)
    return range(qte)


def rand2d(vec):
    return (uniform(0, vec[0]), uniform(0, vec[1]))


class ParticleSystem(set):
    fountains: "List[ParticleFountain]"

    def __init__(self):
        super().__init__()
        self.fountains = []

    def logic(self):
        """Update all the particle for the frame."""

        for fountain in self.fountains:
            fountain.logic(self)

        dead = set()
        for particle in self:
            particle.logic()
            if not particle.alive:
                dead.add(particle)

        self.difference_update(dead)

    def draw(self, surf: pygame.Surface):
        """Draw all the particles"""

        for particle in self:
            particle.draw(surf)

    def add_fire_particle(self, pos, angle):
        self.add(
            SquareParticle()
                .builder()
                .at(pos, gauss(angle, 10))
                .velocity(gauss(1, 0.1))
                .sized(uniform(1, 5))
                .living(30)
                .hsv(gauss(20, 20), gauss(1, 0.1))
                .anim_fade()
                .build()
        )


class ParticleFountain:
    def __init__(
            self, particle_generator: Callable[[], "Particle"], frequency=1.0,
    ):
        self.generator = particle_generator
        self.frequency = frequency

    def logic(self, system):
        for _ in rrange(self.frequency):
            system.add(self.generator())

    @classmethod
    def stars(cls, rect):
        """
        Spawn stars particles in the rectangle
        """
        return cls(
            lambda: SquareParticle("white")
                .builder()
                .at(random_in_rect(rect), 90)
                .velocity(0.2)
                .living(6 * 60)
                .sized(uniform(1, 3))
                .anim_blink()
                .build(),
            0.2,
        )


class Particle:
    def __init__(self):
        self.pos = Vector2(0, 0)

        self.speed = 3.0
        self.angle = -90
        self.acc = 0.0
        self.angle_vel = 0.0
        self.size = 10.0
        self.lifespan = 60
        self.constant_force = Vector2()

        self.inner_rotation = 0
        self.inner_rotation_speed = 0
        self.alpha = 255

        self.life_prop = 0.0
        self.alive = True
        self.animations = []

    # Builder methods

    class Builder(Generic[P]):
        def __init__(self, particle: P):
            self._p: P = particle

        def at(self, pos: VEC2D, angle: DEGREES = 0):
            """
            Set the initial conditions.

            Args:
                pos: 2D position in pixels
                angle: initial target in degrees
            Returns:
                The particle being build.
            """
            self._p.pos = Vector2(pos)
            self._p.angle = angle
            return self

        def velocity(self, speed: float, radial_velocity: DEGREES = 0):
            """Speed is along the target, and radial_velocity is how fast this target changes.

            Args:
                speed: px/frame along the target
                radial_velocity: degrees/frame of angle change
            """
            self._p.speed = speed
            self._p.angle_vel = radial_velocity
            return self

        def constant_force(self, velocity: Vector2):
            """Add the given velocity to the particle's postion every frame."""

            self._p.constant_force = velocity
            return self

        def acceleration(self, directional: float):
            """Set the acceleration along the target and the angular acceleration"""
            self._p.acc = directional
            return self

        def inner_rotation(self, start: DEGREES, speed: DEGREES):
            """Set the rotation of the particle. This does not affect its motion."""
            self._p.inner_rotation = start
            self._p.inner_rotation_speed = speed
            return self

        def sized(self, size: float):
            """Set the radius of the particle."""
            self._p.size = size
            return self

        def living(self, lifespan: int):
            """Set how many frames the particle will be alive."""
            self._p.lifespan = lifespan
            return self

        def anim(self, animation: Callable[[P], None]):
            self._p.animations.append(animation)
            return self

        def anim_fade(self, fade_start=0):
            def fade(particle):
                if particle.life_prop < fade_start:
                    return
                t = (particle.life_prop - fade_start) / (1 - fade_start)
                alpha = int(255 * (1 - t))
                particle.alpha = alpha

            return self.anim(fade)

        def anim_blink(self, up_duration=0.5, pow=2):
            def blink(particle):
                if particle.life_prop < up_duration:
                    a = particle.life_prop / up_duration
                else:
                    a = (1 - particle.life_prop) / (1 - up_duration)
                # a = 1 - abs(1 - 2 * particle.life_prop)
                particle.alpha = int(255 * a ** pow)

            return self.anim(blink)

        def anim_bounce_rect(self, rect):
            """Make the particle bounce inside of the rectangle."""

            rect = pygame.Rect(rect)

            def bounce_rect(particle):
                angle = particle.angle % 360
                if particle.pos.x - particle.size < rect.left and 90 < angle < 270:
                    particle.angle = 180 - angle
                elif particle.pos.x + particle.size > rect.right and (
                        angle < 90 or angle > 270
                ):
                    particle.angle = 180 - angle

                angle = particle.angle % 360
                if particle.pos.y - particle.size < rect.top and angle > 180:
                    particle.angle = -angle
                elif particle.pos.y + particle.size > rect.bottom and angle < 180:
                    particle.angle = -angle

            return self.anim(bounce_rect)

        def anim_shrink(self):
            initial_size = self._p.size

            def shrink(particle):
                particle.size = initial_size * (1 - particle.life_prop)

            return self.anim(shrink)

        def anim_bounce_size(self, increase_duration=0.3, k=10):
            initial_size = self._p.size

            def bounce_size(particle):
                particle.size = (
                        bounce(particle.life_prop, increase_duration, k) * initial_size
                )

            return self.anim(bounce_size)

        def anim_bounce_size_and_shrink(self, stretch=5):
            initial_size = self._p.size

            def bounce_size_and_shrink(particle):
                particle.size = exp_impulse(particle.life_prop, stretch) * initial_size

            return self.anim(bounce_size_and_shrink)

        def apply(self, func):
            """Call a building function on the particle. Useful to factor parts of the build."""
            func(self)
            return self

        def build(self) -> P:
            return self._p

    def builder(self):
        return self.Builder(self)

    # Actual methods

    def logic(self):
        """Update the attributes of the particle."""

        self.life_prop += 1 / self.lifespan
        self.speed += self.acc
        self.angle += self.angle_vel
        self.pos += (
            cos(self.angle * radians) * self.speed,
            sin(self.angle * radians) * self.speed,
        )
        self.pos += self.constant_force

        self.inner_rotation += self.inner_rotation_speed

        if self.speed < 0 or self.size <= 0 or self.life_prop >= 1:
            self.alive = False
        else:
            for anim in self.animations:
                anim(self)

    def draw(self, surf):
        raise NotImplementedError()


class DrawnParticle(Particle):
    def __init__(self, color=None):
        self.color = pygame.Color(color or 0)
        super().__init__()

    @property
    def alpha(self):
        return self.color.a

    @alpha.setter
    def alpha(self, value: int):
        self.color.a = value

    class Builder(Particle.Builder["DrawnParticle"]):
        def hsv(self, hue, saturation=1.0, value=1.0):
            hue = round(hue) % 360
            saturation = clamp(0, 100, round(100 * saturation))
            value = clamp(0, 100, round(100 * value))
            self._p.color.hsva = (hue, saturation, value, 100)
            return self

        def anim_gradient_to(self, h0, s0, v0, h1, v1, s1):
            """
            Animate the color of the particle in hsv space.
            Animations of the transparency should come after this one
            """

            # h0, s0, v0, a = self._p.color.hsva
            # h1 = h if h is not None else h0
            # s1 = clamp(s) * 100 if s is not None else s0
            # v1 = clamp(v) * 100 if v is not None else v0

            def gradient_to(particle):
                p = 1 - particle.life_prop
                t = particle.life_prop

                h = int(p * h0 + t * h1) % 360
                s = int(100 * (p * s0 + t * s1))
                v = int(100 * (p * v0 + t * v1))
                r = h, s, v, 100
                particle.color.hsva = r

            return self.anim(gradient_to)

    def builder(self):
        # the method is here only for type hinting
        return self.Builder(self)


class CircleParticle(DrawnParticle):
    def __init__(self, color=None, filled=True):
        super().__init__(color)
        self.filled = filled

    def draw(self, surf):
        if self.color.a < 255:
            if self.filled:
                gfxd.filled_circle(
                    surf, int(self.pos.x), int(self.pos.y), int(self.size), self.color
                )
            else:
                gfxd.circle(
                    surf, int(self.pos.x), int(self.pos.y), int(self.size), self.color
                )
        else:
            pygame.draw.circle(surf, self.color, self.pos, self.size, 1 - self.filled)


class SquareParticle(DrawnParticle):
    def draw(self, surf):
        pos = self.pos - (self.size / 2, self.size / 2)
        if self.color.a < 255:
            gfxd.box(surf, (pos, (self.size, self.size)), self.color)
        else:
            pygame.draw.rect(surf, self.color, (pos, (self.size, self.size)))


class PolygonParticle(DrawnParticle):
    def __init__(self, vertices: int, color=None, vertex_step: int = 1):
        """
        A particle shaped in a regular polygon.
        
        Args:
            vertices: number of vertices
            color: 
            vertex_step: order in which to draw the vertices.
                This can be used to draw star shaped pattern.
                Rhe order will be 1, 1+step, 1+2*step...
                should be coprime with vertices.
        """

        super().__init__(color)
        self.vertex_step = vertex_step
        self.vertices = vertices

    def draw(self, surf):
        points = [
            self.pos
            + polar(
                self.size,
                self.inner_rotation + i * 360 / self.vertices * self.vertex_step,
            )
            for i in range(self.vertices)
        ]

        gfxd.filled_polygon(surf, points, self.color)


class ShardParticle(DrawnParticle):
    def __init__(self, color=None, head=1, tail=3):
        """A shard shaped particle, inspired from DaFluffyPtato.

        The size of lateral size is given by the particle's size,
        and :head: and :tail: are the length of the head and tail
        compared to the side.
        """

        super().__init__(color)
        self.tail = tail
        self.head = head

    def draw(self, surf):
        vel = polar(self.speed, self.angle)
        vel.scale_to_length(self.size)
        cross = Vector2(-vel.y, vel.x)

        points = [
            self.pos + vel * self.head,
            self.pos + cross,
            self.pos - vel * self.tail,
            self.pos - cross,
        ]

        gfxd.filled_polygon(surf, points, self.color)


class LineParticle(DrawnParticle):
    def __init__(self, length, color=None, width=1):
        self.length = length
        self.width = width
        super().__init__(color)

    def draw(self, surf):
        end = vec2int(self.pos - polar(self.length, self.angle))
        start = vec2int(self.pos)
        gfxd.line(surf, *start, *end, self.color)


class ImageParticle(Particle):
    def __init__(self, surf: pygame.Surface):
        self._alpha = 255
        self.original_surf = surf
        self.need_redraw = True
        self.surf = pygame.Surface((1, 1))

        super().__init__()

        self.size = min(self.original_surf.get_size())

    @property
    def alpha(self):
        return self._alpha

    @alpha.setter
    def alpha(self, value: int):
        self._alpha = value
        self.surf.set_alpha(value)

    def redraw(self):
        self.need_redraw = False
        w, h = self.original_surf.get_size()
        ratio = self.size / min(w, h)
        surf = pygame.transform.scale(
            self.original_surf, vec2int((w * ratio, h * ratio))
        )

        surf.set_alpha(self.alpha)
        return surf

    def draw(self, surf: pygame.Surface):
        if self.need_redraw:
            self.surf = self.redraw()

        surf.blit(self.surf, self.surf.get_rect(center=self.pos))

    def logic(self):
        last_size = self.size
        super(ImageParticle, self).logic()
        if int(last_size) != int(self.size):
            self.need_redraw = True


class UniqueRecv(kataen.EventReceiver):
    def __init__(self):
        super().__init__()
        self.do_logic = True
        
    def proc_event(self, ev, source):
        global frame, particles, gctrl, DEFAULT_FONT, SCR_SIZE

        if ev.type == kataen.EngineEvTypes.LOGICUPDATE:
            frame += 1
            if self.do_logic:
                particles.logic()

        elif ev.type == pygame.QUIT:
            self.pev(kataen.EngineEvTypes.GAMEENDS)

        elif ev.type == pygame.KEYDOWN:
            key = ev.key
            if key in (pygame.K_q, pygame.K_ESCAPE):
                self.pev(kataen.EngineEvTypes.GAMEENDS)
            elif key == pygame.K_SPACE:
                self.do_logic = not self.do_logic

        if ev.type == pygame.MOUSEBUTTONDOWN:
            for _ in range(64):
                rd_angle = uniform(0, 360)
                # /!\ need to take care of upscaling x2
                p = CircleParticle().builder() \
                    .at((ev.pos[0], ev.pos[1]), rd_angle) \
                    .velocity(gauss(3, 0.33)) \
                    .hsv(rd_angle) \
                    .sized(5) \
                    .anim_shrink() \
                    .anim_bounce_rect(((0, 0), SCR_SIZE)) \
                    .build()
                particles.add(p)


class Game:
    """
    Base class (helper)
    for writing a pygame game that can
    ALSO run in the web context
    """
    def __init__(self, track_fps=True):
        self._fps_n_frames = 16 if track_fps else 0
        
        self._fps_tracker_logic = collections.deque()
        self._fps_tracker_rendering = collections.deque()
        self._tick = 0

        self._cached_info_text = None
        self._info_font = None

        self._li_recv = list()
        self._manager = None

        # cached events
        self.lu_ev = kataen.CgmEvent(kataen.EngineEvTypes.LOGICUPDATE, curr_t=None)
        self.paint_ev = kataen.CgmEvent(kataen.EngineEvTypes.PAINT, screen=None)

    # N.B. can launch this in web ctx
    def base_pre_update(self):
        kataen.init(self._get_mode_internal())
        self._li_recv.append(kataen.get_game_ctrl())
        self._li_recv.extend(self.provide_receivers())
        self.pre_update()

        for recv_obj in self._li_recv:
            recv_obj.turn_on()
        self._manager = kataen.get_manager()
        self.paint_ev.screen = kataen.get_screen()

    # N.B. useful only in web ctx
    def update_game(self, infot=None):
        self.lu_ev.curr_t = infot
        self._manager.post(self.lu_ev)
        self._manager.post(self.paint_ev)
        self._manager.update()
    
    def start(self):
        """
        Starts the game loop
        This method will not exit until the game has finished execution...
        It is NOT used in the web ctx and should never be called
        """
        
        self.base_pre_update()
        
        self._li_recv[0].loop()
        
        kataen.cleanup()
    
    def get_mode(self) -> str:
        """returns: "HD', 'OLD_SCHOOL', or 'SUPER_RETRO'"""
        return 'OLD_SCHOOL'

    def is_running_in_web(self) -> bool:
        return kataen.runs_in_web()

    def get_screen_size(self):
        return kataen.get_screen().get_size()

    def get_tick(self) -> int:
        return self._tick

    def pre_update(self):
        pass

    def render(self, screen):
        raise NotImplementedError()

    def update(self, events, dt):
        raise NotImplementedError()

    def render_text(self, screen, text, size=12, pos=(0, 0), color=(255, 255, 255), bg_color=None):
        if self._info_font is None or self._info_font.get_height() != size:
            self._info_font = pygame.font.Font(None, size)
        lines = text.split("\n")
        y = pos[1]
        for l in lines:
            surf = self._info_font.render(l, True, color, bg_color)
            screen.blit(surf, (pos[0], y))
            y += surf.get_height()

    def get_fps(self, logical=True) -> float:
        q = self._fps_tracker_logic if logical else self._fps_tracker_rendering
        if len(q) <= 1:
            return 0
        else:
            total_time_secs = q[-1] - q[0]
            n_frames = len(q)
            if total_time_secs <= 0:
                return float('inf')
            else:
                return (n_frames - 1) / total_time_secs

    def _render_internal(self, screen):
        if self._fps_n_frames > 0:
            self._fps_tracker_rendering.append(time.time())
            if len(self._fps_tracker_rendering) > self._fps_n_frames:
                self._fps_tracker_rendering.popleft()
        self.render(screen)

    def _update_internal(self, events, dt):
        if self._fps_n_frames > 0:
            self._fps_tracker_logic.append(time.time())
            if len(self._fps_tracker_logic) > self._fps_n_frames:
                self._fps_tracker_logic.popleft()
        self.update(events, dt)
        self._tick += 1

    def _get_mode_internal(self):
        mode_str = self.get_mode().upper()
        if mode_str == 'HD':
            return kataen.HD_MODE
        elif mode_str == 'OLD_SCHOOL':
            return kataen.OLD_SCHOOL_MODE
        elif mode_str == 'SUPER_RETRO':
            return kataen.SUPER_RETRO_MODE
        else:
            raise ValueError("Unrecognized mode: {}".format(mode_str))

    class _GameViewController(EventReceiver):
        def __init__(self, game):
            super().__init__()
            self._game = game
            self._event_queue = []
            self._last_update_time = time.time()

        def proc_event(self, ev, source):
            if ev.type == EngineEvTypes.PAINT:
                self._game._render_internal(ev.screen)
            elif ev.type == EngineEvTypes.LOGICUPDATE:
                cur_time = ev.curr_t
                self._game._update_internal(self._event_queue, cur_time - self._last_update_time)
                self._last_update_time = cur_time
                self._event_queue.clear()
            else:
                self._event_queue.append(ev)

    def provide_receivers(self):  # retuns list of EventReceiver obj
        return [Game._GameViewController(self)]


class ParticleSystemTester(Game):

    def get_mode(self):  # redef
        return 'old_school'
    
    def pre_update(self):
        global DEFAULT_FONT, SCR_SIZE
        global particles, gctrl, frame
        
        SCR_SIZE = (960//2,540//2)  # TODO can we retrieve this from kataen
        # but before init?

        particles = ParticleSystem()
        DEFAULT_FONT = pygame.font.Font(None, 42)
        
        def base(y):
            return lambda builder: (
                builder.at((SCR_SIZE[0] // 2, gauss(y, 10)), 0)
                .velocity(2 + gauss(3, 0), gauss(5, 1))
                .sized(3)
                .living(64)
                .anim_fade()
            )
        particles.fountains = [
            ParticleFountain(
                lambda: PolygonParticle(3, "navyblue").builder().apply(base(32)).build(),  # SquareParticle("#00a590")
                1,
            ),
        ]
        vtest = Vector2()
        print(vtest)
        vtest.from_polar((1.4, math.pi / 2))
        print(vtest)
        m = vtest * 3
        print(m)
        jj = m - Vector2((3, 6))
        print(jj)
        print('---------')
        print(pygame.Color(37) - pygame.Color((87, 11, 13, 25)))
        tmptmp = pygame.Color('navyblue')-pygame.Color(88)
        print(tmptmp.b, tmptmp.a)
        w = pygame.Color('white')
        print(w)
        w.hsva = (30, 78, 95, 25)
        print(w)

        print('- - - Mouse click will add more particles! - - -')
        print('- - - SPACE key will pause the simulation - - -')

    def provide_receivers(self):
        t = super().provide_receivers()
        t.append(UniqueRecv())
        return t
    
    def render(self, screen):
        global particles
        screen.fill('antiquewhite3')
        particles.draw(screen)

        fps = self.get_fps()

        self.render_text(screen, f"FPS: {fps:.2f}  Particles: {len(particles)}", size=22)

    def update(self, events, dt):
        pass


if __name__ == '__main__':
    """Entry point for out-of-the-browser execution"""
    pt_obj = ParticleSystemTester()
    pt_obj.start()


# bridge for webctx if the Game cls is used...
if kataen.runs_in_web():
    if katasdk.version == '0.0.6':
        def run_game():
            pt_obj = ParticleSystemTester()
            pt_obj.start()
    else:
        pt_obj = ParticleSystemTester()
        @katasdk.web_entry_point
        def we():
            pt_obj.base_pre_update()
        @katasdk.web_animate
        def wa(infot):
            pt_obj.update_game(infot)
