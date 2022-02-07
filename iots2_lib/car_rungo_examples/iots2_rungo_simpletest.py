import time
from hiibot_iots2 import IoTs2
from hiibot_iots2_rungo import RunGo
iots2 = IoTs2()
iots2.screen.rotation = 180
print('Run Go!')
car = RunGo()
carspeed = 100
go = False
cnt = 0
fsm = 0
print('Button-A -> run')
print('Button-B -> stop')
while True:
    car.pixelsRotation()
    car.buttons_update()
    if car.button_A_wasPressed:
        go = True
        print('running')
    if car.button_B_wasPressed:
        go = False
        cnt = 0
        fsm = 0
        car.rightHeadLED = 0   # turn off right head lamp
        car.stop()
        print('stoping')
    time.sleep(0.01) # 10ms
    if go:
        if fsm==0:
            car.motor(carspeed, carspeed)
            cnt += 1
            if cnt>50:
                cnt = 0
                car.stop()
                fsm = 1
        elif fsm==1:
            car.rightHeadLED = 1   # turn on right head lamp
            car.motor(carspeed//2, -carspeed//2)
            cnt += 1
            if cnt>65:
                car.rightHeadLED = 0   # turn off right head lamp
                car.stop()
                cnt = 0
                fsm = 0
    else:
        pass
