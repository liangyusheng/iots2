from hiibot_iots2 import IoTs2
from hiibot_iots2_rungo import RunGo
iots2 = IoTs2()
car = RunGo()
iots2.pixels.brightness = 0.3
iots2.pixels[0] = (0,0,0)
car.stop() # stop motors
print("Press Button-A to sense ground color")
car.pixels.fill(0)
car.pixels.show()
while True:
    car.buttons_update()
    if car.button_A_wasPressed:
        cid = car.groundColorID # get ground color id (0~6)
        print(car.groundColor_name[cid])
        iots2.pixels[0] = car.groundColor_list[cid]