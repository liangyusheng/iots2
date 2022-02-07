import time
import board
import displayio
import adafruit_imageload
from hiibot_iots2 import IoTs2
iots2 = IoTs2()
iots2.screen.rotation = 180
# Load the sprite sheet (bitmap)
sprite_sheet, palette = adafruit_imageload.load("imgs/cp_sprite_sheet.bmp",
                                                bitmap=displayio.Bitmap,
                                                palette=displayio.Palette)
# Create a sprite (tilegrid)
sprite = displayio.TileGrid(sprite_sheet, pixel_shader=palette,
                            tile_width = 16, tile_height = 16, # pixels
                            width = 1, height = 1  # 
                            )
# Create a Group to hold the sprite
group = displayio.Group(scale=4)
# Add the sprite to the Group
group.append(sprite)
# Add the Group to the Display
iots2.screen.show(group)
# Set sprite location
group.x = 40
group.y = 100
# Loop through each sprite in the sprite sheet
source_index = 0
while True:
    sprite[0] = source_index % 6
    source_index += 1
    time.sleep(2)