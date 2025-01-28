from .. import glvars

from ..glvars import pyv


def new_avatar():
    anims_description = {}
    # example of another "anims_description"
    # that would work well in another game, with another spite sheet:
    # {
    #   "idle": {"set": "0-5", "delay": 100},
    #   "attack": {"set": [6,7,8,9,10,11], "delay": 250}
    # }
    tmp_info = {"default_anim": dict(set=[f"frame{n}.png" for n in range(26)], delay=142)}  # delay= nb ms per frame
    xpos = 16
    ypos = 50

    data = {
        'x': xpos, 'y': ypos,

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

        'anim_sprite': pyv.gfx.AnimatedSprite(  # this line shows you how to use animated sprites!
            (xpos, ypos),  # position x,y
            pyv.vars.spritesheets['GreatSwordKnight_2hIdle5_dir1'],  # first argument is a sprite sheet
            # the description of animations in case we have several in 1 sprsheet
            tmp_info
        ),

        'x_mvt': 0,
        'y_mvt': 0,

        'direction': 'sw',  # South-West
        'moving': False,
        "curr_anim_id": "idle_dir1"
    }

    # start animation
    data['anim_sprite'].play("default_anim")

    def _util_update_dir(this):
        """
        goal= take into account both x_mvt and y_mvt in order to update 3 attributes:
        - this.direction
        - this.moving
        - curr_anim_id
        """
        print('computing direction: params:', this.x_mvt, this.y_mvt)
        if this.x_mvt == 0 and this.y_mvt == 0:
            this.direction = None
            this.moving = False
            # select the idle anim based on the latest known movement
            prev_dir_code = this.curr_anim_id[-1]
            this.curr_anim_id = 'idle_dir' + prev_dir_code
            return
        this.moving = True
        if this.x_mvt == 1:
            if this.y_mvt == 1:
                this.direction = 'se'
            elif this.y_mvt == -1:
                this.direction = 'ne'
            else:
                this.direction = 'e'
        elif this.x_mvt == -1:
            if this.y_mvt == 1:
                this.direction = 'sw'
            elif this.y_mvt == -1:
                this.direction = 'nw'
            else:
                this.direction = 'w'
        else:  # thus, x_mvt is zero
            if this.y_mvt == 1:
                this.direction = 's'
            elif this.y_mvt == -1:
                this.direction = 'n'
        mapcode_to_int = {
            'sw': 1, 'w': 2, 'nw': 3, 'n': 4, 'ne': 5, 'e': 6, 'se': 7, 's': 8
        }
        this.curr_anim_id = 'walk_dir' + str(mapcode_to_int[this.direction])

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
            (this.x, this.y),  # x and y position
            pyv.vars.spritesheets[sprsheet_name],  # first argument is a sprite sheet
            this.infos_anim[this.curr_anim_id]
        )
        # since anim has restarted we MUST use the two lines below,
        # otherwise the update event will break the animation cls
        this.last_tick = None
        this.anim_sprite.play("default_anim")

    # -----------------
    #  behavior
    # -----------------
    def on_av_input(this, ev):
        if 'left_pressed' == ev.k and this.x_mvt != 1:
            this.x_mvt = -1
        if 'left_released' == ev.k:
            this.x_mvt = 0
        if 'right_pressed' == ev.k and this.x_mvt != -1:
            this.x_mvt = 1
        if 'right_released' == ev.k:
            this.x_mvt = 0

        if 'up_pressed' == ev.k and this.y_mvt != 1:
            this.y_mvt = -1
        if 'up_released' == ev.k:
            this.y_mvt = 0
        if 'down_pressed' == ev.k and this.y_mvt != -1:
            this.y_mvt = 1
        if 'down_released' == ev.k:
            this.y_mvt = 0

        _util_update_dir(this)
        print('new direction:', this.direction)
        _util_update_anim(this)

    # - behavior
    # def on_anim_swap(this, ev):
    #     if this.curr_anim_id == "idle_dir1":
    #         new_aid = this.curr_anim_id = "walk_dir1"
    #     else:
    #         new_aid = this.curr_anim_id = "idle_dir1"
    #     _util_update_anim(this)

    def on_update(this, ev):
        # has to update all animations
        delta_t = 0 if (this.last_tick is None) else ev.curr_t - this.last_tick
        this.anim_sprite.update(delta_t)
        # save date of the current tick
        this.last_tick = ev.curr_t

    def on_draw(this, ev):
        scr = ev.screen
        # display the animation
        scr.blit(
            this.anim_sprite.image,
            this.anim_sprite.pos
        )

    return pyv.new_actor('e_avatar', locals())
