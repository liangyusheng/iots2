import time
import displayio
import terminalio
from adafruit_display_text import label
from hiibot_iots2 import IoTs2
iots2 = IoTs2()
iots2.screen.rotation = 90
text_group = displayio.Group(scale=2)
text0 = label.Label(terminalio.FONT, x=0, y=0,  text="", color=(255,0,0))
text1 = label.Label(terminalio.FONT, x=0, y=9,  text="", color=(192,63,0))
text2 = label.Label(terminalio.FONT, x=0, y=18, text="", color=(127,127,0))
text3 = label.Label(terminalio.FONT, x=0, y=27, text="", color=(0,255,0))
text4 = label.Label(terminalio.FONT, x=0, y=36, text="", color=(0,127,127))
text5 = label.Label(terminalio.FONT, x=0, y=45, text="", color=(0,0,255))
text6 = label.Label(terminalio.FONT, x=0, y=54, text="", color=(127,0,127))
text7 = label.Label(terminalio.FONT, x=0, y=63, text="", color=(255,0,0))
labelList = [text0, text1, text2, text3, text4, text5, text6, text7]
for i in range(8):
    text_group.append(labelList[i])
iots2.screen.show(text_group)
stateList = ['Released', 'Pressed']
while True:
    stateBtn = iots2.button_state
    str = "button: {:d} / {}".format(stateBtn, stateList[stateBtn])
    for i in range(8):
        labelList[i].text = str
    time.sleep(0.02)