import time
from hiibot_iots2 import IoTs2
iots2 = IoTs2()
iots2.pixels.auto_write = True
iots2.pixels.brightness = 0.1
colorList = [(255,0,0),   # red
             (192,63,0),  # orange
             (127,127,0), # yellow
             (0,255,0),   # green
             (0,127,127), # cyan
             (0,0,255),   # blue
             (127,0,127)] # purple
colorName = ('Red', 'Orange', 'Yellow', 'Green', 'Cyan', 'Blue', 'Purple')
index = 0
while True:
    iots2.pixels[0] = colorList[index%len(colorList)]
    print( colorName[index%len(colorList)] )
    time.sleep(1.0)
    index += 1
