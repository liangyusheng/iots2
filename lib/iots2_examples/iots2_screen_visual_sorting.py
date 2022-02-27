import time
import random
import displayio
from adafruit_display_shapes.rect import Rect
from adafruit_display_shapes.circle import Circle
from hiibot_iots2 import IoTs2
iots2 = IoTs2()
screen = iots2.screen
screen.rotation = 270
speed = 0.1 # seconds for changing animation
height = [random.randint(10 , 100)  for _ in range(7)]
gol = [0, 1, 2, 3, 4, 5, 6]          # list of the index of group elements
x = [26, 58, 90, 122, 154, 186, 218] # list of x-coordinate for each sprite
#  creat a group of sprites (5x rects)
group = displayio.Group()
#  draw each sprite (5x rects)
s0 = {'x':x[0] , 'y':110-height[0] , 'x2':20 , 'y2':height[0] , 'ot':(0, 52, 255) , 'fl':(0, 26, 255)}
S0 = Rect(s0['x'] , s0['y'] , s0['x2'] , s0['y2'] , outline = s0['ot'] , fill = s0['fl'])
group.append(S0)
s1 = {'x':x[1] , 'y':110-height[1] , 'x2':20 , 'y2':height[1] , 'ot':(255, 0, 0) , 'fl':(255, 0, 0)}
S1 = Rect(s1['x'] , s1['y'] , s1['x2'] , s1['y2'] , outline = s1['ot'] , fill = s1['fl'])
group.append(S1)
s2 = {'x':x[2] , 'y':110-height[2] , 'x2':20 , 'y2':height[2] , 'ot':(212, 255, 0) , 'fl':(212, 255, 0)}
S2 = Rect(s2['x'] , s2['y'] , s2['x2'] , s2['y2'] , outline = s2['ot'] , fill = s2['fl'])
group.append(S2)
s3 = {'x':x[3] , 'y':110-height[3] , 'x2':20 , 'y2':height[3] , 'ot':(63, 255, 0) , 'fl':(63, 255, 0)}
S3 = Rect(s3['x'] , s3['y'] , s3['x2'] , s3['y2'] , outline = s3['ot'] , fill = s3['fl'])
group.append(S3)
s4 = {'x':x[4] , 'y':110-height[4] , 'x2':20 , 'y2':height[4] , 'ot':(0, 216, 255) , 'fl':(0, 216, 255)}
S4 = Rect(s4['x'] , s4['y'] , s4['x2'] , s4['y2'] , outline = s4['ot'] , fill = s4['fl'])
group.append(S4)
s5 = {'x':x[5] , 'y':110-height[5] , 'x2':20 , 'y2':height[5] , 'ot':(255, 0, 255) , 'fl':(255, 0, 255)}
S5 = Rect(s5['x'] , s5['y'] , s5['x2'] , s5['y2'] , outline = s5['ot'] , fill = s5['fl'])
group.append(S5)
s6 = {'x':x[6] , 'y':110-height[6] , 'x2':20 , 'y2':height[6] , 'ot':(255, 216, 0) , 'fl':(255, 216, 0)}
S6 = Rect(s6['x'] , s6['y'] , s6['x2'] , s6['y2'] , outline = s6['ot'] , fill = s6['fl'])
group.append(S6)
#  draw a red dot to mark the current minimum
red_dot = Circle( 36, 120, 5, outline=(255,0,0), fill=(255,0,0) )
group.append(red_dot)
white_dot = Circle( 66, 120, 5, outline=(127,127,127), fill=(127,127,127) )
group.append(white_dot)
#  show thoese sprites onto BlueFi LCD screen
screen.show(group)

#  changing animation
def animation_chg(l, r, steps):
    global group
    for _ in range( 8 ):
        time.sleep(speed)
        group[l].x += 4*steps
        group[r].x -= 4*steps
        #time.sleep(speed)

#  no-change animation
def animation_nochg(l, r):
    global group
    tf = group[l].fill
    for _ in range(2):
        time.sleep(speed)
        group[l].y -= 40
        time.sleep(speed)
        group[l].y += 40
        #time.sleep(speed/4)
    group[l].fill = tf

# sort and its animation
for i in range(7):
    red_dot.x = x[i]+4
    time.sleep(0.1)
    for j in range(i+1, 7):
        time.sleep(0.1)
        white_dot.x = x[j]+4
        time.sleep(0.1)
        if height[i] > height[j]:
            # Exchange their positions, and exchange the index of group elements
            c1, c2 = height[j], gol[j]
            height[j], gol[j] = height[i], gol[i]
            height[i], gol[i] = c1, c2
            animation_chg(gol[j], gol[i], j-i)
        else:
            animation_nochg(gol[j], gol[i])

while True:
    pass