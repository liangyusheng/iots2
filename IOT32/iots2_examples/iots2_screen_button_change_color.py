import time
import displayio
import terminalio
from adafruit_button import Button
from hiibot_iots2 import IoTs2
iots2 = IoTs2()
screen = iots2.screen

BUTTON_X = 70
BUTTON_Y = 45
BUTTON_WIDTH = 100
BUTTON_HEIGHT = 50
BUTTON_STYLE = Button.ROUNDRECT
BUTTON_FILL_COLOR = 0xAA0000
BUTTON_OUTLINE_COLOR = 0x0000FF
BUTTON_LABEL = "IoTs2"
BUTTON_LABEL_COLOR = 0x000000

# Make the display context
splash = displayio.Group()
screen.show(splash)

# Make the button
button = Button(
    x=BUTTON_X,
    y=BUTTON_Y,
    width=BUTTON_WIDTH,
    height=BUTTON_HEIGHT,
    style=BUTTON_STYLE,
    fill_color=BUTTON_FILL_COLOR,
    outline_color=BUTTON_OUTLINE_COLOR,
    label=BUTTON_LABEL,
    label_font=terminalio.FONT,
    label_color=BUTTON_LABEL_COLOR,
)

button.fill_color = 0x00FF00
button.outline_color = 0xFF0000

button.selected_fill = (0, 0, 255)
button.selected_outline = (255, 0, 0)

button.label_color = 0xFF0000
button.selected_label = 0x00FF00

# Add button to the display context
splash.append(button)

# Loop and look for touches
while True:
    if iots2.button_state:
        button.selected = True
        time.sleep(0.01)
    else:
        button.selected = False
