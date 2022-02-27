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
`iots2 extend board -- can2uart`
================================================================================

the board-supported-package for the CAN-2xUART to support HiiBot IoTs2 module, include
1) 1x CAN2.0B communication interface, IO3(CANTx) and IO4(CANRx) were used (canio.CAN)
2) 2x UART-3.3V communication interface, [IO43(U0TxD), IO44(U0RxD)], [IO18(U1TxD), IO17(U1RxD)] were used (busio.UART)
3) 3x LEDs to indicate status, IO7(RunLED), IO8(U0LED), IO9(U1LED) were used (LOW is on)
4) 2x Digital In channel, IO11(DI0), IO12(DI1) were used
5) 2x Digital Out channel, IO41(DO0), IO42(DO1) were used 
6) 1x NeoPixel RGB pixels, IO6 be used

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
import neopixel
import canio
import busio

__version__ = "0.1.0-auto.0"
__repo__ = "https://github.com/HiiBot/Hiibot_CircuitPython_IoTs2.git"

class C2UM:

    def __init__(self, can_baudrate=250_00, canid = 0x02,
                        match_id=0x0, match_mask=0x0, 
                       uart_baudrate=115_200, uart_rbufsize=128,
                       pixels_nums=7, 
                       en_debug=False):
        # CAN2.0B interface
        self._can = canio.CAN(
                    rx=board.IO4, tx=board.IO3,          # two Pins(rx, tx)
                    baudrate=can_baudrate, 
                    auto_restart=True)
        self._listener = self._can.listen(
                    matches=[canio.Match(match_id, match_mask)], 
                    timeout=0.1)
        self._canid = (canid<<6)&0x7A0                   # 5-bit Device ID + 6-bit Message ID
        # UART_0 interface
        self._u0art = busio.UART(
                    tx=board.IO43, rx=board.IO44,        # two Pins(tx, rx)
                    baudrate=uart_baudrate,              # baudrate: 9600 is default
                    timeout=0.01,                        # waiting time(s) for read(nBytes), and readinto(buf, nBytes)
                    receiver_buffer_size=uart_rbufsize)  # size of buffer
        self._u0art.reset_input_buffer()
        self._u0art_rbuf = bytearray(uart_rbufsize+1)
        self._u0art_rbuf_len = 0
        # UART_1 interface
        self._u1art = busio.UART(
                    tx=board.IO18, rx=board.IO17,        # two Pins(tx, rx)
                    baudrate=uart_baudrate,              # baudrate: 9600 is default
                    timeout=0.01,                        # waiting time(s) for read(nBytes), and readinto(buf, nBytes)
                    receiver_buffer_size=uart_rbufsize)  # size of buffer
        self._u1art.reset_input_buffer()
        self._u1art_rbuf = bytearray(uart_rbufsize+1)
        self._u1art_rbuf_len = 0
        # 3x LEDs to indicate our state: running state, UART_0 and UART_1
        self._runled = digitalio.DigitalInOut(board.IO7)
        self._runled.switch_to_output(value=True)        # turn off
        self._u0led = digitalio.DigitalInOut(board.IO9)
        self._u0led.switch_to_output(value=True)         # turn off
        self._u1led = digitalio.DigitalInOut(board.IO8)
        self._u1led.switch_to_output(value=True)         # turn off
        # 2x DI
        self._di0 = digitalio.DigitalInOut(board.IO11)
        self._di0.switch_to_input(pull=digitalio.Pull.UP)
        self._di1 = digitalio.DigitalInOut(board.IO12)
        self._di1.switch_to_input(pull=digitalio.Pull.UP)
        # 2x DO
        self._do0 = digitalio.DigitalInOut(board.IO41)
        self._do0.switch_to_output(value=False)          # turn off
        self._do1 = digitalio.DigitalInOut(board.IO40)
        self._do1.switch_to_output(value=False)          # turn off
        # pixels
        self._pixels = neopixel.NeoPixel( 
                    board.IO6, pixels_nums,              # pin, number of pixels
                    brightness=0.5,                      # the default brightness
                    auto_write=False, 
                    pixel_order=neopixel.GRB )
        self._pixels.fill(0)
        self._pixels.show()
        self._en_debug = en_debug

    # CAN2.0 interface 
    @property
    def canif(self): 
        # get CAN state property : 
        #  st = c2um.canif.state
        return self._can

    @property
    def canif_state(self):
        """ to get the state of CAN-Bus:
            canio.BusState.ERROR_ACTIVE   # normal (active) state
            canio.BusState.ERROR_WARNING  # normal (active) state, but a moderate number of errors
            canio.BusState.ERROR_PASSIVE  # receive only, but cannot transmit messages
            canio.BusState.BUS_OFF        # neither send or receive message

        this example to get the state of CAN

        To use with the IoTs2 and C2UM:
        
        .. code-block:: python
            
            import time
            from hiibot_iots2_can2uart import C2UM
            c2um = C2UM()
            old_bus_state = None
            while True:
                now_bus_state = c2um.canif_state
                if  now_bus_state != old_bus_state:
                    print(f"CAN-Bus state changed to {now_bus_state}")
                    old_bus_state = now_bus_state
        """
        return self._can.state
    
    # send a message through CAN2.0B
    def canif_send(self, msg_id=None, msg_data=None):
        """ to send a message through CAN-Bus
        
        this example to send a message through CAN
        
        To use with the IoTs2 and C2UM:
        
        .. code-block:: python
            
            import time
            from hiibot_iots2_can2uart import C2UM
            from hiibot_iots2 import IoTs2
            iots2 = IoTs2()
            c2um = C2UM()
            while True:
                iots2.button_update()
                if iots2.button_wasPressed:
                    c2um.canif_send(msg_id, msg_data)
                time.sleep(0.1)
        """
        if self._can.state == canio.BusState.ERROR_PASSIVE  or \
           self._can.state == canio.BusState.BUS_OFF:
            print("CAN-Bus Error! state = {}".format(self._can.state))
            return False
        if msg_id is None  or  msg_data is None:
            return False
        else:
            msg_id &= 0x03F  # 6-bit Message ID only!
            theid = self._canid + msg_id
            self._can.send(canio.Message(id=theid, data=msg_data))
            if self._en_debug:
                print("Debug info: Send [ID=0x{:03X}] data: {}".format(theid, msg_data))
            return True

    # receive a message through CAN2.0B
    def canif_receive(self):
        """ to receive a message through CAN-Bus
        
        this example to receive a message through CAN
        
        To use with the IoTs2 and C2UM:
        
        .. code-block:: python
            
            from hiibot_iots2_can2uart import C2UM
            c2um = C2UM()
            while True:
                rec = c2um.canif_receive()
                if rec is None:
                    pass
                else:
                    flag, msg_id, msg_data = rec[0], rec[1], rec[2]
                    if flag==True:
                        print('This is my message')
                    print("ID=0x{:03X}, Data={}".format(msg_id, msg_data))
        """
        if self._can.state == canio.BusState.BUS_OFF:
            print("CAN-Bus Error! state = {}".format(self._can.state))
            return None
        themsg = self._listener.receive()
        if themsg is None:
            return None       # no message
        else:
            if themsg.extended == True:
                return None   # 11-bit ID be used in our system
            if self._en_debug:
                print("Debug info: Receive [ID=0x{:03X}] data: {}".format(themsg.id, themsg.data))
            sender_id    = (themsg.id&0x7A0)>>6
            msg_id     = themsg.id&0x03F
            msg_data   = themsg.data
            return (sender_id, msg_id, msg_data)

    # UART_0 interface
    @property
    def u0art(self):
        return self._u0art

    # send a data frame (bytearray) through UART_0
    def u0art_send(self, bytes, nBytes):
        """ to send a message through UART_0
        
        this example to send a message through UART_0
        
        To use with the IoTs2 and C2UM:
        
        .. code-block:: python
            
            import time
            from hiibot_iots2_can2uart import C2UM
            from hiibot_iots2 import IoTs2
            iots2 = IoTs2()
            c2um = C2UM()
            while True:
                iots2.button_update()
                if iots2.button_wasPressed:
                    c2um.u0art_send(bytes, nBytes)
                time.sleep(0.1)
        """
        if not isinstance(bytes, bytearray):
            print("Error Parameters! 'bytes' must be a bytearray")
            return False
        if nBytes < 1:
            print('Error Parameters! data number must be larger 0')
        self._u0art.write(bytes, nBytes)
        if self._en_debug:
            print("Debug info: Send {} bytes data: {}".format(nBytes, bytes))
        return True

    # receive a data frame (bytearray) through UART_0
    def u0art_receive(self):
        """ to receive a message through UART_0
        
        this example to receive a message through UART_0
        
        To use with the IoTs2 and C2UM:
        
        .. code-block:: python
            
            from hiibot_iots2_can2uart import C2UM
            c2um = C2UM()
            while True:
                rec = c2um.u0art_receive()
                if rec is None:
                    pass
                else:
                    _len, _data = rec[0], rec[1]
                    print("receive {} bytes data {}".format(_len, _data))
        """
        if self._u0art.in_waiting<1:
            return None
        else:
            try_times = 0
            now_ibs = self._u0art.in_waiting
            while True: 
                # baudrate=115200, 11520bytes/second, 11.52bytes/ms, 
                time.sleep(0.02)   # wait more bytes data into UART buffer
                if self._u0art.in_waiting==now_ibs:
                    break
                else:
                    now_ibs = self._u0art.in_waiting
                try_times += 1
                if try_times > 4:  # These gushing floods of data must be Error!
                    self._u0art.reset_input_buffer()
                    return None
            now_ibs = self._u0art.in_waiting  # the (byte-)number of received data
            ibs = self._u0art.read(now_ibs)   # the received data
            if self._en_debug:
                print("Debug info: Receive {} bytes data: {}".format(len(ibs), ibs))
            return (now_ibs, ibs)

    # UART_1 interface
    @property
    def u1art(self):
        return self._u1art

    # send a data frame (bytearray) through UART_1
    def u1art_send(self, bytes, nBytes):
        """ to send a message through UART_1
        
        this example to send a message through UART_1
        
        To use with the IoTs2 and C2UM:
        
        .. code-block:: python
            
            import time
            from hiibot_iots2_can2uart import C2UM
            from hiibot_iots2 import IoTs2
            iots2 = IoTs2()
            c2um = C2UM()
            while True:
                iots2.button_update()
                if iots2.button_wasPressed:
                    c2um.u1art_send(bytes, nBytes)
                time.sleep(0.1)
        """
        if not isinstance(bytes, bytearray):
            print("Error Parameters! 'bytes' must be a bytearray")
            return False
        if nBytes < 1:
            print('Error Parameters! data number must be larger 0')
        self._u1art.write(bytes, nBytes)
        if self._en_debug:
            print("Debug info: Send {} bytes data: {}".format(nBytes, bytes))
        return True

    # receive a data frame (bytearray) through UART_1
    def u1art_receive(self):
        """ to receive a message through UART_1
        
        this example to receive a message through UART_1
        
        To use with the IoTs2 and C2UM:
        
        .. code-block:: python
            
            from hiibot_iots2_can2uart import C2UM
            c2um = C2UM()
            while True:
                rec = c2um.u1art_receive()
                if rec is None:
                    pass
                else:
                    _len, _data = rec[0], rec[1]
                    print("receive {} bytes data {}".format(_len, _data))
        """
        if self._u1art.in_waiting<1:
            return None
        else:
            try_times = 0
            now_ibs = self._u1art.in_waiting
            while True: 
                # baudrate=115200, 11520bytes/second, 11.52bytes/ms, 
                time.sleep(0.02)   # wait more bytes data into UART buffer
                if self._u1art.in_waiting==now_ibs:
                    break
                else:
                    now_ibs = self._u1art.in_waiting
                try_times += 1
                if try_times > 4:  # These gushing floods of data must be Error!
                    self._u1art.reset_input_buffer()
                    return None
            now_ibs = self._u1art.in_waiting  # the (byte-)number of received data
            ibs = self._u1art.read(now_ibs)   # the received data
            if self._en_debug:
                print("Debug info: Receive {} bytes data: {}".format(len(ibs), ibs))
            return (now_ibs, ibs)

    @property
    def runled(self):
        """ get RunLED state property
        
        this example to get the state of RunLED
        
        To use with the IoTs2 and C2UM:
        
        .. code-block:: python
            
            import time
            from hiibot_iots2_can2uart import C2UM
            c2um = C2UM()
            while True:
                print('RunLED {}'.format(c2um.runled))
                time.sleep(1.5)
        """
        return self._runled.value

    @runled.setter
    def runled(self, value):
        """ to control RunLED
        
        this example to control RunLED
        
        To use with the IoTs2 and C2UM:
        
        .. code-block:: python
            
            import time
            from hiibot_iots2_can2uart import C2UM
            from hiibot_iots2 import IoTs2
            iots2 = IoTs2()
            c2um = C2UM()
            while True:
                iots2.button_update()
                if iots2.button_wasPressed:
                    c2um.runled = not c2um.runled
                time.sleep(0.1)
        """
        self._runled.value = value

    @property
    def u0led(self):
        return self._u0led.value

    @u0led.setter
    def u0led(self, value):
        self._u0led.value = value
    
    @property
    def u1led(self):
        return self._u1led.value

    @u1led.setter
    def u1led(self, value):
        self._u1led.value = value
    
    @property
    def di0(self):
        return self._di0.value
    
    @property
    def di1(self):
        return self._di1.value

    @property
    def do0(self):
        return self._do0.value

    @do0.setter
    def do0(self, value):
        self._do0.value = value
    
    @property
    def do1(self):
        return self._do1.value

    @do1.setter
    def do1(self, value):
        self._do1.value = value
    
    @property
    def pixels(self):
        """ to control the pixels[0..n] connected with C2UM
        
        this example to control the color of pixels[0..n] connected with C2UM 
        
        To use with the IoTs2:
        
        .. code-block:: python
            
            import time
            from hiibot_iots2_can2uart import C2UM
            c2um = C2UM()
            colors = [(255,0,0), (255,127,0), (127,127,0), (0,255,0), (0,255,127), (0,0,255), (255,0,255)]
            for i in range( min( c2um.pixels.n, len(colors) ) ):
                c2um.pixels[i] = colors[i]
            c2um.pixels.show()
            while True:
                tc = colors[0]
                index = 1
                for i in range( min( c2um.pixels.n, len(colors) ) -1 ):
                    colors[i] = colors[i+1]
                    c2um.pixels[i] = colors[i]
                    index = i
                colors[index+1] = tc
                c2um.pixels[index+1] = tc
                c2um.pixels.show()
                time.sleep(0.5)
        """
        return self._pixels
    
    @property
    def pixels_brightness(self):
        return self._pixels.brightness

    @pixels_brightness.setter
    def pixels_brightness(self, value):
        """ to control the brightness of pixels[0..n] connected with C2UM
        
        this example to control the brightness of pixels[0..n] connected with C2UM 
        
        To use with the IoTs2:
        
        .. code-block:: python
            
            import time
            from hiibot_iots2_can2uart import C2UM
            c2um = C2UM()
            b_list = [0.0, 0.2, 0.4, 0.6, 0.8, 1.0, 1.0, 0.8, 0.6, 0.4, 0.2, 0.0]
            index = 0
            while True:
                c2um.pixels_brightness = b_list[index%len(b_list)]
                index += 1
                time.sleep(0.5)
        """
        self._pixels.brightness = value
        self._pixels.show()
    