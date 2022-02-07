import time
import random
import displayio
from adafruit_displayio_layout.widgets.icon_animated import IconAnimated
from hiibot_iots2 import IoTs2
iots2 = IoTs2()
screen = iots2.screen

IconAnimated.init_class(screen, max_scale=1.5, max_icon_size=(48, 48), max_color_depth=255)

icon_zoom = IconAnimated(
    "Zoom",
    "imgs/cp_sprite_sheet.bmp",
    x=30,
    y=50,
    on_disk=True,
    scale=2.0,  # zoom animation
    angle=5,
)

icon_shrink = IconAnimated(
    "Shrink",
    "imgs/cp_sprite_sheet.bmp",
    x=150,
    y=50,
    on_disk=True,
    scale=0.5,  # shrink animation
    angle=-10,
)

icons = [icon_zoom, icon_shrink]
contains = [(30, 50), (150, 50),]

main_group = displayio.Group()
main_group.append(icon_zoom)
main_group.append(icon_shrink)

screen.show(main_group)

COOLDOWN_TIME = 0.25
LAST_PRESS_TIME = -1

screen.auto_refresh = True
selected = None
while True:
    time.sleep(0.05)
    if iots2.button_state:
        selected = random.randint(0,1)
        icons[selected].zoom_animation( contains[selected] )
        while iots2.button_state:
            pass  # waiting to release button
        icons[selected].zoom_out_animation( contains[selected] )
    else:
        pass
