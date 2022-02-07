import time
from hiibot_iots2 import IoTs2
iots2 = IoTs2()
b=1.0
while True:
    iots2.blueLED_bright = b
    b -= 0.05
    if b<0.0:
        b = 1.0
    time.sleep(0.1)