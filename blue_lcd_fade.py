import time
import random
from hiibot_iots2 import IoTs2

def set_rgb_color(color):
    iots2.pixels.auto_write = True
    iots2.pixels.brightness = 0.03
    colorsList = [(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)), (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)), (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)), (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)), (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)), (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))]
    iots2.pixels[0] = colorsList[color]

iots2 = IoTs2()
iots2.screen.rotation = 270
b = 1.0
flag = True
rgb_color = 0

while True:
    iots2.blueLED_bright = b
    if flag:
        b -= 0.05
        print("current bright is %f" %b)
        if b <= 0.05:
            b = 0.05
            flag = False
    if not flag:
        b += 0.05
        print("current bright is %f" %b)
        if b >= 1.0:
            b = 1.0
            flag = True
    
    set_rgb_color(rgb_color)
    rgb_color += 1
    if rgb_color == 6:
        rgb_color = 0
        
    time.sleep(0.1)