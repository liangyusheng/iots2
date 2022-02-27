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
`bar10xled`
================================================================================

the board-supported-package for the Bar 10xLED module with MY9221

those interface are used as following:



* Author(s): HiiBot

Implementation Notes
--------------------

**Hardware:**
.. "* `Bar 10xLED module with the driver ic MY9221 "

**Software and Dependencies:**
* Adafruit CircuitPython firmware for the supported boards:
  https://github.com/adafruit/circuitpython/releases

"""
import math
from .my9221 import MY9221

class Bar10xLED(MY9221):

    def __init__(self, clk, dout, green2red=True):
        super().__init__(clk, dout)
        self.__brightnessBuf = bytearray(10)
        self.__brightnessBuf_list = []
        self.__brightnessBuf_list.append(self.__brightnessBuf)
        self.__numGroups = 1
        self.__setGroups = True
        self.__g2r = green2red

    @property
    def groups(self):
        return self.__numGroups
    
    @groups.setter
    def groups(self, value):
        if self.__setGroups:
            self.__setGroups = True
            if 1<value<10:
                self.__numGroups = value
                for i in range(value-1):
                    self.__brightnessBuf_list.append(self.__brightnessBuf)
            else:
                pass # give a error
        else:
            pass
        pass

    def transmitData(self):
        if self.__g2r:
            for g in range(self.__numGroups): 
                self.send16_xBitOne(0)
                self.send16_xBitOne(0)
                self.send16_xBitOne(0)
                for i in range(4):
                    self.send16_xBitOne(self.__brightnessBuf_list[g][6+i])
                for i in range(6):
                    self.send16_xBitOne(self.__brightnessBuf_list[g][5-i])
        else:
            for g in range(self.__numGroups): 
                self.send16_xBitOne(0)
                self.send16_xBitOne(0)
                self.send16_xBitOne(0)
                for i in range(4):
                    self.send16_xBitOne(self.__brightnessBuf_list[g][3-i])
                for i in range(6):
                    self.send16_xBitOne(self.__brightnessBuf_list[g][4+i])
        self.latchTiming()
    
    def setLevel(self, level=3.0, group=0):
        level = max(level, 0.0)
        level = min(9.9, level)
        integerPart = math.floor(level)
        fractionalPart = max(0.0, (level - integerPart))
        int_fP = self.brightnessMap(fractionalPart)  # integer
        int_iP = int(integerPart)                    # integer
        for k in range(int_iP): 
            self.__brightnessBuf_list[group][k] = 8
        self.__brightnessBuf_list[group][int_iP] = int_fP
        for k in range(10-int_iP-1):
            self.__brightnessBuf_list[group][int_iP+1+k] = 0
        self.transmitData()


