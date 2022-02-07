import time
from hiibot_iots2 import IoTs2
iots2 = IoTs2()
iots2.blueLED_bright = 1.0
while True:
    iots2.blueLED_toggle()
    time.sleep(0.5)