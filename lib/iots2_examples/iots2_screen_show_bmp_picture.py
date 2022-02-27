import time
import random
import displayio
import adafruit_imageload
from hiibot_iots2 import IoTs2
iots2 = IoTs2()
screen = iots2.screen
screen.rotation = 180

bitmap, palette = adafruit_imageload.load("/imgs/purple.bmp",
                                          bitmap=displayio.Bitmap,
                                          palette=displayio.Palette)
# Create a TileGrid to hold the bitmap
tile_grid = displayio.TileGrid(bitmap, pixel_shader=palette,
                               tile_width=160, tile_height=240, # pixels number
                               width=1, height=1)  # tiles number
# Create a Group to hold the TileGrid
group = displayio.Group()

# Add the TileGrid to the Group
group.append(tile_grid)
screen.show(group)
while True:
    tile_grid[0] = 0
    time.sleep(2.0)
    tile_grid[0] = 1
    time.sleep(2.0)
