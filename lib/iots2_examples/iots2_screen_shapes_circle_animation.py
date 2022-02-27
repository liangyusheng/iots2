import time
import displayio
from adafruit_display_shapes.circle import Circle
from hiibot_iots2 import IoTs2
iots2 = IoTs2()
screen = iots2.screen

# Make the display context
context_group = displayio.Group()

# Make a background color fill
color_bitmap = displayio.Bitmap(screen.width, screen.height, 1)
color_palette = displayio.Palette(1)
color_palette[0] = 0x000000
bg_sprite = displayio.TileGrid(color_bitmap, pixel_shader=color_palette, x=0, y=0)
context_group.append(bg_sprite)

# Setting up the Circle starting position
posx, posy = 50, 50

# Define Circle characteristics
circle_radius = 20
circle = Circle(posx, posy, circle_radius, fill=0x00FF00, outline=0xFF00FF)
context_group.append(circle)

# Define Circle Animation Steps
delta_x, delta_y = 2, 2

# Showing the items on the screen
screen.show(context_group)

while True:
    if circle.y + circle_radius >= screen.height - circle_radius:
        delta_y = -1
    if circle.x + circle_radius >= screen.width - circle_radius:
        delta_x = -1
    if circle.x - circle_radius <= 0 - circle_radius:
        delta_x = 1
    if circle.y - circle_radius <= 0 - circle_radius:
        delta_y = 1
    circle.x = circle.x + delta_x
    circle.y = circle.y + delta_y
    time.sleep(0.001)
