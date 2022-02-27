
from adafruit_turtle import Color, turtle
from hiibot_iots2 import IoTs2
iots2 = IoTs2()
# 控制光滑细分的圆滑度: 用多少边绘制一个圆。 该参数较大时，比较圆滑；该参数值较小时，圆蜕变为正多边形。
Roundness=56
# 绘制多少个圆?
Density=36
if Density<3:
    Density=3
colors = (Color.RED, Color.ORANGE, Color.YELLOW, Color.GREEN, Color.TURQUOISE, Color.BLUE, Color.PURPLE, Color.PINK)

turtle = turtle(iots2.screen)
turtle.speed=10
#turtle.pencolor(colors[6])
turtle.pensize(1)
turtle.pendown()

for i in range(Density):
    turtle.pencolor(colors[i%len(colors)])
    turtle.circle(38, steps=Roundness)
    turtle.right(360/Density)

while True:
    pass
