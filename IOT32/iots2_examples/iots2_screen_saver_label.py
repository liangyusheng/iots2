import time
import displayio
import terminalio
from adafruit_display_text import label
from hiibot_iots2 import IoTs2
iots2 = IoTs2()
iots2.screen.rotation = 90
text_group = displayio.Group(scale=2)
text0 = label.Label(terminalio.FONT, x=0, y=9, text="", color=(255,0,0))
text_group.append(text0)
text1 = label.Label(terminalio.FONT, x=0, y=27, text="hello IoTs2", color=(0,0,255))
text_group.append(text1)
iots2.screen.show(text_group)
stateList = ['Released', 'Pressed']
cnt_screenSaved = 0
while True:
    time.sleep(0.02)
    sBtn = iots2.button_state
    text0.text = "button: {:d} / {}".format(sBtn, stateList[sBtn])
    if sBtn:
        text0.color = (0,255,0)
        cnt_screenSaved = 0
    else:
        text0.color = (255,0,0)
    cnt_screenSaved += 1
    if cnt_screenSaved>250:
        iots2.screen.brightness = 0.0
    elif cnt_screenSaved>200:
        iots2.screen.brightness = 0.2
    elif cnt_screenSaved>125:
        iots2.screen.brightness = 0.5
    else:
        iots2.screen.brightness = 1.0
    