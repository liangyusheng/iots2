import time
import board
from hiibot_iots2 import IoTs2
iots2 = IoTs2()
from hiibot_my9221_pwmled.white6xled import White6xLED
lamp = White6xLED(board.IO3, board.IO4, groups=3)
bright = 0.2
dir = True
while True:
    iots2.button_update()
    if iots2.button_wasPressed:
        if dir:
            bright += 0.1
            if bright>1.0:
                bright = 1.0
                dir = False
        else:
            bright -= 0.1
            if bright<0.0:
                bright = 0.0
                dir = True
        lamp.setBrightness(bright)
        print(bright)
        time.sleep(0.1)