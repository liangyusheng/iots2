
import time
import random
import displayio
from adafruit_displayio_layout.widgets.switch_round import SwitchRound as Switch
from hiibot_iots2 import IoTs2
iots2 = IoTs2()
screen = iots2.screen
my_group = displayio.Group()

# Create the switches
switchs = []
my_switch1 = Switch(10, 10)
switchs.append( my_switch1 )
my_group.append( my_switch1 )

my_switch2 = Switch(
    x=120,
    y=10,
    height=30,  # Set height to 30 pixels.  If you do not specify width,
    # it is automatically set to a default aspect ratio
    touch_padding=10,  # add extra boundary for touch response
    value=True,
)  # initial value is set to True
switchs.append( my_switch2 )
my_group.append( my_switch2 )

my_switch3 = Switch(
    x=10,
    y=60,
    height=40,
    fill_color_off=(255, 0, 0),  # Set off colorred, can use hex code (0xFF0000)
    outline_color_off=(80, 0, 0),
    background_color_off=(150, 0, 0),
    background_outline_color_off=(30, 0, 0),
)
switchs.append( my_switch3 )
my_group.append( my_switch3 )

my_switch4 = Switch(
    x=120,
    y=60,
    height=40,
    width=110,  # you can set the width manually but it may look weird
)
switchs.append( my_switch4 )
my_group.append( my_switch4 )

my_switch8 = Switch(
    x=0,
    y=0,  # this is a larger, vertical orientation switch
    height=60,
    horizontal=False,  # set orientation to vertical
    flip=True,  # swap the direction
)
# use anchor_point and anchored_position to set the my_switch8 position
# relative to the display size.
my_switch8.anchor_point = (1.0, 1.0)
# the switch anchor_point is the bottom right switch corner
my_switch8.anchored_position = (screen.width - 10, screen.height - 10)
# the switch anchored_position is 10 pixels from the display
# lower right corner
switchs.append( my_switch8 )
my_group.append( my_switch8 )

# Add my_group to the screen
screen.show(my_group)

# Start the main loop
while True:
    for sw in switchs:
        sw.value = True
        time.sleep(0.2)
        sw.value = False
        time.sleep(0.3)