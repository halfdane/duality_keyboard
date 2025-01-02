import busio
import digitalio
from adafruit_bus_device.i2c_device import I2CDevice
from kmk.modules import Module
from kmk.utils import Debug
from kmk.keys import AX, KC

import sys
from digitalio import DigitalInOut
from circuitpython_cirque_pinnacle import (
    PinnacleTouchI2C,
    AbsoluteReport,
    RelativeReport,
    PINNACLE_ABSOLUTE,
    PINNACLE_RELATIVE
)

debug = Debug(__name__)

class Cirque(Module):
    '''Module handles usage of cirque'''

    CIRQUE_PINNACLE_X_LOWER=296 # min "reachable" X value
    CIRQUE_PINNACLE_X_UPPER=1755 # max "reachable" X value
    CIRQUE_PINNACLE_Y_LOWER=194 # min "reachable" Y value
    CIRQUE_PINNACLE_Y_UPPER=1360 # max "reachable" Y value
    CIRQUE_PINNACLE_X_RANGE=(CIRQUE_PINNACLE_X_UPPER - CIRQUE_PINNACLE_X_LOWER)
    CIRQUE_PINNACLE_Y_RANGE=(CIRQUE_PINNACLE_Y_UPPER - CIRQUE_PINNACLE_Y_LOWER)

    def __init__(self, i2c):
        debug(f"Cirque Pinnacle relative mode on {sys.platform.lower()}\n")
        while not i2c.try_lock():
            pass
        debug( "addresses found:" + str([hex(device_address) for device_address in i2c.scan()]) )
        i2c.unlock()
        self._i2c_bus = i2c

        trackpad = PinnacleTouchI2C(i2c)
        trackpad.set_adc_gain(0)
        trackpad.data_mode = PINNACLE_ABSOLUTE 
        # an object to hold the data reported by the Pinnacle
        self.data = AbsoluteReport()

        self.trackpad = trackpad
        self.scale_data = 1024

        self.motionScanner = None
    
    def set_motionscanner(self, scanner):
        self.motionScanner = scanner

    def before_matrix_scan(self, keyboard):
        '''
        Return value will be injected as an extra matrix update
        '''
        if self.trackpad.available():  # is there new data?
            self.trackpad.read(self.data)
            self.touchDown   = (self.data.z != 0)

            (xTemp, yTemp) = self.ClipCoordinates(self.data)

            # scale coordinates to (xResolution, yResolution) range
            xValue = (xTemp * self.scale_data / self.CIRQUE_PINNACLE_X_RANGE)
            yValue = (yTemp * self.scale_data / self.CIRQUE_PINNACLE_Y_RANGE)

            if self.motionScanner:
                 self.motionScanner.scan(xValue, yValue, self.touchDown)



    def ClipCoordinates(self, data):
        x = data.x
        y = data.y
        if (x < self.CIRQUE_PINNACLE_X_LOWER):
            x = self.CIRQUE_PINNACLE_X_LOWER
        elif (x > self.CIRQUE_PINNACLE_X_UPPER):
            x = self.CIRQUE_PINNACLE_X_UPPER
        if (y < self.CIRQUE_PINNACLE_Y_LOWER):
            y = self.CIRQUE_PINNACLE_Y_LOWER
        elif (y > self.CIRQUE_PINNACLE_Y_UPPER):
            y = self.CIRQUE_PINNACLE_Y_UPPER
        
        # translate coordinates to (0, 0) reference by subtracting edge-offset
        x -= self.CIRQUE_PINNACLE_X_LOWER
        y -= self.CIRQUE_PINNACLE_Y_LOWER
        return (x, y)

    def during_bootup(self, keyboard):
        return

    def after_matrix_scan(self, keyboard):
        return

    def before_hid_send(self, keyboard):
        return

    def after_hid_send(self, keyboard):
        return

    def on_powersave_enable(self, keyboard):
        return

    def on_powersave_disable(self, keyboard):
        return


