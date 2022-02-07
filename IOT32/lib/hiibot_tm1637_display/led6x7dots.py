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
`hiibot_led6x7dots`
================================================================================

the board-supported-package for the 6x7 Dots dispaly with TM1637

those interface are used as following:



* Author(s): HiiBot

Implementation Notes
--------------------

**Hardware:**
.. "* `6x7 dots display with the driver ic TM1637 "

**Software and Dependencies:**
* Adafruit CircuitPython firmware for the supported boards:
  https://github.com/adafruit/circuitpython/releases

"""
import time
from .tm1637 import TM1637
from .fonts6x7dots import Front6x7DotsData

class LED6x7Dots(TM1637):
    
    fixedPattern = (
        (0b00011100, 0b00111110, 0b01111100, 0b01111100, 0b00111110, 0b00011100), # 0, big heart 
        (0b00000000, 0b00011100, 0b00111000, 0b00111000, 0b00011100, 0b00000000), # 1, small heart
        (0b00000000, 0b00000010, 0b00000001, 0b01011001, 0b00000110, 0b00000000), # 2, question mark
        (0b00000110, 0b00010110, 0b00100000, 0b00100000, 0b00010110, 0b00000110), # 3, happy face
        (0b00000110, 0b00100110, 0b00010000, 0b00010000, 0b00100110, 0b00000110), # 4, sad face
        (0b00000100, 0b01111110, 0b01111111, 0b01111110, 0b00000100, 0b00000000), # 5, up arrow
        (0b00010000, 0b00111111, 0b01111111, 0b00111111, 0b00010000, 0b00000000), # 6, down arrow
        (0b00001000, 0b00011100, 0b00111110, 0b00011100, 0b00011100, 0b00011100), # 7, left arrow
        (0b00011100, 0b00011100, 0b00011100, 0b00111110, 0b00011100, 0b00001000), # 8, right arrow
        (0x00000000, 0b00000000, 0b00011100, 0b00011100, 0b00000000, 0b00000000), # 9, small square
        (0x00000000, 0b00111110, 0b00111110, 0b00111110, 0b00111110, 0b00000000), # 10, big square
        (0b00000100, 0b00000110, 0b01111111, 0b01000110, 0b00000100, 0b00000000), # 11, umbrella
        (0b00000100, 0b00001110, 0b00011111, 0b00000100, 0b00001110, 0b00000000), # 12, batfish
        (0b00000000, 0b00010000, 0b00011110, 0b01111111, 0b00011110, 0b00010000)  # 13, sword
    )
    fillPattern  = bytes(b'\x7f\x7f\x7f\x7f\x7f\x7f')
    clearPattern = bytes(b'\x00\x00\x00\x00\x00\x00')
    
    def __init__(self, clk, dio, brightness=7, intervalRefresh=1.0):
        super().__init__(clk, dio, brightness)
        self.__currentContentBuf = bytearray(b'\x00\x00\x00\x00\x00\x00')
        #self.__showTextBuf  = bytearray(32)
        #self.__validLenText = 0
        #self.__nowTextPosi = 0
        #self.__drfsmEnable = False
        self.__onetimes = True
        self.__intervalRefresh_s = intervalRefresh
        self.__st_s_Refresh = time.monotonic()
        self.__rollOver = True
        self.__slideShowBuf = bytearray(33*6)
        self.__slideValidLenBuf = 0
        self.__slideNowPosi = 0
        self.__slideDrfsmEnable = False
        self.__priorKey = 0
        self.__oneshotKey = True
    
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

    def fillDots(self):
        for i in range(6):
            self.__currentContentBuf[i] = self.fillPattern[i]
        self.setDots(self.__currentContentBuf, 0)
        self.__drfsmEnable = False
        self.__slideDrfsmEnable = False
    
    def clearDots(self):
        for i in range(6):
            self.__currentContentBuf[i] = self.clearPattern[i]
        self.setDots(self.__currentContentBuf, 0)
        self.__drfsmEnable = False
        self.__slideDrfsmEnable = False
    
    def showFixedPattern(self, n):
        self.__drfsmEnable = False
        self.__slideDrfsmEnable = False
        if n<0:
            n=0
        if n >= len(self.fixedPattern):
            n=len(self.fixedPattern)-1
        for k in range(6):
            self.__currentContentBuf[k] = self.fixedPattern[n][k]
        self.setDots(self.__currentContentBuf, 0)
    
    def drawDot(self, x, y, on):
        if 0<=x<=5 and 0<=y<=6:
            self.__drfsmEnable = False
            self.__slideDrfsmEnable = False
            dotByte = self.__currentContentBuf[x]
            if on:
                dotByte |= self.BITMASK[y]
            else:
                dotByte &= ~self.BITMASK[y]
            self.__currentContentBuf[x] = dotByte
            self.setDots(self.__currentContentBuf, 0)

    def toggleDot(self, x, y):
        if 0<=x<=5 and 0<=y<=6:
            self.__drfsmEnable = False
            self.__slideDrfsmEnable = False
            dotByte = self.__currentContentBuf[x]
            if (self.BITMASK[y] & dotByte) == self.BITMASK[y]:
                dotByte &= ~self.BITMASK[y]
            else:
                dotByte |= self.BITMASK[y]
            self.__currentContentBuf[x] = dotByte
            self.setDots(self.__currentContentBuf, 0)
    '''
    def showText(self, text, waitdone=False):
        if 0<len(text)<33:
            self.__drfsmEnable = False
            self.__slideDrfsmEnable = False
            self.__validLenText = len(text)
            # text[i] -> self.__showTextBuf
            for i in range(self.__validLenText):
                td = ord(text[i])-32
                if td>94:
                    td = 0
                self.__showTextBuf[i] = td
            # show the first char
            for k in range(6):
                self.__currentContentBuf[k] = Front6x7DotsData[self.__showTextBuf[0]][k]
            self.setDots(self.__currentContentBuf, 0)
            # start Display Refresh Finite State Machine (self.drfsm_loop())
            if self.__validLenText > 1:
                self.__rollOver = False
                self.__nowTextPosi = 1
                self.__drfsmEnable = True
                self.__st_s_Refresh = time.monotonic()
                if waitdone:
                    while True:
                        self.drfsm_loop()
                        time.sleep(0.001)
                        if self.__rollOver:
                            break
            else:
                self.__rollOver = True
                self.__drfsmEnable = False

    def drfsm_loop(self):
        if self.__drfsmEnable:
            nt =  time.monotonic()
            if (nt-self.__st_s_Refresh) >= self.__intervalRefresh_s:
                self.__st_s_Refresh = nt
                for k in range(6):
                    self.__currentContentBuf[k] = Front6x7DotsData[self.__showTextBuf[self.__nowTextPosi]][k]
                self.setDots(self.__currentContentBuf, 0)
                self.__nowTextPosi += 1
                if self.__nowTextPosi >= self.__validLenText:
                    self.__nowTextPosi = 0
                    self.__rollOver = True
                    if self.__onetimes:
                        self.__drfsmEnable = False
    '''
    def showText(self, text, waitdone=False):
        if 0<len(text)<33:
            self.__drfsmEnable = False
            self.__slideDrfsmEnable = False
            self.__slideValidLenBuf = len(text)*6
            # text[i] -> self.__showTextBuf[i]
            for i in range( len(text) ):
                td = ord(text[i])-32
                if td>94:
                    td = 0
                # td -> self.__slideShowBuf[i*6 .. (i*6+5)]
                for j in range(6):
                    self.__slideShowBuf[i*6+j] = Front6x7DotsData[td][j]
            # append one blank frame into our buf
            if (len(text)>1) and (not self.__onetimes):
                for j in range(6):
                    self.__slideShowBuf[self.__slideValidLenBuf+j] = 0x00
                self.__slideValidLenBuf += 6
            # show the first char
            for k in range(6):
                self.__currentContentBuf[k] = self.__slideShowBuf[k]
            self.setDots(self.__currentContentBuf, 0)
            # start Slide Display Refresh Finite State Machine (self.sdrfsm_loop())
            if len(text) > 1:
                self.__rollOver = False
                self.__slideNowPosi = 6
                self.__slideDrfsmEnable = True
                self.__st_s_Refresh = time.monotonic()
                if waitdone:
                    while True:
                        self.drfsm_loop()
                        time.sleep(0.001)
                        if self.__rollOver:
                            break
            else:
                self.__rollOver = True
                self.__slideDrfsmEnable = False

    def drfsm_loop(self):
        if self.__slideDrfsmEnable:
            nt = time.monotonic()
            if (nt-self.__st_s_Refresh) >= (self.__intervalRefresh_s/5):
                self.__st_s_Refresh = nt
                for k in range(5):
                    self.__currentContentBuf[k] = self.__currentContentBuf[k+1]
                self.__currentContentBuf[5] = self.__slideShowBuf[self.__slideNowPosi]
                self.setDots(self.__currentContentBuf, 0)
                self.__slideNowPosi += 1
                if self.__slideNowPosi >= self.__slideValidLenBuf:
                    self.__slideNowPosi = 0
                    self.__rollOver = True
                    if self.__onetimes:
                        self.__slideDrfsmEnable = False

    def showNumber(self, num, waitdone=False):
        if not isinstance(num, int) and not isinstance(num, float):
            raise ValueError("Support only integer or floating point number!")
        else:
            st = '{}'.format(num)
            if len(st)>32:
                s = st[:32]
            else:
                s = st
            self.showText( s, waitdone )

    @property
    def buttonPosition(self):
        self.setDots(self.__currentContentBuf, 0)
        ks = self.scanKeys()
        if not self.__oneshotKey:
            return ks
        elif ks != self.__priorKey:
            self.__priorKey = ks
            return ks
        else:
            return None

    @property
    def oneShotKey(self):
        return self.__oneshotKey
    
    @oneShotKey.setter
    def oneShotKey(self, value):
        self.__oneshotKey = value


