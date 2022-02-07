import time
import displayio
from hiibot_iots2 import IoTs2
from adafruit_display_shapes.circle import Circle
from adafruit_display_shapes.line import Line
# instantiate NeoPixel as a pixels, and clear all pixels
iots2 = IoTs2()
iots2.screen.rotation = 180
RED = (255, 0, 0)
ORANGE = (255, 150, 0)
YELLOW = (255, 255, 0)
GREEN = (0, 255, 0)
CYAN = (0, 255, 255)
BLUE = (0, 0, 255)
VIOLET = (255, 0, 255)
WHITE = (255, 255, 255)
# define a group of graphic element to draw a backgroud pattern, include 8 elements
background_subgroup = displayio.Group()
bk_list = []
# define 8 graphic elements in a list
bk_list.append( Line(0, 120, 135, 120, color=WHITE) )  # line1
bk_list.append( Line(67, 0, 67, 240, color=WHITE) )    # line2
bk_list.append( Circle(67, 120, 119, outline=RED) )    # outer1_circle
bk_list.append( Circle(67, 120,  90, outline=YELLOW) ) # outer2_circle
bk_list.append( Circle(67, 120,  70, outline=GREEN) )  # middle_circle
bk_list.append( Circle(67, 120,  50, outline=CYAN) )   # inner2_circle
bk_list.append( Circle(67, 120,  30, outline=BLUE) )   # inner1_circle
bk_list.append( Circle(67, 120,  12, outline=VIOLET) ) # inner0_circle
# append 8 graphic elements into the group of graphic element
for i in range( len(bk_list) ):
    background_subgroup.append( bk_list[i] )
# define a group of graphic element to draw a foregroud pattern, a bubble
foregroud_subgroup = displayio.Group()
# define this bubble, its x-, and y- coordinate equal to x, and y of iots2.Accele_ms2
x, y, _ = iots2.Accele_ms2
level_bubble = Circle(int(x + 67), int(y + 120), 9, fill=RED, outline=RED)
# append this bubble into graphic element
foregroud_subgroup.append(level_bubble)
# append this graphic element into the group
graphic_group = displayio.Group()
graphic_group.append(background_subgroup)
graphic_group.append(foregroud_subgroup)
# show this group of graphic element on the screen
iots2.screen.show(graphic_group)
 
while True:
    # update the bubble position on the screen according to sensors.acceleration
    x, y, _ = iots2.Accele_ms2
    foregroud_subgroup.y = int(x * 12)
    foregroud_subgroup.x = int(y * -12)
    time.sleep(0.05)
    # if the blubble be placed in the center of screen
    if -0.33<=x and x<=0.33 and -0.33<=y and y<=0.33:
        iots2.pixels[0] = (0,255,0)
    else:
        iots2.pixels[0] = (0,0,0)
    
