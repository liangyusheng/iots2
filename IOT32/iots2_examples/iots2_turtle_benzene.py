import board
from adafruit_turtle import Color, turtle
from hiibot_iots2 import IoTs2
iots2 = IoTs2()
turtle = turtle(iots2.screen)
benzsize = min(iots2.screen.width, iots2.screen.height) * 0.6

print("Turtle will draw a picture on the screen")
# list of colors
colors = [Color.RED, Color.ORANGE, Color.YELLOW, Color.GREEN, Color.TURQUOISE, Color.BLUE, Color.PURPLE]
# pen down, and start drawing
turtle.pendown()
start = turtle.pos()

for x in range(benzsize):
    turtle.pencolor(colors[x % len(colors)])
    turtle.forward(x)
    turtle.left(59)

while True:
    pass
