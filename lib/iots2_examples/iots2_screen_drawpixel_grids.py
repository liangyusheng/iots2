import time
import displayio
from hiibot_iots2 import IoTs2
iots2 = IoTs2()
iots2.screen.rotation = 90
grid=8  # modify this variable to chage the final effect
num = 240//grid
bitmap = displayio.Bitmap(grid, grid, 2)
for i in range(grid):
    bitmap[i, i] = 1
    bitmap[grid-i-1, i] = 1

palette = displayio.Palette(2)
palette[0] = 0x000000 # black
palette[1] = 0xFF00FF # purple

tile = displayio.TileGrid(bitmap,
                          pixel_shader=palette,
                          width=num,
                          height=num,
                          tile_width=grid,
                          tile_height=grid)

group = displayio.Group()
group.append(tile)
iots2.screen.show(group)

while True:
    time.sleep(1)