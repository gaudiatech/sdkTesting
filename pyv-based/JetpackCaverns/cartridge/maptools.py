from random import randint

from . import entity
from .core import audio
from .core import rumble


def get_adjacent_tiles(x, y):
    adj = [(x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)]
    return adj


def autotile(tilemap, tile):
    if tile[0] >= 0 and tile[0] <= tilemap.width - 1 and tile[1] >= 0 and tile[1] <= tilemap.height - 1:
        if 'dirt' in tilemap.layers['lower'].cells[tile].tile.properties:
            x = tile[0]
            y = tile[1]
            bw = 0
            if (y - 1) >= 0:
                if 'dirt' in tilemap.layers['lower'].cells[x, y - 1]:
                    bw += 1
            else:
                bw += 1
            if (x + 1) <= tilemap.width - 1:
                if 'dirt' in tilemap.layers['lower'].cells[x + 1, y]:
                    bw += 2
            else:
                bw += 2
            if (y + 1) <= tilemap.height - 1:
                if 'dirt' in tilemap.layers['lower'].cells[x, y + 1]:
                    bw += 4
            else:
                bw += 4
            if (x - 1) >= 0:
                if 'dirt' in tilemap.layers['lower'].cells[x - 1, y]:
                    bw += 8
            else:
                bw += 8
            for t in tilemap.tilesets:
                if 'dirt' in tilemap.tilesets[t].properties:
                    if bw == tilemap.tilesets[t].properties['dirt']:
                        newtile = tilemap.tilesets[t]
            tilemap.layers['lower'].cells[x, y].tile = newtile


def get_tile(tilemap):
    tw = tilemap.tile_width
    x = int(mouse_pos[0] / tw)
    y = int(mouse_pos[1] / tw)
    return x, y, tw


def highlight_tile(game):
    x, y, tw = get_tile(game)
    t = Surface((16, 16)).convert()
    t.fill((255, 255, 255))
    t.set_alpha(127)
    game.screenbuffer.blit(t, (x * tw, y * tw))


def breaktile(game, tilemap, x, y):
    # x, y, tw = get_tile(tilemap)
    l = tilemap.layers['lower']
    if (x, y) in l.cells:
        if 'dirt' in l.cells[x, y].tile.properties:
            game.scene.rumbler = rumble.Rumbler(power=2)
            s = randint(1, 3)
            audio.PlaySounds(game, game.sounds['sfx_explosion_00' + str(s)], 3)
            adj = get_adjacent_tiles(x, y)
            # print(l.cells[x,y].tile.gid)
            # l.cells[x,y].tile.gid = 3
            if 'sky' in l.cells[x, y - 1].tile.properties:
                l.cells[x, y].tile = tilemap.tilesets[4]
            else:
                l.cells[x, y].tile = tilemap.tilesets[3]
            for t in adj:
                autotile(tilemap, t)


def breakbattery(game, tilemap, x, y):
    cell = tilemap.layers['lower'].cells[x, y]
    cell.tile = tilemap.tilesets[3]
    game.scene.rumbler = rumble.Rumbler()
    s = randint(1, 3)
    audio.PlaySounds(game, game.sounds['sfx_explosion_00' + str(s)], 3)
    for j in range(8):
        entity.Effect(game, cell.rect.center, 'effect_explosion_003', game.scene.behind, angle=randint(0, 360), speed=4)
        entity.Effect(game, cell.rect.center, 'effect_explosion_004', game.scene.behind, angle=randint(0, 360), speed=4)
    adj = (
        (x - 1, y),
        (x + 1, y),
        (x, y - 1),
        (x, y + 1),
    )

    for t in adj:
        if t in tilemap.layers['lower'].cells:
            if 'timer' in tilemap.layers['lower'].cells[t].tile.properties:
                set_timer(tilemap.layers['lower'].cells[t])


def find_timers(tilemap):
    timers = tilemap.layers['lower'].find('timer')
    return timers


def set_timer(cell):
    cell['timer'] = 12


def pipe_timers(game, tilemap, timers):
    # cells = tilemap.layers['lower'].find('timer')
    for cell in timers:
        if int(cell['timer']) > 0:
            cell['timer'] -= 1
        elif int(cell['timer']) == 0:
            breakbattery(game, tilemap, cell.x, cell.y)
            cell['timer'] = -1


def breakpipe(game, tilemap, x, y):
    cell = tilemap.layers['lower'].cells[x, y]
    cell.tile = tilemap.tilesets[3]
    game.scene.rumblers.append(rumble.Rumbler(8, 8, 30))
    for x in range(8):
        entity.Effect(game, self.hitbox.center, 'effect_explosion_003', game.scene.behind, angle=randint(0, 360),
                      speed=4)
        entity.Effect(game, self.hitbox.center, 'effect_explosion_004', game.scene.behind, angle=randint(0, 360),
                      speed=4)
    adj = (
        (x - 1, y),
        (x + 1, y),
        (x, y - 1),
        (x, y + 1),
    )
    for t in adj:
        if t in tilemap.layers['lower'].cells:
            if 'pipe' in tilemap.layers['lower'].cells[t].tile.properties:
                breakpipe(tilemap, t[0], t[1])
