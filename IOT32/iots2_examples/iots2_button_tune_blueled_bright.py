import time
from hiibot_iots2 import IoTs2
iots2 = IoTs2()
cnt=1
bl = [0.0, 0.2, 0.4, 0.6, 0.8, 1.0, 0.8, 0.6, 0.4, 0.2]
while True:
    iots2.blueLED_bright=bl[cnt%10]
    iots2.button_update()
    if iots2.button_wasPressed:
        cnt += 1
