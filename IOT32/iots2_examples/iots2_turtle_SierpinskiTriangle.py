import random
from adafruit_turtle import Color, turtle
from hiibot_iots2 import IoTs2
iots2 = IoTs2()
iots2.screen.rotation = 180
ci=0
colors = [Color.RED, Color.ORANGE, Color.YELLOW, Color.GREEN, Color.TURQUOISE, Color.BLUE, Color.PURPLE]

def getMid(p1, p2):
    return ((p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2)  # find midpoint

# recursive draw Triangles !
def triangle(points, depth):
    global ci
    turtle.penup()
    turtle.goto(points[0][0], points[0][1])
    turtle.pendown()
    turtle.pencolor(colors[int(10*random.random())%len(colors)])
    ci+=1
    turtle.goto(points[1][0], points[1][1])
    turtle.goto(points[2][0], points[2][1])
    turtle.goto(points[0][0], points[0][1])

    if depth > 0:
        triangle(
            [points[0], getMid(points[0], points[1]), getMid(points[0], points[2])],
            depth - 1,
        )
        triangle(
            [points[1], getMid(points[0], points[1]), getMid(points[1], points[2])],
            depth - 1,
        )
        triangle(
            [points[2], getMid(points[2], points[1]), getMid(points[0], points[2])],
            depth - 1,
        )


turtle = turtle(iots2.screen)

big = min(iots2.screen.width / 2, iots2.screen.height / 2)
little = big / 1.4
seed_points = [[-big, -little], [0, big], [big, -little]]  # size of triangle
triangle(seed_points, 4)

while True:
    pass
