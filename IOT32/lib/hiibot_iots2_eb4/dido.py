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
import board
import digitalio
from debouncedButton import Debouncer

__version__ = "0.1.0-auto.0"
__repo__ = "https://github.com/HiiBot/Hiibot_CircuitPython_IoTs2.git"

class DIDO:

    def __init__(self):
        # 6x DI
        self._dilist = (board.IO7, board.IO8, board.IO9, board.IO10, board.IO11, board.IO12)
        self.din = []
        for di in self._dilist:
            __dik = digitalio.DigitalInOut(di)
            __dik.switch_to_input(pull=digitalio.Pull.UP)
            self.din.append( Debouncer(__dik, 0.01, True) )
        # 2x DO
        self._dolist = (board.IO40, board.IO41)
        self.dout = []
        for do in self._dolist:
            __dok = digitalio.DigitalInOut(do)
            __dok.switch_to_output(value=False)  # default state is LOW
            self.dout.append(__dok)

    def update_din(self):
        for di in self.din:
            di.read()

    ''' usage example:

        import time
        from hiibot_iots2_eb4.dido import DIDO
        dido = DIDO()
        while True:
            time.sleep(0.001)
            dido.update_din()
            time.sleep(0.001)
            if dido.din[1].wasPressed:
                print('1 closed')
                dido.dout[0].value = not dido.dout[0].value
            if dido.din[3].wasPressed:
                print('3 closed')
                dido.dout[1].value = not dido.dout[1].value
    '''