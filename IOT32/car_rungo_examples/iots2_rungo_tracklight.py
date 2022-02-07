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
carMaxSpeed = 100
speedsList = [carMaxSpeed-30, carMaxSpeed-20, carMaxSpeed-10, carMaxSpeed]
running = False
idleCnt = 0
diff = 200
preDiff = 0
df_scale = 300
def checkDirection():
    global car, diff, preDiff, df_scale
    ls, rs = car.leftLightSensor, car.rightLightSensor
    preDiff = diff
    diff = abs(ls-rs)
    ediff = abs(diff-preDiff)
    if diff<df_scale:
        if diff>preDiff and ediff>100:
            return 3
        else:
            return 0
    elif ls>rs:
        return 1
    else:
        return 2
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
        dir = checkDirection()
        if dir==0:
            car.stop()
        elif dir==1:
            scale = int(diff/df_scale)
            if scale<len(speedsList):
                s = speedsList[scale]
            else:
                s = speedsList[3]
            car.motor(int(s*0.4), s)
        elif dir==2:
            scale = int(diff/df_scale)
            if scale<len(speedsList):
                s = speedsList[scale]
            else:
                s = speedsList[3]
            car.motor(s, int(s*0.4))
        else:
            car.motor(carMaxSpeed, carMaxSpeed)
        time.sleep(0.01)
    else:
        pass