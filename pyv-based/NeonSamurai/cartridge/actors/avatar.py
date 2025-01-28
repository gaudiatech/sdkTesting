import time
from .. import glvars
import math
from ..glvars import pyv


POST_RELEASE_DELAY = 0.05  # sec
AV_SPEED = 3  # world units per second

# - later on, you need to use the real isometric engine
TILE_W, TILE_H = 64, 32


def map_to_screen_iso(wx, wy):
    a = (wx - wy) * (TILE_W/2)
    b = (wx + wy) * (TILE_H/2)
    return a, b


def new_avatar():
    anims_description = {}
    # example of another "anims_description"
    # that would work well in another game, with another spite sheet:
    # {
    #   "idle": {"set": "0-5", "delay": 100},
    #   "attack": {"set": [6,7,8,9,10,11], "delay": 250}
    # }
    tmp_info = {"default_anim": dict(set=[f"frame{n}.png" for n in range(26)], delay=142)}  # delay= nb ms per frame
    tmp_a, tmp_b = pyv.vars.screen.get_size()
    anim_spr = pyv.gfx.AnimatedSprite(  # this line shows you how to use animated sprites!
        (0, 0),  # position x,y
        pyv.vars.spritesheets['GreatSwordKnight_2hIdle5_dir1'],  # first argument is a sprite sheet
        # the description of animations in case we have several in 1 sprsheet
        tmp_info
    )
    anim_spr.play('default_anim')
    spr_size = anim_spr.rect[-2:]
    anim_spr.rect.center = tmp_a//2, tmp_b//2
    xpos, ypos = anim_spr.rect.topleft

    data = {
        'recent_input_cmd': False,
        'last_ev': None,  # to store date of the the last meaningful ev
        'w_x': 0, 'w_y': 0,

        'org_x': xpos, 'org_y': ypos,  # to keep info about the center of the screen
        'scr_x': xpos, 'scr_y': ypos,  # will be updated in real-time

        'last_tick': None,  # to measure time
        "infos_anim": {
            "idle_dir1": tmp_info,
            "idle_dir2": tmp_info,
            "idle_dir3": tmp_info,
            "idle_dir4": tmp_info,
            "idle_dir5": tmp_info,
            "idle_dir6": tmp_info,
            "idle_dir7": tmp_info,
            "idle_dir8": tmp_info,

            "walk_dir1": {"default_anim": dict(set=[f"frame{n}.png" for n in range(9)], delay=142)},
            "walk_dir2": {"default_anim": dict(set=[f"frame{n}.png" for n in range(9)], delay=142)},
            "walk_dir3": {"default_anim": dict(set=[f"frame{n}.png" for n in range(9)], delay=142)},
            "walk_dir4": {"default_anim": dict(set=[f"frame{n}.png" for n in range(9)], delay=142)},
            "walk_dir5": {"default_anim": dict(set=[f"frame{n}.png" for n in range(9)], delay=142)},
            "walk_dir6": {"default_anim": dict(set=[f"frame{n}.png" for n in range(9)], delay=142)},
            "walk_dir7": {"default_anim": dict(set=[f"frame{n}.png" for n in range(9)], delay=142)},
            "walk_dir8": {"default_anim": dict(set=[f"frame{n}.png" for n in range(9)], delay=142)}
        },
        'anim_sprite': anim_spr,
        'x_mvt': 0,
        'y_mvt': 0,
        'direction': 'sw',  # South-West
        'moving': False,
        "curr_anim_id": "idle_dir1"
    }

    # start animation
    data['anim_sprite'].play("default_anim")

    def _util_update_anim(this):
        prefix = this.curr_anim_id[:4]
        suffix = this.curr_anim_id[-4:]

        part0 = {  # use a mapping
            "idle": 'GreatSwordKnight_2hIdle5',
            "walk": 'GreatSwordKnight_2hWalk'
        }[prefix]
        sprsheet_name = part0 + '_' + suffix
        print('>>>>', sprsheet_name)

        print('...Now using spritesheet identified by:', sprsheet_name)
        print('injecting infos for the anim:', this.curr_anim_id)
        this.anim_sprite = pyv.gfx.AnimatedSprite(
            (this.scr_x, this.scr_y),  # x and y position
            pyv.vars.spritesheets[sprsheet_name],  # first argument is a sprite sheet
            this.infos_anim[this.curr_anim_id]
        )
        # since anim has restarted we MUST use the two lines below,
        # otherwise the update event will break the animation cls
        this.last_tick = None
        this.anim_sprite.play("default_anim")

    def _test_dir_change(this):
        """
        goal= take into account both x_mvt and y_mvt in order to update 3 attributes:
        - this.direction
        - this.moving
        - curr_anim_id
        """

        if this.x_mvt == 0 and this.y_mvt == 0:
            moving = False
            # select the idle anim based on the latest known movement
            new_direction = this.direction
        else:
            moving = True
            if this.x_mvt == 1:
                if this.y_mvt == 1:
                    new_direction = 'se'
                elif this.y_mvt == -1:
                    new_direction = 'ne'
                else:
                    new_direction = 'e'
            elif this.x_mvt == -1:
                if this.y_mvt == 1:
                    new_direction = 'sw'
                elif this.y_mvt == -1:
                    new_direction = 'nw'
                else:
                    new_direction = 'w'
            else:  # thus, x_mvt is zero
                if this.y_mvt == 1:
                    new_direction = 's'
                elif this.y_mvt == -1:
                    new_direction = 'n'

        mapcode_to_int = {
            'sw': 1, 'w': 2, 'nw': 3, 'n': 4, 'ne': 5, 'e': 6, 'se': 7, 's': 8
        }
        if this.moving and (not moving):  # stopped going forward
            this.moving = False
            this.curr_anim_id = 'idle_dir' + str(mapcode_to_int[this.direction])
            _util_update_anim(this)
            return

        if (moving and not this.moving) or this.direction != new_direction:
            this.moving = True
            this.curr_anim_id = 'walk_dir' + str(mapcode_to_int[new_direction])
            this.direction = new_direction
            _util_update_anim(this)

    # -----------------
    #  behavior
    # -----------------
    def on_av_input(this, ev):
        if 'left_pressed' == ev.k and this.x_mvt != 1:
            this.x_mvt = -1
        if 'right_pressed' == ev.k and this.x_mvt != -1:
            this.x_mvt = 1
        if 'left_released' == ev.k:
            this.x_mvt = 0
        if 'right_released' == ev.k:
            this.x_mvt = 0
        if 'up_pressed' == ev.k and this.y_mvt != 1:
            this.y_mvt = -1
        if 'down_pressed' == ev.k and this.y_mvt != -1:
            this.y_mvt = 1
        if 'up_released' == ev.k:
            this.y_mvt = 0
        if 'down_released' == ev.k:
            this.y_mvt = 0
        this.recent_input_cmd = True
        this.last_ev = time.time()

    # - behavior
    # def on_anim_swap(this, ev):
    #     if this.curr_anim_id == "idle_dir1":
    #         new_aid = this.curr_anim_id = "walk_dir1"
    #     else:
    #         new_aid = this.curr_anim_id = "idle_dir1"
    #     _util_update_anim(this)

    def on_update(this, ev):
        delta_t = 0 if (this.last_tick is None) else ev.curr_t - this.last_tick
        this.anim_sprite.update(delta_t)

        # has to update all animations
        this.curr_t = ev.curr_t
        if this.recent_input_cmd:
            elapsed_since_r = ev.curr_t - this.last_ev
            if elapsed_since_r > POST_RELEASE_DELAY:
                this.recent_input_cmd = False
        else:
            _test_dir_change(this)

        # update players position in world

        # to avoid speedhacking when going diagonally, we have to calculate the magnitude
        # of the movement vector, then normalize movement speed to ensure consistency
        # and use that speed instead of the raw value AV_SPEED

        if this.moving:
            # Define a mapping of (mvt_x, mvt_y) to (x_offset, y_offset)
            movement_offsets = {
                (0, -1): (-1, -1),  # UP
                (0, 1): (1, 1),  # DOWN
                (-1, 0): (-1, 1),  # LEFT
                (1, 0): (1, -1),  # RIGHT
                (1, 1): (1, 0),  # DOWN + RIGHT
                (-1, -1): (-1, 0),  # UP + LEFT
                (1, -1): (0, -1),  # UP + RIGHT
                (-1, 1): (0, 1),  # DOWN + LEFT
            }
            # Get the offsets for the current movement direction
            offset = movement_offsets.get((this.x_mvt, this.y_mvt), (0, 0))
            magnitude = math.sqrt(offset[0] ** 2 + offset[1] ** 2)

            # warning:
            # magnitude can still be 0 although we have moving==True,
            # because x_mvt and y_mvt are updated faster
            if magnitude != 0:
                normalized_speed = AV_SPEED / magnitude

                # Apply the offsets to the world coordinates
                this.w_x += delta_t * normalized_speed * offset[0]
                this.w_y += delta_t * normalized_speed * offset[1]

                print('new w_coords->', this.w_x, this.w_y)
                a, b = map_to_screen_iso(this.w_x, this.w_y)
                this.scr_x = this.org_x + a
                this.scr_y = this.org_y + b
                this.anim_sprite.rect.topleft = this.scr_x, this.scr_y

        # save date of the current tick
        this.last_tick = ev.curr_t

    def on_draw(this, ev):
        scr = ev.screen
        # display the animation
        scr.blit(
            this.anim_sprite.image,
            this.anim_sprite.pos
        )
        pyv.draw_rect(pyv.vars.screen, 'red', this.anim_sprite.rect, 1)

    return pyv.new_actor('e_avatar', locals())
