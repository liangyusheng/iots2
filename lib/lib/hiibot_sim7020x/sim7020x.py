# The MIT License (MIT)
#
# Copyright Wang Zhongfei (ZJUT-ME)
# Copyright (c) 2020 
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
`sim7020x`
================================================================================

CircuitPython library for the SIM7020X NB-IoT module

* Author(s): Wang Zhongfei

Implementation Notes
--------------------

**Software and Dependencies:**

* Adafruit CircuitPython firmware for the supported boards:
  https://github.com/adafruit/circuitpython/releases

"""
import time
import board
import busio
import digitalio
from micropython import const
from simpleio import map_range

__version__ = "1.0.0"

SIM7020X_DEFAULT_TIMEOUT_MS = 500  # TODO: Check this against arduino...
SIM7020X_NETLED_MODE1 = (b'200', b'800')   # while SIM7020X does not register to the network
SIM7020X_NETLED_MODE2 = (b'300', b'2700')  # while SIM7020X has already registered to the network
SIM7020X_NETLED_MODE3 = (b'100', b'400')   # while SIM7020X is in the state of PPP communication

# pylint: disable=too-many-instance-attributes, too-many-public-methods
class SIM7020X:
    """CircuitPython SIM7020X module interface.
    :param  txd: SIM7020X UART data out pin (board.Tx).
    :param  rxd: SIM7020X UART data out pin (board.RX).
    :param   ri: Optional SIM7020X Ring Interrupt (RI) pin (board.P6).
    :param int bps: baudrate of UART
    :param bool debug: Enable debugging output. """

    # pylint: disable=too-many-arguments
    def __init__(self, txd=board.TX, rxd=board.RX, reset=None, bps=115200, debug=False):
        self._buf = b""   # shared buffer
        self._numLines = 0
        self._listLines = [] # reply lines: message lines
        self._numItems = 0
        self._listItems = [] # reply items: param items with ','
        self._debug = debug
        self._uart = busio.UART(txd, rxd, baudrate=bps, receiver_buffer_size=256)
        self._reset = None
        if reset is not None:
            self._reset = digitalio.DigitalInOut(reset)
            self._reset.switch_to_output(value=1)
        print("Step 1: Find SIM7020X ..")
        if self._find_sim7020x():
            print("\tFund SIM7020X!")
            self.sim7020x_netled()  # set NetLED blink period
            print("Step 2: Check SIM-Card .. ")
            if self.simCard_status :
                if self.simCard_PDN_status :
                    if self.netRegister_status :
                        print("\tGood SIM-Card!")
                        _rssi = self.rssi
                        print("RSSI(-110 ~ -54): {}".format(_rssi))
                        if _rssi<-85:
                            print("Radio Signal Strength Indicator too low")
                        _myip = self.myip
                        print("IP address (and subnet): {}".format(_myip))
                    else:
                        raise RuntimeError("Unregistered SIM-Card")
                else:
                    raise RuntimeError("SIM-Card is deactived")
            else:
                raise RuntimeError("Bad SIM-Card status")
        else:
            raise RuntimeError("Unable to find SIM7020X. Please check connections.")

    # pylint: disable=too-many-branches, too-many-statements
    def _find_sim7020x(self):
        # Find SIM7020X module.
        if self._debug:
            print('Finding SIM7020X ..')
        tryagain_cnt = 10  # 5 seconds, 10 times
        while tryagain_cnt > 0:
            if self._send_check_ack( b'AT\r\n', SIM7020X_DEFAULT_TIMEOUT_MS):
                if self._debug:
                    print('Fund SIM7020X')
                return True
            time.sleep(0.5)
            tryagain_cnt -= 1
            if self._debug:
                print('Try {} times ..'. format(10-tryagain_cnt))
        return False
    
    def sim7020x_netled(self):
        self._send_check_ack(b'AT+SLEDS=1,' + SIM7020X_NETLED_MODE1[0] + b',' + SIM7020X_NETLED_MODE1[1] + b'\r\n')
        self._send_check_ack(b'AT+SLEDS=2,' + SIM7020X_NETLED_MODE2[0] + b',' + SIM7020X_NETLED_MODE2[1] + b'\r\n')
        self._send_check_ack(b'AT+SLEDS=3,' + SIM7020X_NETLED_MODE3[0] + b',' + SIM7020X_NETLED_MODE3[1] + b'\r\n')

    def sim7020x_reset(self):
        if self._reset is not None:
            self._reset.value = 0
            time.sleep(0.2)
            self._reset.value = 1
            time.sleep(1.5)

    @property
    def simCard_status(self):
        self._uart.reset_input_buffer()
        if self._debug:
            print("SIM-Card status")
        if self._send_check_ack(b'AT+CPIN?\r\n', SIM7020X_DEFAULT_TIMEOUT_MS):
            return True 
        return False

    @property
    def simCard_PDN_status(self):
        self._uart.reset_input_buffer()
        if self._debug:
            print("SIM-Card PDN status")
        if self._send_check_ack(b'AT+CGACT?\r\n', SIM7020X_DEFAULT_TIMEOUT_MS):
            if self._numLines == 3:
                _buffer = self._listLines[1][8:]
                _ni = self._resolve_item(_buffer, 44) # with divider: ','
                if _ni>=2:
                    if int(self._listItems[0]) == 1:  # '1': actived, '0': deactived
                        return True
        return False

    @property
    def simCard_iccid(self):
        # SIM Card's unique ICCID (Integrated Circuit Card Identifier).
        self._uart.reset_input_buffer()
        if self._debug:
            print("SIM-Card ICCID")
        if self._send_check_ack(b'AT+CCID\r\n', SIM7020X_DEFAULT_TIMEOUT_MS):
            _iccid = self._listLines[1]
            return _iccid.decode("utf-8")  # converte into String
        else:
            return 'ERROR'
    
    @property
    def sim7020x_iemi(self):
        # SIM7020X Module's IEMI (International Mobile Equipment Identity) number.
        self._uart.reset_input_buffer()
        if self._debug:
            print("SIM7020X IEMI")
        if self._send_check_ack(b'AT+CGSN\r\n', SIM7020X_DEFAULT_TIMEOUT_MS):
            _iemi = self._listLines[1]
            return _iemi.decode("utf-8")  # converte into String
        else:
            return 'ERROR'

    @property
    def netRegister_status(self):
        # The status of the cellular network.
        self._uart.reset_input_buffer()
        if self._debug:
            print("Network Register status")
        if self._send_check_ack(b'AT+CGREG?\r\n', SIM7020X_DEFAULT_TIMEOUT_MS):
            if self._numLines == 3:
                _buffer = self._listLines[1][8:]
                _ni = self._resolve_item(_buffer, 44) # with divider: ','
                if _ni>=2:
                    if int(self._listItems[1]) == 1:  # '1': registered, '0': unregistered
                        return True
        return False

    @property
    def rssi(self):
        # The received signal strength indicator for the cellular network that we are connected to.
        if self._debug:
            print("RSSI")
        _rssi_num = 0
        if self._send_check_ack(b'AT+CSQ\r\n', SIM7020X_DEFAULT_TIMEOUT_MS):
            if self._numLines == 3:
                _buffer = self._listLines[1][6:]
                _ni = self._resolve_item(_buffer, 44) # with divider: ','
                if _ni>=2:
                    _rssi_num = int(self._listItems[0])
        rssi = 0
        if _rssi_num == 0:
            rssi = -115
        elif _rssi_num == 1:
            rssi = -111
        elif _rssi_num == 31:
            rssi = -52
        if 2 <= _rssi_num <= 30:
            rssi = map_range(_rssi_num, 2, 30, -110, -54)
        return rssi

    def _local_ip(self): 
        self._uart.reset_input_buffer()
        # SIM7020X Module's local IP address, None if not set.
        if self._send_check_ack(b'AT+CGCONTRDP\r\n', SIM7020X_DEFAULT_TIMEOUT_MS):
            if self._numLines == 3:
                _buffer = self._listLines[1][12:]
                _ni = self._resolve_item(_buffer, 44) # with divider: ','
                if _ni>=4:
                    _l = len(self._listItems[3])
                    return self._listItems[3][1:_l-1]
        return b'0.0.0.0.0.0.0.0'

    @property
    def myip(self):  # pylint: disable=no-self-use, invalid-name
        # Converts a bytearray IP address to a dotted-quad string for printing
        _bip = self._local_ip()
        return  _bip.decode()

    @property
    def myip_list(self):  # pylint: disable=no-self-use, invalid-name
        # Converts a dotted-quad string to a bytearray IP address
        _bip = self._local_ip()
        _bip = _bip.decode()
        octets = [int(x) for x in _bip.split(".")]
        return bytes(octets)

    ### UART Reply/Response Helpers ###

    def _uart_write(self, buffer):
        """ UART ``write`` with optional debug that prints
        the buffer before sending.
        :param bytes  buffer: Buffer of bytes to send to the bus. """
        if self._debug:
            #print("\tUARTWRITE (debug) ::", buffer.decode())
            print("\tUARTWRITE (debug) ::", buffer)
        self._uart.write(buffer)

    # non-block style operation function (Write)
    def write_line(self, buffer):
        self._uart_write(buffer)

    # non-block style operation function (Read)
    def read_line(self): 
        _rl_nums = 0
        _rl_buf  = b''
        _preChar = b''
        time.sleep(0.001) # 1ms --> 11 bytes
        while self._uart.in_waiting:
            _inChar = self._uart.read(1)
            if _inChar == b'\r':      # ignore '\r'
                continue
            if _inChar == b'\n':
                if _rl_nums == 0:     # ignore first '\n' 
                    continue
                if _preChar == b'\n': # change '\n\n' into '\n'
                    continue
            _rl_buf += _inChar
            _preChar = _inChar
            _rl_nums += 1
            time.sleep(0.0002) # 0.2ms --> 2bytes 
        if self._debug:
            #print("\tUARTREAD (debug) ::", self._rl_buf.decode())
            print("\tUARTREAD (debug) ::", _rl_buf)
        return _rl_nums, _rl_buf

    # resolve received (multiline) package into list of line, divider is '\n'
    def resolve_line(self, buffersize=0, buffer=b''):
        _rl_numLines = 0
        _rl_listLines = []
        if buffersize==0 or buffer==b'':
            return _rl_numLines, _rl_listLines
        _s_idx = 0
        for i in range(buffersize):
            if buffer[i] == 10:  # '\n'
                _rl_numLines += 1
                _rl_listLines.append(buffer[_s_idx:i])
                _s_idx = i+1
        if self._debug:
            print('got {} lines :'.format(_rl_numLines))
            for i in range(_rl_numLines):
                print(_rl_listLines)
        return _rl_numLines, _rl_listLines

    # resolve a line into list of parameters/value, divider is ',' or other
    def resolve_item(self, buffersize=0, buffer=b'', divider=44):
        _ri_numItems = 0
        _ri_listItems = []
        if buffersize == 0 or buffer==b'':
            return _ri_numItems, _ri_listItems
        _s_idx = 0
        for i in range(buffersize):
            if buffer[i] == divider:
                if i == 0:
                    continue
                _ri_numItems += 1
                _ri_listItems.append(buffer[_s_idx:i])
                _s_idx = i+1
        # the last item, for example 'z' of "x,y,z"
        if buffer[_s_idx:] != b'':
            _ri_numItems += 1
            _ri_listItems.append(buffer[_s_idx:])
        if self._debug:
            print('Included {} items :'.format(_ri_numItems))
            for i in range(_ri_numItems):
                print(_ri_listItems)
        return _ri_numItems, _ri_listItems

    def _read_line(self, timeout=SIM7020X_DEFAULT_TIMEOUT_MS, multiline=False):
        """ Reads one or multiple lines into the buffer. Optionally prints the buffer after reading.
        :param int     timeout: Time to wait for UART serial to reply, in seconds.
        :param bool  multiline: Read multiple lines. """
        self._buf = b''
        _reply_idx = 0
        _preNewLine = 0
        while True:
            time.sleep(0.005) 
            _newLen = self._uart.in_waiting
            if _newLen == 0:
                timeout -= 5
                if timeout <= 0:
                    break
            elif _newLen != _preNewLine:
                _preNewLine = _newLen
            else :
                time.sleep(0.005)  # 5ms * 11bytes --> 55bytes
                _preChar = b''
                while self._uart.in_waiting:
                    inChar = self._uart.read(1)
                    if inChar == b'\r':       # ignore all '\r'
                        continue
                    if inChar == b'\n':
                        if _reply_idx == 0:   # ignore first '\n'
                            continue
                        if _preChar == b'\n': # change '\n\n' into '\n'
                            continue
                    self._buf += inChar
                    _preChar = inChar
                    _reply_idx += 1
        if self._debug:
            #print("\tUARTREAD (debug) ::", self._buf.decode())
            print("\tUARTREAD (debug) ::", self._buf)
        return _reply_idx, self._buf

    def _resolve_line(self, bufsize):  # resolve self._buf into some lines, return the number of lines
        self._numLines = 0
        self._listLines = []
        _s_idx = 0
        for i in range(bufsize):
            if self._buf[i] == 10:  # '\n'
                self._numLines += 1
                self._listLines.append(self._buf[_s_idx:i])
                _s_idx = i+1
        return self._numLines

    def _resolve_item(self, line_buf, divider=44):
        self._numItems = 0
        self._listItems = []
        _s_idx = 0
        _pre_char = b""
        for i in range( len(line_buf) ):
            if line_buf[i] == divider:  # 44 = ',', 34 = '"'
                if i == 0:
                    continue
                if _pre_char == divider:
                    continue
                self._numItems += 1
                self._listItems.append(line_buf[_s_idx:i])
                _s_idx = i+1
            _pre_char = line_buf[i]
        # the last item
        if self._numItems >= 1 and not line_buf[_s_idx:]==b'' :
            self._numItems += 1
            self._listItems.append(line_buf[_s_idx:])
        # for debug
        if self._debug:
            print('Included {} items :'.format(self._numItems))
            for i in range(self._numItems):
                print(self._listItems[i])
        return self._numItems

    def _ok_error_line(self, line_buf):  # parse the last line, return True(OK), or False(ERROR) 
        if  line_buf[0:2] == b'OK':
            return True
        else :
            return False

    # for testing, enable debug, send and read command line, then restore debug status
    def send_check_ack(self, send=None, timeout=SIM7020X_DEFAULT_TIMEOUT_MS, debug=False):
        _bak_debug_status = self._debug
        self._debug = debug
        _rb = self._send_check_ack(send, timeout)
        self._debug = _bak_debug_status
        return _rb

    def _send_check_ack(self, send=None, timeout=SIM7020X_DEFAULT_TIMEOUT_MS):
        if send == None:
            return 
        else:
            self._uart.reset_input_buffer()
            self._uart_write(send)
            _numBytes, _ = self._read_line(timeout=SIM7020X_DEFAULT_TIMEOUT_MS, multiline=True)
            if _numBytes == 0:
                # no ack (timeout)!
                if self._debug:
                    print('no ack, SIM7020X module error')
                return False
            else:
                self._numLines = self._resolve_line(_numBytes)
                if self._debug:
                    print('got {} lines :'.format(self._numLines))
                    for i in range(self._numLines):
                        print(self._listLines[i])
                if self._numLines >= 1:
                    if self._ok_error_line(self._listLines[self._numLines-1]):
                        return True
                else :
                    return False

