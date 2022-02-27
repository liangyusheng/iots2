import os
import time
import random
import displayio
from adafruit_bitmap_font import bitmap_font
from adafruit_button import Button
from hiibot_iots2 import IoTs2
iots2 = IoTs2()
screen = iots2.screen

# the current working directory (where this file is)
cwd = ("/" + __file__).rsplit("/", 1)[0]
fonts = [
    file
    for file in os.listdir(cwd + "/fonts/")
    if (file.endswith(".bdf") and not file.startswith("._"))
]
for i, filename in enumerate(fonts):
    fonts[i] = cwd + "/fonts/" + filename
print(fonts)
THE_FONT = "/fonts/Arial-12.bdf"
DISPLAY_STRING = "Button Text"

# Make the display context
splash = displayio.Group()
screen.show(splash)
BUTTON_WIDTH = 80
BUTTON_HEIGHT = 40
BUTTON_MARGIN = 20

##########################################################################
# Make a background color fill
color_bitmap = displayio.Bitmap(screen.width, screen.height, 1)
color_palette = displayio.Palette(1)
color_palette[0] = 0x404040
bg_sprite = displayio.TileGrid(color_bitmap, pixel_shader=color_palette, x=0, y=0)
print(bg_sprite.x, bg_sprite.y)
splash.append(bg_sprite)
##########################################################################

# Load the font
font = bitmap_font.load_font(THE_FONT)

buttons = []
# Default button styling:
button_0 = Button(
    x=BUTTON_MARGIN,
    y=BUTTON_MARGIN,
    width=BUTTON_WIDTH,
    height=BUTTON_HEIGHT,
    label="button0",
    label_font=font,
)
buttons.append(button_0)

# a shadowroundrect
button_1 = Button(
    x=BUTTON_MARGIN * 2 + BUTTON_WIDTH,
    y=BUTTON_MARGIN,
    width=BUTTON_WIDTH,
    height=BUTTON_HEIGHT,
    label="button1",
    label_font=font,
    label_color=0x00FF00,
    fill_color=0x0000FF,
    outline_color=0x101010,
    style=Button.SHADOWROUNDRECT,
)
buttons.append(button_1)

# Transparent button with text
button_2 = Button(
    x=BUTTON_MARGIN,
    y=BUTTON_MARGIN * 2 + BUTTON_HEIGHT,
    width=BUTTON_WIDTH,
    height=BUTTON_HEIGHT,
    label="button2",
    label_font=font,
    label_color=0x0,
    fill_color=None,
    outline_color=None,
)
buttons.append(button_2)

# a roundrect and various colorings
button_3 = Button(
    x=BUTTON_MARGIN * 2 + BUTTON_WIDTH,
    y=BUTTON_MARGIN * 2 + BUTTON_HEIGHT,
    width=BUTTON_WIDTH,
    height=BUTTON_HEIGHT,
    label="button3",
    label_font=font,
    label_color=0x0000FF,
    fill_color=0x00FF00,
    outline_color=0xFF0000,
    style=Button.ROUNDRECT,
)
buttons.append(button_3)

for b in buttons:
    splash.append(b)

sb = 0
while True:
    iots2.button_update()
    if iots2.button_wasPressed:
        sb = random.randint(0, 3)
        if 0<=sb<4:
            buttons[sb].selected = True
            time.sleep(0.2)
            buttons[sb].selected = False
