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
`circular24xled`
================================================================================

the board-supported-package for the circular 24xLED module with MY9221

those interface are used as following:



* Author(s): HiiBot

Implementation Notes
--------------------

**Hardware:**
.. "* `Circular 24xLED module with the driver ic MY9221 "

**Software and Dependencies:**
* Adafruit CircuitPython firmware for the supported boards:
  https://github.com/adafruit/circuitpython/releases

"""
from .my9221 import MY9221

class Circular24xLED(MY9221):

    def __init__(self, clk, dout):
        super().__init__(clk, dout)
        self.__brightnessBuf = bytearray(24)
        for i in range(len(self.__brightnessBuf)):
            self.__brightnessBuf[i] = 0x00

    def transmitData(self):
        self.send16_xBitOne(0)
        for i in range(6):
            self.send16_xBitOne(self.__brightnessBuf[5-i])
        for i in range(6):
            self.send16_xBitOne(self.__brightnessBuf[11-i])
        self.send16_xBitOne(0)
        for i in range(6):
            self.send16_xBitOne(self.__brightnessBuf[17-i])
        for i in range(6):
            self.send16_xBitOne(self.__brightnessBuf[23-i])
        self._dout.value = 0
        self.latchTiming()
    
    def setBrightness(self, blist):
        if len(blist)>=24:
            for i in range(24):
                self.__brightnessBuf[i] = self.brightnessMap(blist[i])
            self.transmitData()

    def leftRotate(self):
        tp = self.__brightnessBuf[0]
        for i in range(23):
            self.__brightnessBuf[i] = self.__brightnessBuf[i+1]
        self.__brightnessBuf[23] = tp
        self.transmitData()

    def rightRotate(self):
        tp = self.__brightnessBuf[23]
        for i in range(23):
            self.__brightnessBuf[23-i] = self.__brightnessBuf[22-i]
        self.__brightnessBuf[0] = tp
        self.transmitData()

    def leftShift(self):
        for i in range(23):
            self.__brightnessBuf[i] = self.__brightnessBuf[i+1]
        self.__brightnessBuf[23] = 0.0
        self.transmitData()

    def rightShift(self):
        for i in range(23):
            self.__brightnessBuf[23-i] = self.__brightnessBuf[22-i]
        self.__brightnessBuf[0] = 0.0
        self.transmitData()
