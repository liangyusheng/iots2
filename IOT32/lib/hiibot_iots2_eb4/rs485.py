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
import board
import digitalio
import busio

__version__ = "0.1.0-auto.0"
__repo__ = "https://github.com/HiiBot/Hiibot_CircuitPython_IoTs2.git"

class RS485:

    def __init__(self, uart_baudrate=115_200, uart_rbufsize=128,
                    STX=None, ETX=None, en_debug=False):
        # UART_0 interface
        self._u0art = busio.UART(
                    tx=board.IO43, rx=board.IO44,             # two Pins(tx, rx)
                    baudrate=uart_baudrate,                   # baudrate: 115,200 is default
                    timeout=0.01,                             # waiting time(s) for read(nBytes), and readinto(buf, nBytes)
                    receiver_buffer_size=uart_rbufsize)       # size of buffer
        self._u0art.reset_input_buffer()
        self.rxbuf = bytearray(uart_rbufsize+1)
        self.rxbuf_len = 0
        # RS485 Receive Enable Control
        self._enRecv = digitalio.DigitalInOut(board.IO0)
        self._enRecv.switch_to_output(value=True)       # enable receive
        # STX, and ETX
        self._stx = STX
        self._etx = ETX
        # 
        self._en_debug = en_debug

    # RS485 Receive Enable Control State
    @property
    def enRecv(self): 
        # get state property : 
        #  st = rs485.enRecv
        return self._enRecv.value

    @enRecv.setter
    def enRecv(self, value):
        # enable receive:
        # rs485.enRecv = 1
        # enable transmitt:
        # rs485.enRecv = 0
        self._enRecv.value = value

    @property
    def STX(self):
        return self._stx

    @STX.setter
    def STX(self, value):
        self._stx = value

    @property
    def ETX(self):
        return self._etx

    @ETX.setter
    def ETX(self, value):
        self._etx = value
    
    @property
    def in_waiting(self):
        return self._u0art.in_waiting
    
    # send a data frame (bytearray) through RS485
    def send(self, sbytes):
        """ to send a message through RS485
        
        this example to send a message through RS485
        
        To use with the IoTs2 and EB4:
        
        .. code-block:: python
            
            import time
            from hiibot_iots2_eb4.rs485 import RS485
            from hiibot_iots2 import IoTs2
            iots2 = IoTs2()
            rs485 = RS485()
            sbytes = b'hello\r\n'
            while True:
                iots2.button_update()
                if iots2.button_wasPressed:
                    rs485.send(sbytes)
                time.sleep(0.1)
        """
        if not (type(sbytes) in [bytes, bytearray]):
            print("Error Parameters! 'bytes' must be a bytearray")
            return False
        if len(sbytes) < 1:
            print('Error Parameters! data number must be larger 0')
        self._enRecv.value = 0  # enable transmit
        __st = time.monotonic()
        time.sleep(0.0002)
        __sn = self._u0art.write(sbytes)
        time.sleep(0.0008)
        __et =  (time.monotonic()-__st)*1000  # ms
        if self._en_debug:
            print("Debug info: Send {} bytes data: {}, Elapsed time: {}ms".format(len(sbytes), sbytes, __et))
        self._enRecv.value = 1  # enable receive
        return __sn

    # receive a data frame (bytearray) through RS485
    def recv(self):
        """ to receive a message through RS485
        
        this example to receive a message through RS485
        
        To use with the IoTs2 and EB4:
        
        .. code-block:: python
            
            from hiibot_iots2_eb4.rs485 import RS485
            rs485 = RS485()
            while True:
                rec = rs485.recv()
                if rec is None:
                    pass
                else:
                    print("receive {} bytes data: {}".format(len(rec), rec))
        """
        if self._u0art.in_waiting<1:
            return None
        else:
            __try_times = 0
            __now_ibs = self._u0art.in_waiting
            while True: 
                # baudrate=115200, 11520bytes/second, 11.52bytes/ms, 
                time.sleep(0.001)   # wait more bytes data into UART buffer
                if self._u0art.in_waiting==__now_ibs:
                    break
                else:
                    __now_ibs = self._u0art.in_waiting
                __try_times += 1
                if __try_times > 10:  # These gushing floods of data must be Error!
                    self._u0art.reset_input_buffer()
                    return None
            __now_ibs = self._u0art.in_waiting    # the (byte-)number of received data
            __ibs = self._u0art.read(__now_ibs)   # the received data
            if self._en_debug:
                print("Debug info: Receive {} bytes data: {}".format(len(__ibs), __ibs))
            return __ibs



