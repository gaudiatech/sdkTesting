# raycaster.py
import random
import katagames_sdk as katasdk
from BaseGame import BaseGame
from math import cos as cosinus
from math import sin as sinus
from math import radians as to_radians

kataen = katasdk.engine
pygame = kataen.import_pygame()


# class MyVector2(pygame.Vector2):
#     panic hotfix... OOPS! :-/ there are differences of implementation
#
#     def __init__(self, *args):
#         super().__init__(*args)
#
#     def rotate(self, degrees):
#         res = self.__class__(self)
#         res.rotate_ip(degrees)
#         return res
#
#     def rotate_ip(self, degrees):
#         theta = math.radians(degrees)
#         cs = math.cos(theta)
#         sn = math.sin(theta)
#         x = self.x * cs - self.y * sn
#         y = self.x * sn + self.y * cs
#         self.x = x
#         self.y = y


class MyVector2:
    # TODO pygame.Vector2 doesn't seem to be supported yet. So I made my own >:(

    def __init__(self, x, y=0.0):
        if isinstance(x, MyVector2):
            self.x = x.x
            self.y = x.y
        else:
            self.x = x
            self.y = y

    def __getitem__(self, idx):
        if idx == 0:
            return self.x
        else:
            return self.y

    def __len__(self):
        return 2

    def __iter__(self):
        return (v for v in (self.x, self.y))

    def __add__(self, other: 'MyVector2'):
        return MyVector2(self.x + other.x, self.y + other.y)

    def __sub__(self, other: 'MyVector2'):
        return MyVector2(self.x - other.x, self.y - other.y)

    def __mul__(self, other: float) -> 'MyVector2':
        return MyVector2(self.x * other, self.y * other)

    def __neg__(self):
        return MyVector2(-self.x, -self.y)

    def __eq__(self, other: 'MyVector2'):
        return self.x == other.x and self.y == other.y

    def __hash__(self):
        return hash((self.x, self.y))

    def rotate_ip(self, degrees):
        theta = to_radians(degrees)
        cs = cosinus(theta)
        sn = sinus(theta)
        x = self.x * cs - self.y * sn
        y = self.x * sn + self.y * cs
        self.x = x
        self.y = y

    def rotate(self, degrees) -> 'MyVector2':
        res = MyVector2(self)
        res.rotate_ip(degrees)
        return res

    def to_ints(self):
        return MyVector2(int(self.x), int(self.y))

    def length(self):
        a = self.x*self.x
        a += self.y*self.y
        if a:
            return a ** -0.5
        return 0.
    
    def length_squared(self):
        return self.x * self.x + self.y * self.y

    def scale_to_length(self, length):
        cur_length = self.length()
        if cur_length == 0 and length != 0:
            raise ValueError("Cannot scale vector with length 0")
        else:
            mult = length / cur_length
            self.x *= mult
            self.y *= mult


class RayEmitter:

    def __init__(self, xy, direction, fov, n_rays, max_depth=100):
        self.xy = xy
        self.direction = direction
        self.fov = fov
        self.n_rays = max(n_rays, 3)
        self.max_depth = max_depth

    def get_rays(self):
        left_ray = self.direction.rotate(-self.fov / 2)
        for i in range(self.n_rays):
            yield left_ray.rotate((i + 0.5) * self.fov / self.n_rays)


class RayCastPlayer(RayEmitter):

    def __init__(self, xy, direction, fov, n_rays, max_depth=100):
        super().__init__(xy, direction, fov, n_rays, max_depth=max_depth)
        self.move_speed = 75  # units per second
        self.turn_speed = 160

    def move(self, forward, strafe, dt):
        if forward != 0:
            self.xy = self.xy + self.direction * forward * self.move_speed * dt

        if strafe != 0:
            right = self.direction.rotate(90)
            self.xy = self.xy + right * strafe * self.move_speed * dt

    def turn(self, direction, dt):
        self.direction.rotate_ip(direction * self.turn_speed * dt)


class RayCastWorld:

    def __init__(self, grid_dims, cell_size, bg_color=(0, 0, 0)):
        self.grid = []
        for _ in range(grid_dims[0]):
            self.grid.append([None] * grid_dims[1])
        self.cell_size = cell_size
        self.bg_color = bg_color

    def randomize(self, chance=0.2, n_colors=5):
        colors = []
        for _ in range(n_colors):
            colors.append((random.randint(50, 255),
                           random.randint(50, 255),
                           random.randint(50, 255)))
        for xy in self.all_cells():
            if random.random() < chance:
                color = random.choice(colors)
                self.set_cell(xy, color)
        return self

    def set_cell(self, xy, color):
        self.grid[xy[0]][xy[1]] = color

    def get_cell(self, xy):
        return self.grid[xy[0]][xy[1]]

    def get_cell_coords_at(self, x, y):
        return int(x / self.cell_size), int(y / self.cell_size)

    def get_cell_value_at(self, x, y):
        coords = self.get_cell_coords_at(x, y)
        return self.get_cell(coords)

    def all_cells(self, in_rect=None):
        dims = self.get_dims()
        x_min = 0 if in_rect is None else max(0, int(in_rect[0] / self.cell_size))
        y_min = 0 if in_rect is None else max(0, int(in_rect[1] / self.cell_size))
        x_max = dims[0] if in_rect is None else min(dims[0], int((in_rect[0] + in_rect[2]) / self.cell_size) + 1)
        y_max = dims[1] if in_rect is None else min(dims[1], int((in_rect[1] + in_rect[3]) / self.cell_size) + 1)
        for x in range(x_min, x_max):
            for y in range(y_min, y_max):
                yield x, y

    def get_dims(self):
        if len(self.grid) == 0:
            return 0, 0
        else:
            return len(self.grid), len(self.grid[0])

    def get_size(self):
        dims = self.get_dims()
        return dims[0] * self.cell_size, dims[1] * self.cell_size

    def get_width(self):
        return self.get_size()[0]

    def get_height(self):
        return self.get_size()[1]


class RayState:
    """The state of a single ray."""

    def __init__(self, start, end, ray, color):
        self.start = start
        self.end = end
        self.ray = ray
        self.color = color

    def dist(self):
        if self.end is None:
            return float('inf')
        else:
            return (self.end - self.start).length()


class RayCastState:

    def __init__(self, player: RayCastPlayer, world: RayCastWorld):
        self.player = player
        self.world = world

        self.ray_states = []

    def update_ray_states(self):
        self.ray_states.clear()
        for ray in self.player.get_rays():
            self.ray_states.append(self.cast_ray(self.player.xy, ray, self.player.max_depth))

    def cast_ray(self, start_xy, ray, max_dist) -> RayState:
        # yoinked from https://theshoemaker.de/2016/02/ray-casting-in-2d-grids/
        dir_sign_x = ray[0] > 0 and 1 or -1
        dir_sign_y = ray[1] > 0 and 1 or -1

        tile_offset_x = (ray[0] > 0 and 1 or 0)
        tile_offset_y = (ray[1] > 0 and 1 or 0)

        cur_x, cur_y = start_xy[0], start_xy[1]
        tile_x, tile_y = self.world.get_cell_coords_at(cur_x, cur_y)
        t = 0

        grid_w, grid_h = self.world.get_dims()
        cell_size = self.world.cell_size

        max_x = start_xy[0] + ray[0] * max_dist
        max_y = start_xy[1] + ray[1] * max_dist

        if ray.length() > 0:
            while ((0 <= tile_x < grid_w and 0 <= tile_y < grid_h)
                   and (cur_x <= max_x if ray[0] >= 0 else cur_x >= max_x)
                   and (cur_y <= max_y if ray[1] >= 0 else cur_y >= max_y)):

                color_at_cur_xy = self.world.get_cell((tile_x, tile_y))
                if color_at_cur_xy is not None:
                    return RayState(start_xy, MyVector2(cur_x, cur_y), ray, color_at_cur_xy)

                dt_x = float('inf') if ray[0] == 0 else ((tile_x + tile_offset_x) * cell_size - cur_x) / ray[0]
                dt_y = float('inf') if ray[1] == 0 else ((tile_y + tile_offset_y) * cell_size - cur_y) / ray[1]

                if dt_x < dt_y:
                    t = t + dt_x
                    tile_x = tile_x + dir_sign_x
                else:
                    t = t + dt_y
                    tile_y = tile_y + dir_sign_y

                cur_x = start_xy[0] + ray[0] * t
                cur_y = start_xy[1] + ray[1] * t

        return RayState(start_xy, None, ray, None)


def lerp(v1, v2, a):
    if isinstance(v1, float) or isinstance(v1, int):
        return v1 + a * (v2 - v1)
    else:
        return tuple(lerp(v1[i], v2[i], a) for i in range(len(v1)))


def bound(v, lower, upper):
    if isinstance(v, float) or isinstance(v, int):
        if v > upper:
            return upper
        elif v < lower:
            return lower
        else:
            return v
    else:
        return tuple(bound(v[i], lower, upper) for i in range(len(v)))


def round_tuple(v):
    return tuple(round(v[i]) for i in range(len(v)))


def lerp_color(c1, c2, a):
    return bound(round_tuple(lerp(c1, c2, a)), 0, 255)


class RayCastRenderer:

    def __init__(self):
        pass

    @staticmethod
    def render(screen, state: RayCastState):
        p_xy = state.player.xy

        cs = state.world.cell_size
        screen_size = screen.get_size()
        cam_offs = MyVector2(-p_xy[0] + screen_size[0] // 2, -p_xy[1] + screen_size[1] // 2)

        bg_color = lerp_color(state.world.bg_color, (255, 255, 255), 0.05)

        for r in state.ray_states:
            color = r.color if r.color is not None else bg_color
            if r.end is not None:
                color = lerp_color(color, bg_color, r.dist() / state.player.max_depth)
                pygame.draw.line(screen, color, r.start + cam_offs, r.end + cam_offs, 2)
            else:
                end_point = r.start
                end_point += r.ray*state.player.max_depth
                end_point += cam_offs
                pygame.draw.line(screen, color, r.start + cam_offs, end_point, 2)

        camera_rect = [p_xy[0] - screen_size[0] // 2, p_xy[1] - screen_size[1] // 2, screen_size[0], screen_size[1]]

        for xy in state.world.all_cells(in_rect=camera_rect):
            color = state.world.get_cell(xy)
            if color is not None:
                r = [xy[0] * cs + cam_offs[0], xy[1] * cs + cam_offs[1], cs, cs]
                pygame.draw.rect(screen, color, r)


class RayCasterGame(BaseGame):

    def __init__(self):
        super().__init__()
        self.state = None
        self.renderer = RayCastRenderer()
        self.show_fps = True

    def _build_initial_state(self):
        w = RayCastWorld(self.get_screen_size(), 16).randomize()
        xy = MyVector2(w.get_width() / 2, w.get_height() / 2)
        direction = MyVector2(0, 1)
        p = RayCastPlayer(xy,
                          direction,
                          60,
                          18, max_depth=175)
        return RayCastState(p, w)

    def get_mode(self):
        return 'SUPER_RETRO'

    def update(self, events, dt):
        if self.state is None:
            self.state = self._build_initial_state()
        if self.get_tick() % 20 == 0:
            dims = self.get_screen_size()
            cap = "Raycaster (DIMS={}, FPS={:.1f})".format(dims, self.get_fps(logical=False))
            pygame.display.set_caption(cap)

        for e in events:
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_r:
                    print("Reseting!")
                    self.state = self._build_initial_state()

        pressed = pygame.key.get_pressed()

        turn = 0
        if pressed[pygame.K_q] or pressed[pygame.K_LEFT]:
            turn -= 1
        if pressed[pygame.K_e] or pressed[pygame.K_RIGHT]:
            turn += 1

        forward = 0
        if pressed[pygame.K_w] or pressed[pygame.K_UP]:
            forward += 1
        if pressed[pygame.K_s] or pressed[pygame.K_DOWN]:
            forward -= 1

        strafe = 0
        if pressed[pygame.K_a]:
            strafe -= 1
        if pressed[pygame.K_d]:
            strafe += 1

        self.state.player.turn(turn, dt)
        self.state.player.move(forward, strafe, dt)
        self.state.update_ray_states()

    def render(self, screen):
        screen.fill((0, 0, 0))
        self.renderer.render(screen, self.state)

        if self.show_fps:
            fps_text = "FPS {:.1f}".format(self.get_fps(logical=False))
            self.render_text(screen, fps_text, bg_color=(0, 0, 0), size=16)


# end of raycaster.py


# body of the program
def run_game():
    """Entry point for packaged web runs"""
    g = RayCasterGame()
    g.start()


if __name__ == '__main__':
    """Entry point for offline runs"""
    run_game()
