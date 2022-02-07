import time
import random
import displayio
from adafruit_displayio_layout.widgets.switch_round import SwitchRound as Switch
from hiibot_iots2 import IoTs2
iots2 = IoTs2()
screen = iots2.screen
switch_group = displayio.Group()

# Create the switch: size = (2*height + touch_padding, height)
switchs = [
    Switch(x= 10, y=10, height=30, touch_padding=10, value=False), 
    Switch(x= 10, y=77, height=30, touch_padding=10, value=False), 
    Switch(x= 80, y=10, height=30, touch_padding=10, value=False), 
    Switch(x= 80, y=77, height=30, touch_padding=10, value=False),
]
contains = [(10, 10), (10, 77), (130, 10), (130, 77)]
for sw in switchs:
    switch_group.append(sw)

# Add my_group to the display
screen.show(switch_group)
sw_selected = None
# Start the main loop
while True:
    iots2.button_update()
    if iots2.button_wasPressed:
        if not sw_selected is None:
            switchs[sw_selected].value = False
            #switchs[sw_selected].selected( (0,0) )
        sw_selected = random.randint(0,3)
        switchs[sw_selected].value = True
        #switchs[sw_selected].selected( contains[sw_selected] )
