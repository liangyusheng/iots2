import time
import random
import displayio
import terminalio
from adafruit_display_text import label
from adafruit_display_shapes.sparkline import Sparkline
from adafruit_display_shapes.line import Line
from adafruit_display_shapes.rect import Rect
from hiibot_iots2 import IoTs2
iots2 = IoTs2()
screen = iots2.screen

# Baseline size of the sparkline chart, in pixels.
chart_width = screen.width - 20
chart_height = screen.height - 16
font = terminalio.FONT
line_color = 0xFFFFFF

# Setup the first bitmap and sparkline
# This sparkline has no background bitmap
# mySparkline1 uses a vertical y range between 0 to 10 and will contain a
# maximum of 40 items
sparkline1 = Sparkline(
    width=chart_width,
    height=chart_height,
    max_items=40,
    y_min=0,
    y_max=10,
    x=20,
    y=9,
    color=line_color,
)

# Label the y-axis range
text_xoffset = -10
text_label1a = label.Label(font=font, text=str(sparkline1.y_top), color=line_color)  # yTop label
text_label1a.anchor_point = (1, 0.5)  # set the anchorpoint at right-center
text_label1a.anchored_position = (sparkline1.x + text_xoffset, sparkline1.y,)  # set the text anchored position to the upper right of the graph

text_label1b = label.Label(font=font, text=str(sparkline1.y_bottom), color=line_color)  # yTop label
text_label1b.anchor_point = (1, 0.5)  # set the anchorpoint at right-center
text_label1b.anchored_position = (sparkline1.x + text_xoffset,sparkline1.y + chart_height,)  # set the text anchored position to the upper right of the graph

bounding_rectangle = Rect(sparkline1.x, sparkline1.y, chart_width, chart_height, outline=line_color)

my_group = displayio.Group()
my_group.append(sparkline1)
my_group.append(text_label1a)
my_group.append(text_label1b)
my_group.append(bounding_rectangle)

total_ticks = 10

for i in range(total_ticks + 1):
    x_start = sparkline1.x - 5
    x_end = sparkline1.x
    y_both = int(round(sparkline1.y + (i * (chart_height) / (total_ticks))))
    if y_both > sparkline1.y + chart_height - 1:
        y_both = sparkline1.y + chart_height - 1
    my_group.append(Line(x_start, y_both, x_end, y_both, color=line_color))

# Set the display to show my_group that contains the sparkline and other graphics
screen.show(my_group)

# Start the main loop
while True:
    # Turn off auto_refresh to prevent partial updates of the screen during updates
    # of the sparkline drawing
    screen.auto_refresh = False

    # add_value: add a new value to a sparkline
    # Note: The y-range for mySparkline1 is set to 0 to 10, so all these random
    # values (between 0 and 10) will fit within the visible range of this sparkline
    sparkline1.add_value(random.uniform(0, 10))

    # Turn on auto_refresh for the display
    screen.auto_refresh = True

    # The display seems to be less jittery if a small sleep time is provided
    # You can adjust this to see if it has any effect
    time.sleep(0.01)
