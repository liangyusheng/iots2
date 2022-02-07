import time
import random
from hiibot_iots2 import IoTs2
from hiibot_iots2_rungo import RunGo
car = RunGo()
iots2 = IoTs2()
car.stop()
iots2.screen.rotation = 180
print('Run Go!')
minDistance = 8.0
maxDistance = 15.0
badDistance = 440.00
carMaxSpeed = 80
carMinSpeed = 60
pdt = [0, 0, 0]
running = False
idleCnt = 0
# 检查是否堵住(堵住时连续的距离变化非常小)
def stallCheck(dt) :
    dif0 = abs(pdt[0] - pdt[1])
    dif1 = abs(pdt[1] - pdt[2])
    dif2 = abs(pdt[2] - dt)
    pdt[0] = pdt[1]
    pdt[1] = pdt[2]
    pdt[2] = dt
    if 0.4>max(dif0, dif1, dif2):
        return True
    else:
        return False
# 随机转弯
def randomTurn():
    global car, carMinSpeed, carMaxSpeed
    car.stop()
    time.sleep(0.01)
    dir = random.randint(0,2)
    if dir==1:
        car.motor(carMinSpeed, -carMinSpeed)
    else:
        car.motor(-carMinSpeed, carMinSpeed)
    time.sleep(0.5)
    car.motor(carMaxSpeed, carMaxSpeed)
# 先后退一段距离再随机转弯    
def backThenRandomRurn():
    global car, carMaxSpeed
    car.stop()
    time.sleep(0.01)
    car.motor(-carMaxSpeed, -carMaxSpeed)
    time.sleep(0.4)
    randomTurn()
# 主循环：检查是否待机，待机则关闭彩灯；检查启动(A)或停止(B)；
# 启动后检测障碍物距离并决定前进/随机转弯/先后退再随机转弯等3种行为
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
        time.sleep(0.01)
        idleCnt = 0
        dt = car.distance
        if stallCheck(dt):
            backThenRandomRurn()
            continue
        if dt<minDistance or dt>badDistance:
            backThenRandomRurn()   
        elif dt<maxDistance:
            randomTurn()
        else:
            car.motor(carMaxSpeed, carMaxSpeed)
    else:
        pass