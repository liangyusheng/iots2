import time
import random
from hiibot_iots2 import IoTs2
from hiibot_iots2_rungo import RunGo
iots2 = IoTs2()
iots2.screen.rotation = 180
car = RunGo()
car.stop()  # stop car one second
carspeed = 80
time.sleep(1)
running = False
def  searchBackLine():
    global car
    for steps in range(360):
        rdir = random.randint(0, 2)
        if rdir==0:
            car.move(2, 60)
        else:
            car.move(3, 60)
        time.sleep(0.005)
        if not car.rightTracker or not car.leftTracker:
            # backlin be searched by any sensor
            car.stop()
            return True
    car.stop()
    return False
while True:
    car.pixelsRotation()
    car.buttons_update()
    if car.button_A_wasPressed:
        running = True
        print("running")
    if car.button_B_wasPressed:
        car.stop()
        print("stop")
        running = False
    lt = car.leftTracker   # left sensor
    rt = car.rightTracker  # right sensor
    if running:
        # two sensors is above backline, go on
        if lt and rt:
            car.motor(carspeed, carspeed)
        # left sensor is above backline, but right sensor missed backline, thus turn left
        elif lt:
            car.motor(carspeed//2, carspeed)
        # right sensor is above backline, but left sensor missed backline, thus turn right
        elif rt:
            car.motor(carspeed, carspeed//2)
        # two sensors missed backline, thus stop car and search backline
        else:
            car.stop()
            print("black line is missing, need to search the black line")
            if not searchBackLine():
                break
        time.sleep(0.01)
    else:
        pass
