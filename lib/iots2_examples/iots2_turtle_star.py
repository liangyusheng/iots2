from adafruit_turtle import Color, turtle
from hiibot_iots2 import IoTs2
iots2 = IoTs2()
iots2.screen.rotation = 180
turtle = turtle(iots2.screen)
starsize = min(iots2.screen.width, iots2.screen.height) * 0.9  # 90% of screensize

print("Turtle time! Lets draw a star")

turtle.pencolor(Color.BLUE)
turtle.setheading(90)

turtle.penup()
turtle.goto(-starsize / 2, 0)
turtle.pendown()

start = turtle.pos()
while True:
    turtle.forward(starsize)
    turtle.left(170)
    if abs(turtle.pos() - start) < 1:
        break

while True:
    pass
