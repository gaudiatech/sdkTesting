from . import glvars
from .glvars import pyv
from .actors.entities_viewer import new_entities_viewer
from .actors.avatar import new_avatar
from .actors.misc import new_solid_background, new_color_viewer, new_movable_rect


pyv.bootstrap_e()

# gl. vars
pressed_keys = set()
last_nb_keys = 0
timer_active = False

# const.
VALID_EVENTS = (
    'new_nb_pressed_keys', 'timer_start', 'timer_stop', 'color_change', 'av_input'
)


# -----
#  declare the 3 main functions (mandatory)
def init(vmst=None):
    pyv.init(mode=pyv.LOW_RES_MODE, wcaption='Neon Samurai Tech Demo')
    # declare your custom events here
    pyv.declare_evs(*VALID_EVENTS)

    print('-' * 32)
    print('press one or two key (any key) to see something cool')
    font_size = 48
    glvars.font_obj = pyv.new_font_obj(None, font_size)  # None -> the defaut font
    new_solid_background()
    glvars.screen_center = (
        pyv.get_surface().get_width()//2,
        pyv.get_surface().get_height()//2
    )
    new_movable_rect(glvars.screen_center)
    new_entities_viewer()
    new_avatar()
    new_color_viewer()

    print('----- try to press 1, 2 or 3 keys at the same time! ---------')
    print('you can also drag and drop the purple square, for fun. This will play a sound')


def update(time_info=None):
    global last_nb_keys, timer_active
    # <>
    # handle events, many operations here are mere forwarding
    for ev in pyv.evsys0.get():
        if ev.type == pyv.evsys0.QUIT:
            pyv.vars.gameover = True
        elif ev.type == pyv.evsys0.MOUSEBUTTONDOWN:
            pyv.post_ev('mousedown', pos=ev.pos, button=ev.button)  # forward event (low level->game level)
        elif ev.type == pyv.evsys0.MOUSEBUTTONUP:
            pyv.post_ev('mouseup', pos=ev.pos, button=ev.button)  # forward event
        elif ev.type == pyv.evsys0.MOUSEMOTION:
            pyv.post_ev('mousemotion', pos=ev.pos, rel=ev.rel)  # forward event

        elif ev.type == pyv.evsys0.KEYDOWN:
            pressed_keys.add(ev.key)  # counting

            if ev.key == pyv.evsys0.K_RETURN:
                if not timer_active:
                    pyv.post_ev('timer_start')
                    timer_active = True
                else:
                    pyv.post_ev('timer_stop')
                    timer_active = False
            elif ev.key == pyv.evsys0.K_SPACE:
                pyv.post_ev('color_change')
            elif ev.key == pyv.evsys0.K_UP:
                pyv.post_ev('av_input', k='up_pressed')
            elif ev.key == pyv.evsys0.K_DOWN:
                pyv.post_ev('av_input', k='down_pressed')
            elif ev.key == pyv.evsys0.K_RIGHT:
                pyv.post_ev('av_input', k='right_pressed')
            elif ev.key == pyv.evsys0.K_LEFT:
                pyv.post_ev('av_input', k='left_pressed')
                print('-->left pressed')

        elif ev.type == pyv.evsys0.KEYUP:
            pressed_keys.remove(ev.key)
            mapping = {
                pyv.evsys0.K_UP: 'up_released',
                pyv.evsys0.K_DOWN: 'down_released',
                pyv.evsys0.K_RIGHT: 'right_released',
                pyv.evsys0.K_LEFT: 'left_released'
            }
            if ev.key in mapping:
                pyv.post_ev('av_input', k=mapping[ev.key])

    # <>
    # logic update
    if last_nb_keys is None or len(pressed_keys) != last_nb_keys:  # only if smth changed
        new_nb = len(pressed_keys)
        pyv.post_ev('new_nb_pressed_keys', nb=new_nb)  # we forward how many keys are pressed now
        last_nb_keys = new_nb
    pyv.post_ev('update', curr_t=time_info)

    # <>
    # screen/visual update
    pyv.post_ev('draw', screen=pyv.vars.screen)  # ref. to the screen can also be fetched through: pyv.get_surface()
    pyv.process_evq()  # process all events that are in stand-by
    pyv.flip()  # always call .flip() at the end of the update function


def close(vmst=None):
    pyv.close_game()
