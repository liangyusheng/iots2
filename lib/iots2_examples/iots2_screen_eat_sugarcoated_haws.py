import time
import displayio
from adafruit_display_shapes.line import Line
from adafruit_display_shapes.triangle import Triangle
from adafruit_display_shapes.polygon import Polygon
from adafruit_display_shapes.rect import Rect
from adafruit_display_shapes.roundrect import RoundRect
from adafruit_display_shapes.circle import Circle
import terminalio
from adafruit_display_text.label import Label
from hiibot_iots2 import IoTs2
iots2 = IoTs2()
iots2.screen.rotation = 180
shape_group = displayio.Group() # 3 sub-groups
# Color variables available for import.
RED, GREEN, GOLD = (255, 0, 0), (0, 255, 0), (255, 222, 30)
lines, circles = [], []
# draw 3 lines and append on the lines_subgroup
lines_subgroup = displayio.Group()
for i in range(3):
    lines.append( Line(66+i, 8, 66+i, 230, color=GOLD) )
    lines_subgroup.append(lines[i])
shape_group.append(lines_subgroup)
# draw 6 circles and append on the circle_subgroup
y_initial = 25
circle_subgroup = displayio.Group()
for i in range( 6 ):
    circles.append( Circle(67,y_initial+(i*20), 16, fill=RED, outline=RED) )
    circle_subgroup.append(circles[i])
shape_group.append(circle_subgroup)
# create a text label
textlabel_subgroup = displayio.Group(scale=2)
textlabel = Label(terminalio.FONT,x=18,y=88,text="", color=GREEN)
textlabel_subgroup.append(textlabel)
shape_group.append(textlabel_subgroup)
# show those content on the IoTs2 screen
iots2.screen.show(shape_group)
eat_index = 0
textlabel.text = 'eating'
s_point = time.monotonic()
while True:
    if iots2.button_state:
        jy = circles[eat_index].y//3
        for j in range(jy+3):
            circles[eat_index].y -= 3
            time.sleep(0.02)
        circles[eat_index].hidden = True
        eat_index += 1
        if eat_index>=len(circles):
            tl = time.monotonic() - s_point
            eat_index = 0
            for i in range(20):
                lines_subgroup.y += 5
                time.sleep(0.01)
            lines_subgroup.hidden = True
            lines_subgroup.y = 0
            textlabel.text = '{:.3f}'.format(tl)
            time.sleep(0.5)
            for i in range(len(circles)):
                circles[i].y = y_initial+(i*20)
            lines_subgroup.hidden = False
            for i in range(len(circles)):
                circles[i].hidden = False
            time.sleep(0.5)
            textlabel.text = 'eating'
            s_point = time.monotonic()

