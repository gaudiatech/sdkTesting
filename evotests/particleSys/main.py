
"""
original code found in the project "Flyre" by CozyFractal
"""
from game import Game
import math
from math import cos, pi, sin
from random import choice, gauss, randint, random, uniform
from time import time
from typing import Callable, Generic, Tuple, TypeVar, Union
from utils import bounce, exp_impulse, random_in_rect

import katagames_sdk as katasdk
kataen = katasdk.engine

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

#kataen.init(kataen.HD_MODE)

DEGREES = float
VEC2D = Union[Tuple[float, float], Vector2]
P = TypeVar("P", bound="Particle")

radians = pi / 180

DEFAULT_FONT = None
frame = 0


##SNOW = pygame.image.fromstring(
##    b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00W\x84\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00W\x84\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00W\x84\x00W\x84\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00W\x84\x00W\x84\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00W\x841\xa2\xf2\x00W\x84\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00W\x841\xa2\xf2\x00W\x84\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00W\x841\xa2\xf21\xa2\xf2\x00W\x84\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00W\x841\xa2\xf21\xa2\xf2\x00W\x84\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00W\x84\x00\x00\x001\xa2\xf21\xa2\xf2\x00W\x84\x00\x00\x00\x00W\x841\xa2\xf21\xa2\xf2\x00\x00\x00\x00W\x84\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00W\x841\xa2\xf21\xa2\xf21\xa2\xf2\x00W\x84\x00\x00\x00\x00W\x841\xa2\xf21\xa2\xf21\xa2\xf2\x00W\x84\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00W\x841\xa2\xf2\x00\x00\x001\xa2\xf2\x00W\x84\x00\x00\x00\x00W\x841\xa2\xf2\x00\x00\x001\xa2\xf2\x00W\x84\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00W\x84\x00W\x84\x00W\x84\x00W\x84\x00W\x84\x00W\x84\x00W\x841\xa2\xf2\x00W\x841\xa2\xf21\xa2\xf2\x00W\x84\x00\x00\x00\x00W\x841\xa2\xf21\xa2\xf2\x00W\x841\xa2\xf2\x00W\x84\x00W\x84\x00W\x84\x00W\x84\x00W\x84\x00W\x84\x00\x00\x00\x00W\x841\xa2\xf21\xa2\xf2\x00\x00\x001\xa2\xf21\xa2\xf2\x00W\x841\xa2\xf2\x00W\x84\x00\x00\x00\x00W\x84\x00\x00\x00\x00W\x84\x00\x00\x00\x00W\x841\xa2\xf2\x00W\x841\xa2\xf2\x00\x00\x001\xa2\xf21\xa2\xf2\x00W\x84\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00W\x841\xa2\xf21\xa2\xf21\xa2\xf2\x00\x00\x001\xa2\xf2\x00W\x841\xa2\xf2\x00W\x84\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00W\x841\xa2\xf2\x00W\x841\xa2\xf2\x00\x00\x001\xa2\xf21\xa2\xf2\x00W\x84\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00W\x841\xa2\xf21\xa2\xf21\xa2\xf21\xa2\xf2\x00\x00\x00\x00W\x841\xa2\xf2\x00W\x84\x00W\x84\x00W\x841\xa2\xf2\x00W\x84\x00\x00\x001\xa2\xf21\xa2\xf21\xa2\xf2\x00W\x84\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00W\x84\x00W\x84\x00W\x84\x00W\x84\x00W\x84\x00\x00\x00\x00W\x84\x00\x00\x001\xa2\xf2\x00\x00\x00\x00W\x84\x00\x00\x00\x00W\x84\x00W\x84\x00W\x84\x00W\x84\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00W\x841\xa2\xf2\x00\x00\x001\xa2\xf2\x00W\x84\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00W\x84\x00W\x84\x00W\x84\x00W\x84\x00W\x84\x00\x00\x00\x00W\x84\x00\x00\x001\xa2\xf2\x00\x00\x00\x00W\x84\x00\x00\x00\x00W\x84\x00W\x84\x00W\x84\x00W\x84\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00W\x841\xa2\xf21\xa2\xf21\xa2\xf21\xa2\xf2\x00\x00\x00\x00W\x841\xa2\xf2\x00W\x84\x00W\x84\x00W\x841\xa2\xf2\x00W\x84\x00\x00\x001\xa2\xf21\xa2\xf21\xa2\xf2\x00W\x84\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00W\x841\xa2\xf21\xa2\xf21\xa2\xf2\x00\x00\x001\xa2\xf2\x00W\x841\xa2\xf2\x00W\x84\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00W\x841\xa2\xf2\x00W\x841\xa2\xf2\x00\x00\x001\xa2\xf21\xa2\xf2\x00W\x84\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00W\x841\xa2\xf21\xa2\xf2\x00\x00\x001\xa2\xf21\xa2\xf2\x00W\x841\xa2\xf2\x00W\x84\x00\x00\x00\x00W\x84\x00\x00\x00\x00W\x84\x00\x00\x00\x00W\x841\xa2\xf2\x00W\x841\xa2\xf2\x00\x00\x001\xa2\xf21\xa2\xf2\x00W\x84\x00\x00\x00\x00W\x84\x00W\x84\x00W\x84\x00W\x84\x00W\x84\x00W\x84\x00W\x841\xa2\xf2\x00W\x841\xa2\xf21\xa2\xf2\x00W\x84\x00\x00\x00\x00W\x841\xa2\xf21\xa2\xf2\x00W\x841\xa2\xf2\x00W\x84\x00W\x84\x00W\x84\x00W\x84\x00W\x84\x00W\x84\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00W\x841\xa2\xf21\xa2\xf21\xa2\xf2\x00W\x84\x00\x00\x00\x00W\x841\xa2\xf21\xa2\xf21\xa2\xf2\x00W\x84\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00W\x84\x00\x00\x001\xa2\xf21\xa2\xf2\x00W\x84\x00\x00\x00\x00W\x841\xa2\xf21\xa2\xf2\x00\x00\x00\x00W\x84\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00W\x841\xa2\xf21\xa2\xf2\x00W\x84\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00W\x841\xa2\xf21\xa2\xf2\x00W\x84\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00W\x841\xa2\xf2\x00W\x84\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00W\x841\xa2\xf2\x00W\x84\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00W\x84\x00W\x84\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00W\x84\x00W\x84\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00W\x84\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00W\x84\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00",
##    (24, 24),
##    "RGB",
##)


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
        """Spawn stars particles in the rectangle."""
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
            """Animate the color of the particle in hsv space.

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

        elif ev.type == pygame.MOUSEBUTTONDOWN:
            for _ in range(96):
                rd_angle = uniform(0, 360)
                p = CircleParticle().builder() \
                    .at(ev.pos, rd_angle) \
                    .velocity(gauss(10, 0.5)) \
                    .hsv(rd_angle) \
                    .anim_shrink() \
                    .anim_bounce_rect(((0, 0), SCR_SIZE)) \
                    .build()
                particles.add(p)




# -------------- add-on by Ghast --


class MyGame(Game):

    def get_mode(self):  # redef
        return 'hd'
    
    def start(self):  # redef
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
        # ----------
        
        global DEFAULT_FONT, SCR_SIZE
        global particles, gctrl, frame
        
        kataen.init(self._get_mode_internal())
        SCR_SIZE = self.get_screen_size()

        # display = pygame.display.set_mode(SIZE, )
        particles = ParticleSystem()

        # snow = SNOW
        # snow.set_colorkey((0, 0, 0))
        texts = [
            "Ahlan",
            "Asalaam alaikum",
            "Zdrasti",
            "Zdraveĭte",
            "Nǐ hǎo",
            "Nǐn hǎo",
            "Hallo",
            "Goede dag",
            "Hey",
            "Hello",
            "Salut",
            "Bonjour",
            "Hug",
            "Dia dhuit",
            "Hallo",
            "Guten tag",
            "Yasou",
            "Kalimera",
            "Shalom",
            "Shalom aleichem",
            "Hē",
            "Namastē",
            "Halló",
            "Góðan dag",
            "Salam!",
            "Selamat siang",
            "Ciao",
            "Salve",
            "Yā, _Yō",
            "Konnichiwa",
            "Suosdei",
            "Suostei",
            "Anyoung",
            "Anyoung haseyo",
            "Hej",
            "Cześć",
            "Cześć!",
            "Dzień dobry!",
            "Oi",
            "Olá",
            "Hei",
            "Bună ziua",
            "Privet",
            "Zdravstvuyte",
            "¿Qué tal?",
            "Hola",
            "Hujambo",
            "Habari",
            "Hej",
            "God dag",
            "Ia ora na",
            "Ia ora na",
            "Selam",
            "Merhaba",
            "Chào",
            "Xin chào",
            "Helo",
            "Shwmae",
            "Sawubona",
            "Ngiyakwemukela",
        ]
        DEFAULT_FONT = pygame.font.Font(None, 42)
        texts_surfs = [DEFAULT_FONT.render(text, 1, "white") for text in texts]

        def base(y):
            return lambda builder: (
                builder.at((-20, gauss(y, 10)), 0)
                    .velocity(gauss(8, 1), 0)
                    .sized(10)
                    .living(120)
                    .anim_shrink()
                    .anim_fade()
            )

        particles.fountains = [
            ParticleFountain(
                lambda: SquareParticle("#00a590").builder().apply(base(50)).build(),  #PolygonParticle(4, "#00a590", 3)
                1,
            ),

            ParticleFountain(
                lambda: CircleParticle("white")
                    .builder()
                    .at(pygame.mouse.get_pos(), gauss(90, 10))
                    .velocity(gauss(3, 0.5))
                    .anim_fade()
                    .build(),
                2,
            )
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

        # this list is the most important variable!
        li_recv = [
            kataen.get_game_ctrl(),
            self.__class__._GameViewController(self),
            UniqueRecv()
        ]
        for recv_obj in li_recv:
            recv_obj.turn_on()
        
        self.pre_update()

        li_recv[0].loop()
        kataen.cleanup()
    
    def render(self, screen):
        global particles
        screen.fill('antiquewhite3')#"#282832")
        particles.draw(screen)
        fps = self.get_fps()
        s = self.render_text(screen, f"FPS: {fps:.2f}  Particles: {len(particles)}", size=22)

    def update(self, events, dt):
        pass


############## main.py ##############

def run_game():
    """Entry point for packaged web runs"""
    o = MyGame()
    o.start()


if __name__ == '__main__':
    """Entry point for offline runs"""
    run_game()

############## main.py ##############
