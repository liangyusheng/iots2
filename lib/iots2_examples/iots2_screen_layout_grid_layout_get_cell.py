import time
import displayio
import terminalio
from adafruit_display_text import label
from adafruit_displayio_layout.layouts.grid_layout import GridLayout
from hiibot_iots2 import IoTs2
iots2 = IoTs2()
screen = iots2.screen
main_group = displayio.Group()
screen.show(main_group)

layout = GridLayout(
    x=10,
    y=10,
    width=200,
    height=100,
    grid_size=(2, 2),
    cell_padding=8,
)
_labels = []

_labels.append(
    label.Label(terminalio.FONT, scale=2, x=0, y=0, text="Hello", background_color=0x770077)
)
layout.add_content(_labels[0], grid_position=(0, 0), cell_size=(1, 1))

_labels.append(
    label.Label(terminalio.FONT, scale=2, x=0, y=0, text="World", background_color=0x007700)
)
layout.add_content(_labels[1], grid_position=(1, 0), cell_size=(1, 1))

_labels.append(label.Label(terminalio.FONT, scale=2, x=0, y=0, text="Hello"))
layout.add_content(_labels[2], grid_position=(0, 1), cell_size=(1, 1))

_labels.append(label.Label(terminalio.FONT, scale=2, x=0, y=0, text="IoTs2"))
layout.add_content(_labels[3], grid_position=(1, 1), cell_size=(1, 1))

main_group.append(layout)


while True:
    layout.get_cell((0, 0)).text = "Happy"
    layout.get_cell((1, 0)).text = "Circuit"
    layout.get_cell((0, 1)).text = "Python"
    layout.get_cell((1, 1)).text = "Day"
    layout.get_cell((0, 1)).background_color = 0x007700
    layout.get_cell((1, 1)).background_color = 0x770077
    time.sleep(1.0)
    layout.get_cell((0, 0)).text = "Hello"
    layout.get_cell((1, 0)).text = "World"
    layout.get_cell((0, 1)).text = "Hello"
    layout.get_cell((1, 1)).text = "IoTs2"
    layout.get_cell((0, 1)).background_color = 0x770077
    layout.get_cell((1, 1)).background_color = 0x007700
    time.sleep(2.0)

