from math import pi

import katagames_sdk as katasdk


if katasdk.VERSION != '0.0.6':
    kataen = katasdk.engine
    pygame = kataen.pygame

else:
    import katagames_sdk.engine as kataen
    pygame = kataen.import_pygame()

"""
--- --- ---
retro-compatibility support of this test:

         0.0.6    0.0.7
      --- --- --- --- -
local |   y   |   Y    |
      |       |        |
      --- --- --- --- -
 web  |   N   |   Y    |
      |       |        |
      --- --- --- --- -
"""

# Define the colors we will use in RGB format
BLACK = (  0,   0,   0)
WHITE = (255, 255, 255)
BLUE =  (  0,   0, 255)
GREEN = (  0, 255,   0)
RED =   (255,   0,   0)


#Loop until the user clicks the close button.
clock,gameover,screen = None,None,None
tmpsurf = None

def game_init():
    global clock,gameover,screen,tmpsurf
    kataen.init(kataen.OLD_SCHOOL_MODE)
    
    #screen = pygame.display.set_mode(size)
    screen = kataen.get_screen()
    size = screen.get_size()

    ft = pygame.font.Font(None,16)
    tmpsurf=ft.render(
        "Example code for the draw module",
        False,
        BLUE
    )

    clock = pygame.time.Clock()
    gameover=False


def update_game(timeinfo=None):
    global gameover, tmpsurf
    for event in pygame.event.get(): # User did something
        if event.type == pygame.QUIT: # If user clicked close
            gameover=True # Flag that we are done so we exit this loop
 
    # All drawing code happens after the for loop and but
    # inside the main while done==False loop.
     
    # Clear the screen and set the screen background
    screen.fill('antiquewhite3')
 
    # Draw on the screen a GREEN line from (0, 0) to (50, 30) 
    # 5 pixels wide.
    pygame.draw.line(screen, GREEN, [0, 0], [50,30], 5)
 
    # Draw on the screen 3 BLACK lines, each 5 pixels wide.
    # The 'False' means the first and last points are not connected.
    pygame.draw.lines(screen, BLACK, False, [[0, 80], [50, 90], [200, 80], [220, 30]], 5)
    
    # Draw on the screen a GREEN line from (0, 50) to (50, 80) 
    # Because it is an antialiased line, it is 1 pixel wide.
    pygame.draw.aaline(screen, GREEN, [0, 50],[50, 80], True)

    # Draw a rectangle outline
    pygame.draw.rect(screen, BLACK, [75, 10, 50, 20], 2)
     
    # Draw a solid rectangle
    pygame.draw.rect(screen, BLACK, [150, 10, 50, 20])

    # Draw a rectangle with rounded corners
    pygame.draw.rect(screen, GREEN, [235, 150, 70, 40], 10, border_radius=15)
    pygame.draw.rect(screen, RED, [255, 195, 50, 30], 0, border_radius=10, border_top_left_radius=0,
                     border_bottom_right_radius=15)

    # Draw an ellipse outline, using a rectangle as the outside boundaries
    pygame.draw.ellipse(screen, RED, [225, 10, 50, 20], 2) 

    # Draw an solid ellipse, using a rectangle as the outside boundaries
    pygame.draw.ellipse(screen, RED, [300, 10, 50, 20]) 
 
    # This draws a triangle using the polygon command
    pygame.draw.polygon(screen, BLACK, [[98, 98], [8, 150], [175, 150]], 5)
  
    # Draw an arc as part of an ellipse. 
    # Use radians to determine what angle to draw.
    ydebut,yfin = 45, 85
    pygame.draw.arc(screen, BLACK,[290, ydebut, 150, yfin], 0, pi/2, 2)
    pygame.draw.arc(screen, GREEN,[290, ydebut, 150, yfin], pi/2, pi, 2)
    pygame.draw.arc(screen, BLUE, [290, ydebut, 150, yfin], pi,3*pi/2, 2)
    pygame.draw.arc(screen, RED,  [290, ydebut, 150, yfin], 3*pi/2, 2*pi, 2)
    
    # Draw a circle
    pygame.draw.circle(screen, BLUE, [60, 200], 40)

    # Draw only one circle quadrant
    xy_pos=380,190
    pygame.draw.circle(screen, BLUE, xy_pos, 40, 0, draw_top_right=True)
    pygame.draw.circle(screen, RED, xy_pos, 40, 30, draw_top_left=True)
    pygame.draw.circle(screen, GREEN, xy_pos, 40, 20, draw_bottom_left=True)
    pygame.draw.circle(screen, BLACK, xy_pos, 40, 10, draw_bottom_right=True)

    screen.blit(tmpsurf, (90,235))
    # pygame.display.flip()
    # pygame.display.flip()
    if katasdk.VERSION == '0.0.6':
        kataen.gfx_updater.display_update()
    else:
        kataen.display_update()

    # This limits the while loop to a max of 10 times per second.
    # Leave this out and we will use all CPU we can.
    clock.tick(10)


# entry pt for local execution
if __name__ == '__main__':
    game_init()
    while not gameover:
        update_game()
    kataen.cleanup()


# /!\ will not run in web ctx for katasdk v0.0.6
if kataen.runs_in_web():
    @katasdk.web_entry_point
    def game_init_web():
        game_init()
    @katasdk.web_animate
    def game_update(infot=None):
        update_game(infot)
