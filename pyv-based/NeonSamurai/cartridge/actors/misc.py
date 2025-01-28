from .. import glvars

from ..glvars import pyv


def new_color_viewer():
    data = {
        'curr_color_name': 'medium_gray',
        'square_position': (325, 400, 80, 80)
    }

    # - behavior
    def on_color_change(this, ev):
        this.curr_color_name = pyv.pal.yu.next_colorname(this.curr_color_name)
        print(' color?', this.curr_color_name)

    def on_draw(this, ev):
        pyv.draw_rect(ev.screen, pyv.pal.yu[this.curr_color_name], this.square_position)

    return pyv.new_actor('color_viewer', locals())


def new_solid_background():
    data = {
        'color': pyv.pal.yu.medium_gray
    }

    def on_draw(this, ev):
        ev.screen.fill(this.color)

    return pyv.new_actor('bg', locals())  # 1st argument = arbitrary name(used to debug) and 2nd arg is ALWAYS locals()


def new_movable_rect(init_position):
    data = {
        'rect': pyv.new_rect_obj(init_position[0], init_position[1], 64, 64),
        'drag_state': False
    }

    def on_mousedown(this, ev):
        if ev.button == 1:
            print('<MOUSE CLICK,> position:', ev.pos)
            if this.rect.collidepoint(ev.pos):
                this.drag_state = True
                pyv.play_sound('woosh', repeat=1)  # as defined in metadat.json

    def on_mouseup(this, ev):
        if ev.button == 1:
            if this.drag_state:
                this.drag_state = False
                pyv.play_sound('sfx_drop')

    def on_mousemotion(this, ev):
        if this.drag_state:
            this.rect.topleft = ev.pos

    def on_draw(this, ev):
        pyv.draw_rect(ev.screen, 'purple', this.rect, 4)  # 4 stands for line width

    return pyv.new_actor('movable_rect', locals())
