from adafruit_turtle import Color, turtle
from hiibot_iots2 import IoTs2
iots2 = IoTs2()
iots2.screen.rotation = 180
branchLength = None
branch_diffence = None

t = turtle(iots2.screen)
t.hideturtle()
t.speed(0)
t.up()

#  define a recursive function to draw a tree
def recursiveDrawBranch(branchLength):
    global t, branch_diffence
    if branchLength >= 5:
        if branchLength - branch_diffence <= 5:
            t.pencolor(Color.GREEN)
        else:
            t.pencolor(Color.BROWN)
        t.pensize((branchLength * 0.2))
        t.pendown()
        t.backward(1)
        t.forward(branchLength)
        t.right(20)
        recursiveDrawBranch(branchLength - branch_diffence)
        t.left(40)
        recursiveDrawBranch(branchLength - branch_diffence)
        t.penup()
        t.right(20)
        t.backward(branchLength)

#  Ready! lets go to draw a picture 
t.setposition(-33, -110)
branch_diffence = 10
recursiveDrawBranch(40)

t.setposition(33, -100)
branch_diffence = 8
recursiveDrawBranch(30)

t.setposition(0, -120)
branch_diffence = 15
recursiveDrawBranch(70)

while True:
    pass