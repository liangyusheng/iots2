from adafruit_turtle import Color, turtle
from hiibot_iots2 import IoTs2
iots2 = IoTs2()

colors = [Color.ORANGE, Color.PURPLE]
turtle = turtle(iots2.screen)

turtle.pendown()
for x in range(400):
    turtle.pencolor(colors[x % 2])
    turtle.forward(x)
    turtle.left(91)

while True:
    pass
