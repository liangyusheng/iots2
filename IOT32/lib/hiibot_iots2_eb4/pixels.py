# The MIT License (MIT)
#
# Copyright (c) 2021 HiiBot for Hangzhou Leban Tech. Ltd
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
"""
`iots2 extend board -- EB4`
================================================================================

the board-supported-package for the CAN-2xUART to support HiiBot IoTs2 module, include
1) 2x CAN2.0B communication interface, IO3(CANTx) and IO4(CANRx) for CAN0, 
   IO17(UART1RxD) and IO18(UART1TxD) for CAN1 with TT-CAN module
2) 1x RS485 communication interface, IO43(UART0TxD), IO44(UART0RxD), and IO0(nTXEN) were used (busio.UART)
3) 1x I2C (Grove-4P-2.0mm) interface, IO5(SDA) and IO6(SCL) were used
4) 6x Digital In channel, IO7(DI0)~IO12(DI5) were used, LOW is Closed; HIGH is Opened
5) 2x Digital Out channel, IO40(DO0), IO41(DO1) were used, LOW is Off; HIGH is On 
6) 1x NeoPixel RGB pixels, IO42 be used

those interface are used as following:


* Author(s): HiiBot

Implementation Notes
--------------------

**Hardware:**
.. "* `HiiBot IoTs2 - a funny production with WiFi`_"

**Software and Dependencies:**
* Adafruit CircuitPython firmware for the supported boards:
  https://github.com/adafruit/circuitpython/releases
 * Adafruit's Bus Device library: https://github.com/adafruit/Adafruit_CircuitPython_BusDevice
 * Adafruit's Register library: https://github.com/adafruit/Adafruit_CircuitPython_Register

"""
import time
import math
import random
import board
import neopixel

__version__ = "0.1.0-auto.0"
__repo__ = "https://github.com/HiiBot/Hiibot_CircuitPython_IoTs2.git"

class PIXELS:

    def __init__(self, pixels_nums=6, bright=0.5, color=None):
        # pixels
        self._pixels = neopixel.NeoPixel( 
                    board.IO42, pixels_nums,  # pin, number of pixels
                    brightness=bright,        # the default brightness
                    auto_write=False, pixel_order=neopixel.GRB )
        self.colorList = []
        if not ( isinstance(color, tuple) and (len(color)==3) ):
            color = (255, 255, 255)
        for i in range(pixels_nums):
            self.colorList.append(color)
        self._pixels.fill(color)
        self._pixels.show()
        self._pixelsDrawAnimation_peakValue = 0
        self._ci = 0
        # for debug (default colors)
        print( [rgb for rgb in self._pixels.pixels] )

    @property
    def pixels(self):
        return self._pixels

    @property
    def bright(self):
        return self._pixels.brightness
    
    @bright.setter
    def bright(self, value):
        self._pixels.brightness = value
        self._pixels.show()

    def shiftRotateLeft(self):
        __xt = self._pixels[0]
        for i in range(self._pixels.n-1):
            self._pixels[i] = self._pixels[i+1]
        self._pixels[self._pixels.n-1] = __xt
        self._pixels.show()

    def shiftRotateRight(self):
        __xt = self._pixels[self._pixels.n-1]
        for i in range(self._pixels.n-1):
            self._pixels[self._pixels.n-1-i] = self._pixels[self._pixels.n-2-i]
        self._pixels[0] = __xt
        self._pixels.show()

    def drawPattern(self, list_colors=None):
        if list_colors is None:
            return
        for i in range( min(self._pixels.n, len(list_colors)) ):
            self._pixels[i]=list_colors[i]
        self._pixels.show()

    def fillPixels(self, cv):
        self._pixels.fill(cv)
        self._pixels.show()

    def clearPixels(self):
        self.fillPixels( (0,0,0) )

    def _colorsWheel(self, pos):
        if pos < 0 or pos > 255:
            r = g = b = 0
        elif pos < 85:
            r = int(pos * 3)
            g = int(255 - pos * 3)
            b = 0
        elif pos < 170:
            pos -= 85
            r = int(255 - pos * 3)
            g = 0
            b = int(pos * 3)
        else:
            pos -= 170
            r = 0
            g = int(pos * 3)
            b = int(255 - pos * 3)
        return (r, g, b)

    def drawRainbow(self, c):
        """The NeoPixel RGB LED (x n) show rainbow strip .

        This example show Rainbow on the NeoPixel.

        To use with the IoTs2 and EB4:

        .. code-block:: python

            from hiibot_iots2_eb4.pixels import PIXELS
            pixels = PIXELS(10, 0.5, (200, 200, 200)) 
            c = 0
            while True:
                pixels.drawRainbow( c )
                c+=5
                if c>255:
                    c=0
        """
        for i in range(self._pixels.n):
            pixel_index = (i*256//self._pixels.n) + c
            self._pixels[i] = self._colorsWheel(pixel_index & 255)
        self._pixels.show()

    def drawPillar(self, m, minValue=10, maxValue=500, peakColor=(100,0,255)):
        """The NeoPixel RGB LED (x n).

        This example show lighting pillar with the NeoPixel and variable.

        To use with the IoTs2 and EB4:

        .. code-block:: python

            from hiibot_iots2_eb4.pixels import PIXELS
            pixels = PIXELS(10, 0.5, (200, 200, 200))
            while True:
                pixels.drawPillar( var, minLevel, maxLevel, (100,0,255) )
        """
        self._pixels.fill(0)
        __minV = minValue
        __maxV = maxValue
        constrainedValue = max( __minV, min(m, __maxV) )
        normalizedValue = (constrainedValue - __minV) / (__maxV - __minV)
        c = math.pow(normalizedValue, 0.630957) * self._pixels.n
        for i in range(self._pixels.n):
            if i < c:
                self._pixels[i] = 200, i*(255//self._pixels.n), 0
            if c >= self._pixelsDrawAnimation_peakValue:
                self._pixelsDrawAnimation_peakValue = min(c, self._pixels.n-1)
            elif self._pixelsDrawAnimation_peakValue > 0:
                self._pixelsDrawAnimation_peakValue = self._pixelsDrawAnimation_peakValue-1
            if self._pixelsDrawAnimation_peakValue > 0:
                self._pixels[int(self._pixelsDrawAnimation_peakValue)] = peakColor
        self._pixels.show()

    def showAnimation_star(self, ts=0.2):
        """The NeoPixel RGB LED (x n) show rainbow strip .

        This example show star effect on the NeoPixel.

        To use with the IoTs2 and EB4:

        .. code-block:: python

            from hiibot_iots2_eb4.pixels import PIXELS
            pixels = PIXELS(10, 0.5, (200, 200, 200))

            while True:
                pixels.showAnimation_star( 2 )
        """
        if ts>=0.2:
            self._pixels.fill(0)
            self._pixels.show()
            nt = int(ts/0.2)
            for i in range(nt):
                rf=0.5*(random.random())
                r = int(rf*10.0)
                r = min(r, 4)
                r = max(0, r)
                self._pixels[r]=(255,255,255)
                self._pixels.show()
                time.sleep(0.02)
                self.pixels[r]=(0,0,0)
                self.pixels.show()
                time.sleep(0.17)

    def showAnimation_rainbow(self, ts=1.0):
        """The NeoPixel RGB LED (x 5) show rainbow strip .

        This example show Rainbow on the NeoPixel.

        To use with the IoTs2 and EB4:

        .. code-block:: python

            from hiibot_iots2_eb4.pixels import PIXELS
            pixels = PIXELS(10, 0.5, (200, 200, 200))

            while True:
                pixels.showAnimation_rainbow( 2 )
        """
        if ts>=0.2:
            nt = int(ts/0.01)
            for j in range(nt):
                for i in range(self._pixels.n):
                    pixel_index = (i*256//self._pixels.n) + self._ci
                    self._pixels[i] = self._colorsWheel(pixel_index & 255)
                self._pixels.show()
                self._ci+=1
                if self._ci>255: self._ci=0
                time.sleep(0.01)

    def showAnimation_comet(self, ts=1.0):
        """The NeoPixel RGB LED (x n) show rainbow strip .

        This example show comet effect on the NeoPixel.

        To use with the IoTs2 and EB4:

        .. code-block:: python

            from hiibot_iots2_eb4.pixels import PIXELS
            pixels = PIXELS(10, 0.5, (200, 200, 200))

            while True:
                pixels.showAnimation_comet( 2 )
        """
        if ts>=0.1:
            nt = int(ts/0.1)
            colors_comet = [(30,0,90),(50,0,100),(70,0,100),(140,0,140),(200,0,200)]
            for i in range(self._pixels.n):
                self._pixels[i] = colors_comet[i%5]
            self._pixels.show()
            for i in range(nt):
                ct = self._pixels[4]
                for j in range(4, 0, -1):
                    self._pixels[j] = self._pixels[j-1]
                self._pixels[0] = ct
                self._pixels.show()
                time.sleep(0.1)

    def showAnimation_wipe(self, ts=2.0):
        """The NeoPixel RGB LED (x n) show rainbow strip .

        This example show wipe effect on the NeoPixel.

        To use with the IoTs2 and EB4:

        .. code-block:: python

            from hiibot_iots2_eb4.pixels import PIXELS
            pixels = PIXELS(10, 0.5, (200, 200, 200))

            while True:
                pixels.showAnimation_wipe( 2 )
        """
        if ts>=0.2:
            self._pixels.fill(0)
            nt = int(ts/0.2)
            ci = 0
            mod = 0
            for i in range(nt):
                if mod==0:
                    self._pixels[ci]=(80,0,200)
                else:
                    self._pixels[ci]=(0,0,0)
                self._pixels.show()
                ci+=1
                if ci>4:
                    if mod==1: mod=0
                    else: mod=1
                    ci=0;
                time.sleep(0.2)

