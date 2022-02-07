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
import struct
import board
import busio

class CAN1Message:
	def __init__(self, id, data, extended=False):
		self._data = None
		self.id = id
		self.data = data
		self.extended = extended

	@property
	def data(self):
		return self._data

	@data.setter
	def data(self, new_data):
		if (new_data is None) or (not (type(new_data) in [bytes, bytearray])):
			raise AttributeError( "non-RTR Message must have a `data` argument of type `bytes`" )
		if len(new_data) > 8:
			raise AttributeError( "Message object data must be of length 8 or less" )
		self._data = new_data

class CAN1IO:
	def __init__(self, bitrate=500000, debug_enable=False):
		self._en_debug = debug_enable
		self._bitrate = bitrate
		self._u1p = busio.UART(tx=board.IO18, rx=board.IO17, baudrate=512000, timeout=0.01)
		self._u1p.read( self._u1p.in_waiting )  # remove all
		if not self._cfg_canif(bitrate):
			raise ConnectionError("CAN-IF no ack! please check your hardware CAN unit")

	@property
	def enDebug(self):
		return self._en_debug
	
	@enDebug.setter
	def enDebug(self, value):
		self._en_debug = value

	def send(self, message_obj):
		if message_obj.extended:
			obytes = b'\xAA\x01\x00'      # frame head with extended ID (29-bit)
		else:
			obytes = b'\xAA\x00\x00'      # frame head with standard ID (11-bit)
		obytes += struct.pack('<B', len(message_obj.data))  # length of message_obj.data
		obytes += struct.pack('>I', message_obj.id)         # message_obj.id
		obytes += message_obj.data                          # message_obj.data
		for i in range(8-len(message_obj.data)):            # placeholder characters
			obytes += b'\x00'
		self._u1pw(obytes)
		# for debug
		if self._en_debug:
			if message_obj.extended:
				pstr = 'debug - send to [0x{:08X}]: '.format(message_obj.id)
			else:
				pstr = 'debug - send to [0x{:03X}]: '.format(message_obj.id)
			for i in range(len(message_obj.data)):
				pstr += '{:02X} '.format(message_obj.data[i])
			print(pstr)
		# 
	def show_send(self, message_obj):
		if message_obj.extended:
			pstr = 'send to [0x{:08X}]: '.format(message_obj.id)
		else:
			pstr = 'send to [0x{:03X}]: '.format(message_obj.id)
		for i in range(len(message_obj.data)):
			pstr += '{:02X} '.format(message_obj.data[i])
		print(pstr)

	def listening(self, timeout=0.1):
		_ibs = self._u1pr(timeout)
		if _ibs is None:
			return None
		if len(_ibs)<16:   # 16 bytes for each frame 
			return None
		else:
			msgs = []
			dl = len(_ibs)   # it may be multi-frame
			nf = int(dl/16)  # 16 bytes for each frame
			for i in range(nf):
				sp, ep = i*16, (i+1)*16
				_ibytes = _ibs[sp:ep]
				if _ibytes[0] == 0xAA and _ibytes[3]<=0x08:
					_flag = True if _ibytes[1]==0x01 else False   # extended ID ?
					_RTR  = True if _ibytes[2]==0x01 else False   # RTR frame ?
					_dn   = _ibytes[3]                            # length of Message Data
					_id   = struct.unpack('>I', _ibytes[4:8])[0]  # Message ID
					_data = _ibytes[8:(8+_dn)]                    # Message Data
					# for debug
					if self._en_debug:
						if _flag:
							pstr = 'debug - from [0x{:08X}]: '.format(_id)
						else:
							pstr = 'debug - from [0x{:03X}]: '.format(_id)
						for i in range(_dn):
							pstr += '{:02X} '.format(_data[i])
						print(pstr)
					#
					imsg = CAN1Message(id=_id, data=_data, extended=_flag)
					msgs.append(imsg)
				else:
					#print('a Error data frame')
					pass
			return msgs

	def show_listen(self, msgs):
		for msg in msgs:
			if msg.extended:
				ostr = 'from [0x{:08X}]: '.format(msg.id)  # extended ID
			else:
				ostr = 'from [0x{:03X}]: '.format(msg.id)  # standard ID
			for i in range(len(msg.data)):
				ostr += '{:02X} '.format(msg.data[i])
			print(ostr)

	def _u1pw(self, _obytes):
		if (_obytes is None) or (not (type(_obytes) in [bytes, bytearray])):
			raise AttributeError("_obytes must be type of `bytes`")
		sn = self._u1p.write(_obytes)
		if self._en_debug:
			print('debug - write: ', _obytes)
		return sn

	def _u1pw_cfg(self, cfg_bytes):
		if (cfg_bytes is None) or (not (type(cfg_bytes) in [bytes, bytearray])):
			raise AttributeError("cfg_bytes must be type of `bytes`")
		_obytes = cfg_bytes+b'\r\n'
		return self._u1pw(_obytes)

	def _u1pr(self, timeout=0.1):
		st = time.monotonic()
		while (time.monotonic()-st) <= timeout:
			if self._u1p.in_waiting>0:
				break
			time.sleep(0.002)  # 2ms * 51-bytes
		if self._u1p.in_waiting>0:
			wn = self._u1p.in_waiting
			trycnt = 5
			while trycnt>0:
				time.sleep(0.001)
				if self._u1p.in_waiting != wn:
					wn = self._u1p.in_waiting
				else:
					break
			_ibytes = self._u1p.read( self._u1p.in_waiting ) # read all
			# for debug
			if self._en_debug:
				pstr = 'debug - read: '
				for i in range(len(_ibytes)):
					pstr += '{:02X} '.format(_ibytes[i])
				print(pstr)
			#
			return _ibytes
		else:
			return None

	def _u1pr_cfg(self, timeout=0.1):
		_ibytes = self._u1pr(timeout)
		if _ibytes is None:
			return None
		else:
			return _ibytes

	def _cfg_canif(self, bitrate=None):
		if bitrate is None or bitrate<5 or bitrate>1000000:
			pass
		else:
			self._u1pw(b'+++')
			_ack = self._u1pr_cfg(timeout=2.0)
			if _ack is None:
				print('CAN-IF error: no ack [0]')
				self._cfg_exit()
				return False
			else:
				if _ack[0:2]==b'OK'[0:2]:
					# handshake ok
					br_str = b'AT+CAN_BAUD=' + bytes(str(bitrate), 'utf-8')
					self._u1pw_cfg(br_str)
					_ack = self._u1pr_cfg(timeout=2.0)
					self._cfg_exit()
					if _ack is None:
						return False
					else:
						if _ack[0:2]==b'OK'[0:2]:
							return True
						return False
				else:
					self._cfg_exit()
					return False

	def _cfg_exit(self):
		self._u1pw_cfg(b'ATO')
		self._u1pr_cfg(timeout=2.0)
