import time
import random
import displayio
import terminalio
from adafruit_bitmap_font import bitmap_font
from adafruit_button import Button
from hiibot_iots2 import IoTs2
iots2 = IoTs2()
screen = iots2.screen

# Load the font
font = bitmap_font.load_font("/fonts/Arial-12.bdf")
#font = terminalio.FONT

SHOW_BUTTONS = True

# Make the display context
splash = displayio.Group()

# the current working directory (where this file is)
cwd = ("/" + __file__).rsplit("/", 1)[0]

spots = []
spots.append({"label": "1", "pos": ( 10, 10), "size": (60, 25), })
spots.append({"label": "2", "pos": ( 90, 10), "size": (60, 25), })
spots.append({"label": "3", "pos": (170, 10), "size": (60, 25), })
spots.append({"label": "_Aa_Bb_", "pos": ( 10, 50), "size": (60, 80), })
spots.append({"label": "CcDd", "pos": ( 90, 50), "size": (60, 80), })
spots.append({"label": "EeFf", "pos": (170, 50), "size": (60, 80), })

buttons = []
for spot in spots:
    fill = outline = None
    if SHOW_BUTTONS:
        fill = None
        outline = 0x00FF00
    button = Button(
        x=spot["pos"][0],
        y=spot["pos"][1],
        width=spot["size"][0],
        height=spot["size"][1],
        fill_color=fill,
        outline_color=outline,
        label=spot["label"],
        label_font=font, 
        label_color = 0xFF0000,
    )
    splash.append(button)
    buttons.append(button)

screen.show(splash)
last_pressed = None
currently_pressed = None

while True:
    iots2.button_update()
    if iots2.button_wasPressed:
        last_pressed = currently_pressed
        currently_pressed = random.randint(0,5)
        while currently_pressed==last_pressed:
            currently_pressed = random.randint(0,5)
        if not last_pressed is None:
            buttons[last_pressed].selected = False
        if 0<=currently_pressed<=5:
            buttons[currently_pressed].selected = True
