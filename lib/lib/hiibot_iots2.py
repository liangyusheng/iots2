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
`hiibot_iots2`
================================================================================

the board-supported-package for the HiiBot IoTs2 board, include
  (IoTs2 that a open source board from Hangzhou Leban (HiiBot) with ESP32-S2)
1) 1x programmable Button, IO21 be used, low level when button be pressed 
2) 1x programmable blue LED, IO37 be used, high level to on
3) 1x NeoPixel RGB pixels, IO16 be used
4) 1x 3-axis Accelerometer (LIS3DH), I2C bus (IO1-SCL, and IO2-SDA) be used
5) 1x QWiic/miniI2C port, I2C bus (IO1-SCL, and IO2-SDA) be used
6) 1x 1.14" IPS TFT LCD, SPI bus (IO33-MOSI, IO34-SCK, IO35-DC, IO36-NSS, IO38-BL) be used 

those interface are used as following:



* Author(s): HiiBot

Implementation Notes
--------------------

**Hardware:**
.. "* `HiiBot IoTs2 - a funny production with ESP32-S2`_"

**Software and Dependencies:**
* Adafruit CircuitPython firmware for the supported boards:
  https://github.com/adafruit/circuitpython/releases
 * Adafruit's Bus Device library: https://github.com/adafruit/Adafruit_CircuitPython_BusDevice
 * Adafruit's Register library: https://github.com/adafruit/Adafruit_CircuitPython_Register

"""
import time
import math
import board
import digitalio
#import pulseio  # for 6.x
import pwmio  # for 7.x
import busio
import neopixel
import displayio
import adafruit_lis3dh
from debouncedButton import Debouncer

__version__ = "0.1.0-auto.0"
__repo__ = "https://github.com/HiiBot/Hiibot_CircuitPython_IoTs2.git"

ACCELE_RANGE = (adafruit_lis3dh.RANGE_2_G, adafruit_lis3dh.RANGE_4_G,
                adafruit_lis3dh.RANGE_8_G, adafruit_lis3dh.RANGE_16_G)
ACCELE_DATARATE = (
                    adafruit_lis3dh.DATARATE_POWERDOWN, 
                    adafruit_lis3dh.DATARATE_1_HZ,
                    adafruit_lis3dh.DATARATE_10_HZ,
                    adafruit_lis3dh.DATARATE_25_HZ,
                    adafruit_lis3dh.DATARATE_50_HZ,
                    adafruit_lis3dh.DATARATE_100_HZ,
                    adafruit_lis3dh.DATARATE_200_HZ,
                    adafruit_lis3dh.DATARATE_400_HZ,
                    adafruit_lis3dh.DATARATE_LOWPOWER_1K6HZ,
                    adafruit_lis3dh.DATARATE_1344_HZ
                  )

class IoTs2:

    RED = (255, 0, 0)
    YELLOW = (255, 255, 0)
    ORANGE = (255, 150, 0)
    GREEN = (0, 255, 0)
    TEAL = (0, 255, 120)
    CYAN = (0, 255, 255)
    BLUE = (0, 0, 255)
    PURPLE = (180, 0, 255)
    MAGENTA = (255, 0, 150)
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    GREY = (200,200,200)
    GOLD = (255, 222, 30)
    PINK = (242, 90, 255)
    AQUA = (50, 255, 255)
    JADE = (0, 255, 40)
    AMBER = (255, 100, 0)
    VIOLET = (255, 0, 255)
    SKY = (0, 180, 255)

    def __init__(self):
        # 1x bleu LED 
        self._buleled = pwmio.PWMOut(board.BLUELED, duty_cycle=32768, frequency=1000)  # BLUELED
        self._buleledState = True
        self._buleledDutyBackup = 32768
        # 1x button
        self._button = digitalio.DigitalInOut(board.BUTTON)
        self._button.switch_to_input(pull=digitalio.Pull.UP)
        self._db_button = Debouncer(self._button, 0.01, True)

        # 1x Neopixels RGB pixels: IO16
        self._pixels = neopixel.NeoPixel( board.NEOPIXEL, 1, brightness=0.1, 
                            auto_write=True, pixel_order=neopixel.GRB )
        self._pixels.fill(0)
        self._pixels.show()

        # 1x QWiic/minii2c extened interface
        self._i2cbus = busio.I2C(board.SCL, board.SDA, frequency=100000)
        # 1x 3-axis Accelerometer (LIS3DH) with I2C interface
        self._lis3dh = adafruit_lis3dh.LIS3DH_I2C(self._i2cbus, address=0x19)

        # 1x 1.14" IPS TFT-LCD display (screen): 135*240 dots
        self._display = board.DISPLAY

    # 1x Blue LED
    @property
    def blueLED_bright(self):
        return self._buleled.duty_cycle/65535.0

    @blueLED_bright.setter
    def blueLED_bright(self, value):  # 0.0~1.0
        fv = value*65535.0
        iv = min(int(fv), 65535)
        self._buleled.duty_cycle = iv
        self._buleledDutyBackup = iv
        if value>0.01:
            self._buleledState = True
        else:
            self._buleledState = False

    def blueLED_toggle(self):
        if self._buleledState:
            self._buleledState = False
            self._buleled.duty_cycle = 0  # turn off
        else:
            self._buleledState = True
            self._buleled.duty_cycle = self._buleledDutyBackup  # turn on

    # 1x button
    @property
    def button_state(self):
        return not self._button.value

    def button_update(self):
        self._db_button.read()

    @property
    def button_wasPressed(self):
        return self._db_button.wasPressed

    @property
    def button_wasReleased(self):
        return self._db_button.wasReleased

    def button_pressedFor(self, t_s):
        return self._db_button.pressedFor(t_s)

    # 1x RGB LED 
    @property
    def pixels(self):
        return self._pixels

    # 
    @property
    def minii2cbus(self): 
        return self._i2cbus

    def connect_i2cDevice(self, address=None):
        if None==address:
            raise ValueError("None I2C address")
        return I2CDevice(self._i2cbus, address, probe=True)

    def writeValues_i2cDevive(self, regAddr, bufBytes, numBytes, i2cd=None):
        if None==i2cd:
            raise ValueError("a I2C device must be specified")
        if numBytes<1:
            raise ValueError("need some bytes data")
        if numBytes>128:
            numBytes = 128
        _obuf = bytearray(numBytes+1)
        _obuf[0] = regAddr&0xFF
        for i in range(numBytes):
            _obuf[i+1] = bufBytes[i]&0xFF
        with i2cd as i2c:
            i2c.write(_obuf, end=numBytes+1)

    def readValues_i2cDevive(self, regAddr, bufBytes, numBytes, i2cd=None):
        if None==i2cd:
            raise ValueError("a I2C device must be specified")
        if numBytes<1:
            raise ValueError("need some bytes data")
        if numBytes>128:
            numBytes = 128
        _obuf = bytearray(2)
        _obuf[0] = regAddr&0xFF
        with i2cd as i2c:
            i2c.write(_obuf, end=1)
            i2c.readinto(bufBytes, end=numBytes)

    # 1x 3-axis Accelerometer (LIS3DH) with I2C interface
    @property
    def Accele_Range(self):
        return ACCELE_RANGE[self._lis3dh.range]

    @Accele_Range.setter
    def Accele_Range(self, r):
        if r<0 or r>3:
            raise ValueError("Range Value can only take 0(2G), 1(4G), 2(8G), or 3(16G)!")
        else:
            self._lis3dh.range = ACCELE_RANGE[r]

    @property
    def Accele_DataRate(self):
        return ACCELE_DATARATE[self._lis3dh.data_rate]

    @Accele_DataRate.setter
    def Accele_DataRate(self, dr):
        if dr<0 or dr>9:
            raise ValueError("Data Rate Value can only take 0(PowerDown)~9(1.344KHz)!")
        else :
            self._lis3dh.data_rate = ACCELE_DATARATE[dr]

    @property
    def Accele_ms2(self): # (x,y,z) uint: m/s^2
        return self._lis3dh.acceleration

    @property
    def Accele_Gs(self): # (x,y,z) uint: Gs
        ax, ay, az = [ value / adafruit_lis3dh.STANDARD_GRAVITY for value in self._lis3dh.acceleration ]
        return (ax, ay,az)

    @property
    def angle_RollPitch(self):
        x, y, z = self.Accele_Gs
        pitch = int( 57.2958*( math.atan2(-x, -z) ) )
        roll  = int( 57.2958*( math.atan2( y, -z) ) )
        return (roll, pitch)

    def Shake(self, threshold=30, counts=10, delay=0.1):
        return self._lis3dh.shake(shake_threshold=threshold, avg_count=counts, total_delay=delay)

    # 1x 1.14" IPS TFT-LCD display (screen): 135*240 dots
    @property
    def screen(self):
        return self._display
