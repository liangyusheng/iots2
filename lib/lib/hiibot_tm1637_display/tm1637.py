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
`hiibot_tm1637`
================================================================================

the board-supported-package for the Dots/Segment-style dispaly with TM1637

those interface are used as following:



* Author(s): HiiBot

Implementation Notes
--------------------

**Hardware:**
.. "* `all display with the driver ic TM1637 "

**Software and Dependencies:**
* Adafruit CircuitPython firmware for the supported boards:
  https://github.com/adafruit/circuitpython/releases

"""
import time
from digitalio import DigitalInOut, Direction

__version__ = "0.1.0-auto.0"
__repo__ = "https://github.com/HiiBot/Hiibot_CircuitPython_IoTs2.git"

class TM1637:

    CONTROL_COMM = bytes(b'\x40\xC0\x87\x42')  # command 1~4
    BITMASK = bytes(b'\x01\x02\x04\x08\x10\x20\x40\x80') # LSB is the first
    KEYVALUE = [0xFF, 0xE9, 0xEB, 0xEA, 0xED, 0xEC]
    
    def __init__(self, clk, dio, brightness):
        self._clk = DigitalInOut(clk)
        self._clk.direction = Direction.INPUT
        self._dio = DigitalInOut(dio)
        self._dio.direction = Direction.INPUT
        self._brightness = brightness
    
    def writeByte(self, byte_data):
        # send 8 bits
        for i in range(8):
            self._clk.direction = Direction.OUTPUT # CLK to LOW
            self._delayBit()
            if (self.BITMASK[i] & byte_data) == self.BITMASK[i]:
                self._dio.direction = Direction.INPUT  # '1' 
            else:
                self._dio.direction = Direction.OUTPUT # '0'
            self._delayBit()
            self._clk.direction = Direction.INPUT  # CLK to HIGH
            self._delayBit()
        # to get a ACK bit, the timing: CLK to low and DIO to high
        self._clk.direction = Direction.OUTPUT # CLK to LOW
        self._dio.direction = Direction.INPUT  # DIO to HIGH (get ACK)
        self._delayBit()
        self._clk.direction = Direction.INPUT  # CLK to HIGH
        self._delayBit()
        ack = self._dio.value
        if not ack:
            self._dio.direction = Direction.OUTPUT
        self._delayBit()
        self._clk.direction = Direction.OUTPUT # CLK to LOW
        self._delayBit()
    
    def readByte(self):
        rd = 0x00
        self._dio.direction = Direction.INPUT  # DIO to HIGH
        self._delayBit()
        for i in range(8):
            self._clk.direction = Direction.OUTPUT # CLK to LOW
            self._delayBit()
            self._clk.direction = Direction.INPUT  # CLK to HIGH
            self._delayBit()
            if self._dio.value:
                rd |= self.BITMASK[i]
            else:
                pass
        # get a ACK
        self._clk.direction = Direction.INPUT  # CLK to HIGH
        self._delayBit()
        ack = self._dio.value
        if not ack:
            self._dio.direction = Direction.OUTPUT
        self._delayBit()
        self._clk.direction = Direction.OUTPUT # CLK to LOW
        self._delayBit()
        return rd
    
    def start(self):
        # DIO to LOW and CLK hold HIGH as a start timing 
        self._dio.direction = Direction.OUTPUT
        self._delayBit()
        
    def stop(self):
        # when CLK is a HIGH level and DIO changes from LOW to HIGH level, data input stop
        self._dio.direction = Direction.OUTPUT # DIO to LOW
        self._delayBit()
        self._clk.direction = Direction.INPUT  # CLK to HIGH
        self._delayBit()
        self._dio.direction = Direction.INPUT  # DIO to HIGH
        self._delayBit()

    def writeCommd1(self):
        self.start()
        self.writeByte(self.CONTROL_COMM[0])
        self.stop()    

    def writeCommd3(self):
        self.start()
        self.writeByte(self.CONTROL_COMM[2]+self._brightness)
        self.stop()    

    @property
    def brightness(self):
        """The brightness. Range 0~7"""
        return self._brightness

    @brightness.setter
    def brightness(self, value):
        if value<0:
            value = 0
        if value>7:
            value = 7
        self._brightness = value
    
    def _delayBit(self, dt_us=10):
        ns = dt_us*1000  # to ns
        st = time.monotonic_ns()
        while True:
            et = time.monotonic_ns()
            if (et-st) >= ns:
                break

    def setDots(self, dotList, pos):
        self.writeCommd1()
        self.start()
        self.writeByte(self.CONTROL_COMM[1]+pos)
        for i in range( len(dotList) ):
            self.writeByte( dotList[i] )
        self.stop()
        self.writeCommd3()

    def scanKeys(self):
        kv = 0x00
        self.start()
        self.writeByte(self.CONTROL_COMM[3])
        kv = self.readByte()
        ik = 0
        for k in self.KEYVALUE:
            if kv==k:
                break
            ik += 1
        return ik
