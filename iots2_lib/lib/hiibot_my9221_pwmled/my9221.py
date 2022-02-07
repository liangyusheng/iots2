# The MIT License (MIT)
#
# Copyright (c) 2020 HiiBot for Hangzhou Leban Tech. Ltd
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
`hiibot_my9221`
================================================================================

the board-supported-package for the 12-PWM LED (3*4) modules with MY9221

those interface are used as following:



* Author(s): HiiBot

Implementation Notes
--------------------

**Hardware:**
.. "* `all LED module with the driver ic MY9221 "

**Software and Dependencies:**
* Adafruit CircuitPython firmware for the supported boards:
  https://github.com/adafruit/circuitpython/releases

"""
import time
from digitalio import DigitalInOut, Direction, Pull

__version__ = "0.1.0-auto.0"
__repo__ = "https://github.com/HiiBot/Hiibot_CircuitPython_IoTs2.git"

class MY9221:

    GBL_CMDMODE = bytes(b'\x00\x00')   # 2 bytes: 0x0010 
    BITMASK = bytes(b'\x80\x40\x20\x10\x08\x04\x02\x01')  # MSB is the first

    def __init__(self, clk, dout):
        self._clk = DigitalInOut(clk)
        self._clk.switch_to_output(value=0) 
        self._dout = DigitalInOut(dout)
        self._dout.switch_to_output(value=0)

    def _delayBit(self, dt_us=10):
        ns = dt_us*40  # to ns
        st = time.monotonic_ns()
        while True:
            et = time.monotonic_ns()
            if (et-st) >= ns:
                break

    def latchTiming(self):
        self._dout.value = 0
        time.sleep(0.0001)
        for i in range(4):
            self._dout.value = 1
            self._dout.value = 0

    def send16_xBitOne(self, oneNum):
        self._dout.value = 0
        for k in range(16-oneNum):
            self._clk.value = not self._clk.value
        self._dout.value = 1
        for i in range(oneNum):
            self._clk.value = not self._clk.value

    def brightnessMap(self, brightness):
        return  min(8, int(brightness*8.0)) 
    
    def clrAll(self):
        self._dout.value = 0
        for x in range(416):
            self._clk.value = not self._clk.value
        self.latchTiming()

    def setAll(self, brightness=3):
        self.send16_xBitOne(0)
        for x in range(12):
            self.send16_xBitOne(brightness)
        self.send16_xBitOne(0)
        for x in range(12):
            self.send16_xBitOne(brightness)
        self.latchTiming()

