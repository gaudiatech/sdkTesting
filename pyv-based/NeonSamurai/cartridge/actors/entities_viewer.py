from .. import glvars

from ..glvars import pyv


def new_entities_viewer():
    TEXT_COLOR = '#a1eeff'  # could also be 'black' or pyv.pal.c64.blue for example
    TEXT_POS = (250, 168)

    data = {
        'what_to_display': 'text',
        'my_rect': pyv.new_rect_obj(28, 56, 200, 200),
        'my_text': glvars.font_obj.render('hello, no timer', False, TEXT_COLOR),
        'saved_date': None,
        'last_t': None
    }

    def on_timer_start(this, ev):
        print('timer started')
        this.saved_date = pyv.time()  # convenient way to retrieve current time
        this.my_text = glvars.font_obj.render('measuring time...', False, TEXT_COLOR)

    def on_timer_stop(this, ev):
        print('stop')
        total_time = this.last_t - this.saved_date
        this.my_text = glvars.font_obj.render(f'elpsed time:{total_time:.2f}', False, TEXT_COLOR)

    def on_update(this, ev):
        this.last_t = ev.curr_t

    def on_new_nb_pressed_keys(this, ev):
        if ev.nb == 0:
            this.what_to_display = 'text'
        elif ev.nb == 1:
            this.what_to_display = 'lion'
        elif ev.nb == 2:
            this.what_to_display = 'square'
        else:
            this.what_to_display = None

    def on_draw(this, ev):
        scr = ev.screen
        if this.what_to_display is None:
            pass  # nothing to display...
        elif this.what_to_display == 'text':
            scr.blit(this.my_text, TEXT_POS)
        elif this.what_to_display == 'lion':
            scr.blit(pyv.vars.images['lion'], this.my_rect)
        elif this.what_to_display == 'square':
            pyv.draw_rect(scr, 'orange', this.my_rect)

    return pyv.new_actor('e_viewer', locals())
