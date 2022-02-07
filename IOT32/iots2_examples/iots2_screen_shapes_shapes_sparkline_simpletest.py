import time
import random
import displayio
from adafruit_display_shapes.sparkline import Sparkline
from hiibot_iots2 import IoTs2
iots2 = IoTs2()
screen = iots2.screen

# Baseline size of the sparkline chart, in pixels.
chart_width = screen.width
chart_height = screen.height

# sparkline1 uses a vertical y range between 0 to 10 and will contain a
# maximum of 40 items
sparkline1 = Sparkline(
    width=chart_width, height=chart_height, max_items=50, y_min=0, y_max=10, x=0, y=0
)

spark_group = displayio.Group()

# add the sparkline into my_group
spark_group.append(sparkline1)

# Add my_group (containing the sparkline) to the display
screen.show(spark_group)

# Start the main loop
while True:
    # turn off the auto_refresh of the display while modifying the sparkline
    screen.auto_refresh = False

    # add_value: add a new value to a sparkline
    # Note: The y-range for mySparkline1 is set to 0 to 10, so all these random
    # values (between 0 and 10) will fit within the visible range of this sparkline
    sparkline1.add_value(random.uniform(0, 10))

    # turn the display auto_refresh back on
    screen.auto_refresh = True

    # The display seems to be less jittery if a small sleep time is provided
    # You can adjust this to see if it has any effect
    time.sleep(0.01)
