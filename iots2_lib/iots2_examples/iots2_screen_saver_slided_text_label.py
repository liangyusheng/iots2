import time
import random
import displayio
import terminalio
from adafruit_display_text import label
from hiibot_iots2 import IoTs2
iots2 = IoTs2()
iots2.screen.rotation = 90
text_group = displayio.Group(scale=2)
textLabel = label.Label( 
                     terminalio.FONT,    # font of the text label
                     x=20, y=30,         # initial position
                     text="Hello IoTs2", # text content of the label
                     color=(255,0,0)     # text color
                    )
text_group.append(textLabel)
iots2.screen.rotation = 90
iots2.screen.show(text_group)
xb = textLabel.x
yb = textLabel.y
cntDelay = 0
while True:
    xp=random.randint(0, 60)
    yp=random.randint(6, 60)
    steps = max( abs(xp-xb), abs(yp-yb) )
    xdelta = float(xp-xb)/steps
    ydelta = float(yp-yb)/steps
    for i in range(steps):
        textLabel.x = int(xb+(xdelta*i))
        textLabel.y = int(yb+(ydelta*i))
        time.sleep(0.1)
        # quit Screen saver if button be pressed
        if iots2.button_state:
            cntDelay = 0
    xb = textLabel.x
    xb = textLabel.y
    # Screen saver 
    cntDelay += 1
    if cntDelay>12:
        iots2.screen.brightness = 0.0
    elif cntDelay>8:
        iots2.screen.brightness = 0.2
    elif cntDelay>6:
        iots2.screen.brightness = 0.5
    else :
        iots2.screen.brightness = 1.0
