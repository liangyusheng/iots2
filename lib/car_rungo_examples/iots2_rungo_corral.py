import time
# import RunGo module from hiibot_iots2_rungo.py
from hiibot_iots2_rungo import RunGo
car = RunGo()
print("Run Go!")
# speed=100, 0, forward; 1, backward; 2, rotate-left; 3, rotate-right
car.stop() # stop motors
print("press Button-A")
car.rightHeadLED = 0
car.leftHeadLED = 0
carSpeed_fast = 100
carSpeed_slow = 70
carrun = False
idleCnt = 0
while True:
    idleCnt+=1
    if idleCnt>=50000:
        for i in range(3):
            car.pixels[i] = (0,0,0)
        car.pixels.show()
    else:
        car.pixelsRotation()
    car.buttons_update()
    if car.button_A_wasPressed:
        carrun = True
        idleCnt = 0
        print("running")
    if car.button_B_wasPressed:
        car.stop()
        idleCnt = 0
        print("stop")
        carrun = False
    lt = car.leftTracker   # left sensor
    rt = car.rightTracker  # right sensor
    if carrun:
        idleCnt = 0
        if lt ==1 and rt ==1 :  # dual sensor above back-line
            car.stop()
            car.move(1, 0-carSpeed_fast)  # backward
            time.sleep(0.2)
            car.stop()
            car.move(2, carSpeed_fast)  # turn left
            time.sleep(0.2)
            car.stop()
        elif lt ==1 :  # left sensor above back-line only
            car.stop()
            car.rightHeadLED = 1
            car.move(3, carSpeed_fast)  # turn right
            time.sleep(0.2)
            car.stop()
            car.rightHeadLED = 0
        elif rt ==1 :   # right sensor above back-line only
            car.stop()
            car.leftHeadLED = 1
            car.move(2, carSpeed_fast)  # turn left
            time.sleep(0.2)
            car.stop()
            car.leftHeadLED = 0
        else: 
            car.move(0, carSpeed_slow)  # forward
            time.sleep(0.02)
    pass
