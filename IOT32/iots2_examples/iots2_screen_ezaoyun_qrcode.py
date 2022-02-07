import displayio
import adafruit_miniqr
from hiibot_iots2 import IoTs2
iots2 = IoTs2()
screen = iots2.screen

def bitmap_QR(matrix):
    BORDER_PIXELS = 2 # monochome (2 color) palette
    # bitmap the size of the screen, monochrome (2 colors)
    bitmap = displayio.Bitmap(
        matrix.width + 2 * BORDER_PIXELS, matrix.height + 2 * BORDER_PIXELS, 2
    )
    # raster the QR code
    for y in range(matrix.height):  # each scanline in the height
        for x in range(matrix.width):
            if matrix[x, y]:
                bitmap[x + BORDER_PIXELS, y + BORDER_PIXELS] = 1
            else:
                bitmap[x + BORDER_PIXELS, y + BORDER_PIXELS] = 0
    return bitmap

qr = adafruit_miniqr.QRCode(qr_type=3, error_correct=adafruit_miniqr.L)
qr.add_data(b"https://www.ezaoyun.com")
qr.make()

# generate the 1-pixel-per-bit bitmap
qr_bitmap = bitmap_QR(qr.matrix)
# We'll draw with a classic black/white palette
palette = displayio.Palette(2)
palette[0] = 0xFFFFFF
palette[1] = 0x000000
# we'll scale the QR code as big as the display can handle
scale = min( screen.width // qr_bitmap.width, screen.height // qr_bitmap.height )
# then center it!
pos_x = int(((screen.width / scale) - qr_bitmap.width) / 2)
pos_y = int(((screen.height / scale) - qr_bitmap.height) / 2)
qr_img = displayio.TileGrid(qr_bitmap, pixel_shader=palette, x=pos_x, y=pos_y)

splash = displayio.Group(scale=scale)
splash.append(qr_img)
screen.show(splash)

# Hang out forever
while True:
    pass
