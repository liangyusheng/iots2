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
`hiibot_digit4display`
================================================================================

the board-supported-package for the 4xdigit 7-segment dispaly with TM1637

those interface are used as following:



* Author(s): HiiBot

Implementation Notes
--------------------

**Hardware:**
.. "* `4xdigit 7-segment dots display with the driver ic TM1637 "

**Software and Dependencies:**
* Adafruit CircuitPython firmware for the supported boards:
  https:#github.com/adafruit/circuitpython/releases

"""
import time
from .tm1637 import TM1637

class Digit4Display(TM1637):
    
    code7Segment = (
                    0b00111111,    # 0
                    0b00000110,    # 1
                    0b01011011,    # 2
                    0b01001111,    # 3
                    0b01100110,    # 4
                    0b01101101,    # 5
                    0b01111101,    # 6
                    0b00000111,    # 7
                    0b01111111,    # 8
                    0b01101111,    # 9, 0x09
                    0b01110111,    # A
                    0b01111100,    # b
                    0b00111001,    # C
                    0b01011110,    # d
                    0b01111001,    # E
                    0b01110001,    # F
                    0b00000000,    # +, blank, 0x10
                    0b01000000,    # -, 0x11
                    0b00000001,    # close eye
                    0b01011101,    # open eye
                    0b01011100     # o, 0x14
                  )
    
    def __init__(self, clk, dio, brightness=3, intervalRefresh=0.5):
        super().__init__(clk, dio, brightness)
        self.__currentSegmentCodeBuf = bytearray(b'\x00\x00\x00\x00')
        self.__onetimes = True
        self.__intervalRefresh_s = intervalRefresh
        self.__st_s_Refresh = time.monotonic()
        self.__rollOver = True
        self.__slideSegmentCodeBuf = bytearray(10)  # 2^32 = 4,294,967,296
        self.__slideValidLenBuf = 0
        self.__slideNowPosi = 0
        self.__slideDrfsmEnable = False
        self.__doubleDotOnFlag = False
        self.__hms = [0,0,0]
        self.__st1_s_stfsm_Refresh = time.monotonic()
        self.__st2_s_stfsm_Refresh = time.monotonic()
    
    @property
    def rollOver(self):
        if self.__rollOver:
            self.__rollOver = False
            return True
        else:
            return False
    
    @property
    def oneTimes(self):
        return self.__onetimes
    
    @oneTimes.setter
    def oneTimes(self, value):
        self.__onetimes = value

    @property
    def intervalRefresh(self):
        return self.__intervalRefresh_s
    
    @intervalRefresh.setter
    def intervalRefresh(self, value):
        self.__intervalRefresh_s = value

    def clrDisplay(self):
        for i in range(len(self.__currentSegmentCodeBuf)):
            self.__currentSegmentCodeBuf[i] = 0
        self.setDots(self.__currentSegmentCodeBuf, 0)
        self.__slideDrfsmEnable = False

    def fillDisplay(self):
        for i in range(len(self.__currentSegmentCodeBuf)):
            self.__currentSegmentCodeBuf[i] = 0xFF
        self.setDots(self.__currentSegmentCodeBuf, 0)
        self.__slideDrfsmEnable = False

    def show4Value(self, value):
        if len(value)==4:
            for i in range(4):
                if value[i]>len(self.code7Segment):
                    value[i]=16
                self.__currentSegmentCodeBuf[i] = self.code7Segment[value[i]]
            self.setDots(self.__currentSegmentCodeBuf, 0)
        else:
            pass # give a error

    def sdrfsm_loop(self):
        if self.__slideDrfsmEnable:
            nt = time.monotonic()
            if (nt - self.__st_s_Refresh) >= self.__intervalRefresh_s:
                self.__st_s_Refresh = nt
                for i in range(3):
                    self.__currentSegmentCodeBuf[i] = self.__currentSegmentCodeBuf[i+1]
                self.__currentSegmentCodeBuf[3] = self.__slideSegmentCodeBuf[self.__slideNowPosi]
                self.setDots(self.__currentSegmentCodeBuf, 0)
                self.__slideNowPosi += 1
                if self.__slideNowPosi >= self.__slideValidLenBuf:
                    self.__rollOver = True
                    self.__slideNowPosi = 0
                    if self.__onetimes:
                        self.__slideDrfsmEnable = False
                    else:
                        # next refresh
                        time.sleep(3*self.__intervalRefresh_s)
                        self.clrDisplay()
                        self.__currentSegmentCodeBuf[3] = self.__slideSegmentCodeBuf[0]
                        self.__slideNowPosi = 1
                        self.setDots(self.__currentSegmentCodeBuf, 0)
                        self.__slideDrfsmEnable = True
                    pass
                pass
            pass
        pass

    def showNumber(self, num, waitdone=True):
        if num>2**32:
            raise ValueError('Input numberic too large (>2**32)')
        if not isinstance(num, int):
            raise ValueError('Only surpport integer data')
        for i in range(4):
            self.__currentSegmentCodeBuf[i] = 0x0
        tn = num
        self.__slideValidLenBuf = len( '{:d}'.format(num) )
        for m in range(len(self.__slideSegmentCodeBuf)):
            self.__slideSegmentCodeBuf[m] = 0x0  # blank
        for k in range(self.__slideValidLenBuf):
            power = 10**(self.__slideValidLenBuf-k-1)
            self.__slideSegmentCodeBuf[k] = self.code7Segment[int(tn/power)]
            tn %= power
        if self.__slideValidLenBuf<=4 :
            b = 4-self.__slideValidLenBuf
            self.__currentSegmentCodeBuf[b:] = self.__slideSegmentCodeBuf[:4-b]
            self.setDots(self.__currentSegmentCodeBuf, 0)
        elif waitdone:
            for i in range(self.__slideValidLenBuf):
                for j in range(3):
                    self.__currentSegmentCodeBuf[j] = self.__currentSegmentCodeBuf[j+1]
                self.__currentSegmentCodeBuf[3] = self.__slideSegmentCodeBuf[i]
                self.setDots(self.__currentSegmentCodeBuf, 0)
                time.sleep(self.__intervalRefresh_s)
                self.__rollOver = True
        else:
            self.__currentSegmentCodeBuf[3] = self.__slideSegmentCodeBuf[0]
            self.setDots(self.__currentSegmentCodeBuf, 0)
            self.__slideNowPosi = 1  # 
            self.__slideDrfsmEnable = True
            self.__st_s_Refresh = time.monotonic()
            self.__rollOver = False

    def showTime(self, f_b, doubledots=True):
        mh, ml = int(f_b[0]//10), int(f_b[0]%10)
        sh, sl = int(f_b[1]//10), int(f_b[1]%10)
        if mh==0:
            self.__currentSegmentCodeBuf[0] = 0
        else:
            self.__currentSegmentCodeBuf[0] = self.code7Segment[mh]
        self.__currentSegmentCodeBuf[1] = self.code7Segment[ml]
        if doubledots:
            self.__currentSegmentCodeBuf[1] |= 0x80
        self.__currentSegmentCodeBuf[2] = self.code7Segment[sh]
        self.__currentSegmentCodeBuf[3] = self.code7Segment[sl]
        self.setDots(self.__currentSegmentCodeBuf, 0)

    @property
    def doubledots(self):
        return self.__doubleDotOnFlag

    @doubledots.setter
    def doubledots(self, value):
        self.__doubleDotOnFlag = value
        if value:
            self.__currentSegmentCodeBuf[1] |= 0x80
        else:
            self.__currentSegmentCodeBuf[1] &= 0x7F
        self.setDots(self.__currentSegmentCodeBuf, 0)

    @property
    def time_hms(self):
        return self.__hms
    
    @time_hms.setter
    def time_hms(self, hms):
        self.__hms[:] = hms[:]
        self.__st1_s_stfsm_Refresh = time.monotonic()
        self.__st2_s_stfsm_Refresh = self.__st1_s_stfsm_Refresh-hms[2]

    def showTimeFSM_loop(self):
        nt = time.monotonic()
        if (nt-self.__st1_s_stfsm_Refresh) >= 0.5:
            self.__st1_s_stfsm_Refresh = nt
            self.doubledots = not self.doubledots
        if (nt-self.__st2_s_stfsm_Refresh) >= 60.0:
            self.__st2_s_stfsm_Refresh = nt
            self.__hms[1] += 1   # increment minute
            if self.__hms[1]>=60:
                self.__hms[1] = 0
                self.__hms[0] += 1
                if self.__hms[0] >= 24:
                    self.__hms[0] = 0
            self.showTime(self.__hms[:2], True)



