# draw a Sakura tree (it is a very enjoyable works)
import random
from adafruit_turtle import Color, turtle
from hiibot_iots2 import IoTs2
iots2 = IoTs2()
iots2.screen.rotation = 180
t = turtle(iots2.screen)

#  draw Sakura tree with a recursive method
def draw_Sakura_Tree(branchLen, t):
    if branchLen >3:
        if 8<=branchLen and branchLen<=12:
            if random.randint(0, 2) == 0:
                t.pencolor(Color.WHITE)
            else:
                t.pencolor(Color.ORANGE)
            t.pensize(branchLen / 3)
        elif branchLen<8:
            if random.randint(0,1) == 0:
                t.pencolor(Color.WHITE)
            else:
                t.pencolor(Color.ORANGE)
            t.pensize(branchLen / 2)
        else:
            t.pencolor(Color.BROWN)
            t.pensize(branchLen/10)
        t.forward(branchLen)
        a = 1.5*random.random()
        t.right(20*a)
        b = 1.5*random.random()
        # ready! recursive
        draw_Sakura_Tree(branchLen-10*b, t)
        t.left(40*a)
        draw_Sakura_Tree(branchLen-10*b, t)
        t.right(20*a)
        t.up()
        t.backward(branchLen)
        t.down()

# 0: the fastest speed
t.speed(0)
t.hideturtle()
t.up()
t.backward(90)
t.down()
t.pencolor(Color.BROWN)

# call a recursive function to draw Sakura tree
draw_Sakura_Tree(40, t)

while True:
    pass