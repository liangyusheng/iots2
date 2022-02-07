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
import canio
import struct

class CAN0IO:

    BusState = ('BUS_OFF', 'BUS_ACTIVE', 'BUS_PASSIVE', 'BUS_WARNING')

    def __init__(self, can_baudrate=500_000, match_id=0x0, match_mask=0x0, en_debug=False):
        # CAN2.0B interface
        self._can = canio.CAN(
                    rx=board.IO4, tx=board.IO3,          # two Pins(rx, tx)
                    baudrate=can_baudrate, 
                    auto_restart=True)
        self._listener = self._can.listen(
                    matches=[canio.Match(match_id, match_mask)], 
                    timeout=0.1)
        self._en_debug = en_debug
        self._bus_state_old = 0
        # COBID: [10~7: Function Code] [6~0: NodeID]
        self.Nodes_ID_Used = {}   # 0x01~0x7F (1~127)
        self.Nodes_ID_State = {}  # 0x01~0x7F (1~127)
        self.Nodes_ID_HBt = {}    # 0x01~0x7F (1~127)
        self.timeInterval = time.monotonic()

    @property
    def enDebug(self):
        return self._en_debug

    @enDebug.setter
    def enDebug(self, value):
        self._en_debug = value

    def _show_msg(self, message=None, recvFlag=True):
        if recvFlag:
            __ostr = 'from ID [0x{:03X}]: '.format(message.id)
        else:
            __ostr = 'to ID [0x{:03X}]: '.format(message.id)
        #__obslist  = struct.unpack('<BHBl', message.data)
        for i in range(len(message.data)):
            __ostr += '{:02X} '.format(message.data[i])
        print(__ostr)

    def recv(self):
        __rmsg = self._listener.receive()
        if __rmsg is None:
            __nt = time.monotonic()
            for __id in self.Nodes_ID_HBt:
                if (__nt - self.Nodes_ID_HBt[__id])>5.1:
                    print('NodeID [{:03d}] offline!'.format(__id))
                    del self.Nodes_ID_HBt[__id]
                    del self.Nodes_ID_State[__id]
            return None
        if self._en_debug:
            self._show_msg(__rmsg, True)
        # update on-line Node ID and its state while received Heartbeat package
        if ( (__rmsg.id&0x700)==0x700 ) and (len(__rmsg.data)==1):
            __nodeid    = (__rmsg.id&0x7F)
            __nodestate = __rmsg.data[0]
            if __nodeid in self.Nodes_ID_State:
                pass
            else:
                self.Nodes_ID_State[__nodeid] = __nodestate
                self.Nodes_ID_Used[__nodeid] = time.monotonic()  # time stamp
                #if self._en_debug:
                print('NodeID [{:03d}] online! its state: 0x{:02X}'.format(__nodeid, __nodestate))
            self.Nodes_ID_HBt[__nodeid] = time.monotonic()
            return None
        # SDO package ()
        else:
            return __rmsg

    def send(self, msg=None):
        if isinstance(msg, canio.Message):
            self._can.send(msg)
            if self._en_debug:
                self._show_msg(msg, False)
        pass

    @property
    def busstate(self):
        __bs  = self._can.state
        if   __bs == canio.BusState.BUS_OFF:
            __bsc = 0
        elif __bs == canio.BusState.ERROR_ACTIVE:
            __bsc = 1
        elif __bs == canio.BusState.ERROR_PASSIVE:
            __bsc = 2
        elif __bs == canio.BusState.ERROR_WARNING:
            __bsc = 3
        else:
            __bsc = 0
        return __bsc
    
    def loop(self):
        __bsc = self.busstate 
        if __bsc != self._bus_state_old:
            print(f"CAN Bus state changed to {self.BusState[__bsc]}")
            self._bus_state_old = __bsc

        __rmsg = self.recv()
        if __rmsg is None:
            pass
        else:
            self._show_msg(__rmsg, True)
