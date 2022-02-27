import time
from hiibot_iots2 import IoTs2
from hiibot_iots2_rungo import RunGo
iots2 = IoTs2()
car = RunGo()
car.stop()
iots2.screen.rotation = 180
print('Run Go!')
minDistance = 8.0
maxDistance = 15.0
carMaxSpeed = 80
speedsList = [carMaxSpeed, carMaxSpeed-10, carMaxSpeed-20, carMaxSpeed-30]
running = False
idleCnt = 0
while True:
    idleCnt += 1
    if idleCnt>50000:
        for i in range(3):
            car.pixels[i] = (0,0,0)
        car.pixels.show()
    else:
        car.pixelsRotation()
    car.buttons_update()
    if car.button_A_wasPressed:
        running = True
        idleCnt = 0
        print('running')
    if car.button_B_wasPressed:
        running = False
        car.stop()
        idleCnt = 0
        print('stopping')
    if running:
        idleCnt = 0
        ds = car.distance
        if ds<minDistance:
            si = int(minDistance-ds)
            if si<len(speedsList):
                s = speedsList[si]
            else:
                s = speedsList[3]
            car.motor(-s, -s)
        elif ds>maxDistance:
            si = int(ds-maxDistance)
            if si<len(speedsList):
                s = speedsList[3-si]
            else:
                s = speedsList[0]
            car.motor(s, s)
        else:
            car.stop()
        time.sleep(0.01)
    else:
        pass