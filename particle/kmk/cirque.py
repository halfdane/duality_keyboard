import busio
import board
import digitalio
from adafruit_bus_device.i2c_device import I2CDevice
from kmk.modules import Module
from kmk.utils import Debug
from kmk.keys import AX, KC

import time
import board
import sys
from digitalio import DigitalInOut
from circuitpython_cirque_pinnacle import (
    PinnacleTouchI2C,
    AbsoluteReport,
    RelativeReport,
    PINNACLE_ABSOLUTE,
    PINNACLE_RELATIVE
)

from kmk.scheduler import cancel_task, create_task

debug = Debug(__name__)

class Cirque(Module):
    '''Module handles usage of cirque'''

    CIRQUE_PINNACLE_X_LOWER=127 # min "reachable" X value
    CIRQUE_PINNACLE_X_UPPER=1919 # max "reachable" X value
    CIRQUE_PINNACLE_Y_LOWER=63 # min "reachable" Y value
    CIRQUE_PINNACLE_Y_UPPER=1471 # max "reachable" Y value
    CIRQUE_PINNACLE_X_RANGE=(CIRQUE_PINNACLE_X_UPPER - CIRQUE_PINNACLE_X_LOWER)
    CIRQUE_PINNACLE_Y_RANGE=(CIRQUE_PINNACLE_Y_UPPER - CIRQUE_PINNACLE_Y_LOWER)

    MIN_VELOCITY=5
    AUTOMOVE_DECAY=0.95

    def __init__(
        self,
        i2c
    ):
        debug(f"Cirque Pinnacle relative mode on {sys.platform.lower()}\n")
        while not i2c.try_lock():
            pass
        debug( "addresses found:" + str([hex(device_address) for device_address in i2c.scan()]) )
        i2c.unlock()
        self._i2c_bus = i2c

        self.x0 = -10
        self.y0 = -10

        trackpad = PinnacleTouchI2C(i2c)
        trackpad.set_adc_gain(0)
        trackpad.data_mode = PINNACLE_ABSOLUTE 
        # an object to hold the data reported by the Pinnacle
        self.data = AbsoluteReport()

        self.trackpad = trackpad
        self.scale_data = 1024

        self._fling_task = None
        self.touch_start = None
        self.touch_end = None

    def on_touch_end(self, touch_end):
        self.touch_end = touch_end
    
    def on_touch_start(self, touch_start):
        self.touch_start = touch_start

    def during_bootup(self, keyboard):
        self._fling = self.create_fling_motion(keyboard)

    def before_matrix_scan(self, keyboard):
        '''
        Return value will be injected as an extra matrix update
        '''
        if self.trackpad.available():  # is there new data?
            self.trackpad.read(self.data)
            self.touchDown   = (self.data.x != 0 or self.data.y !=0)

            (xTemp, yTemp) = self.ClipCoordinates(self.data);

            # translate coordinates to (0, 0) reference by subtracting edge-offset
            xTemp -= self.CIRQUE_PINNACLE_X_LOWER
            yTemp -= self.CIRQUE_PINNACLE_Y_LOWER

            # scale coordinates to (xResolution, yResolution) range
            xValue = (xTemp * self.scale_data / self.CIRQUE_PINNACLE_X_RANGE)
            yValue = (yTemp * self.scale_data / self.CIRQUE_PINNACLE_Y_RANGE)

            self.dx = int(xValue - self.x0) if self.x0 > 0 else 0
            self.dy = int(yValue - self.y0) if self.y0 > 0 else 0
        
            if self.touchDown:
                AX.X.move(keyboard, self.dy)
                AX.Y.move(keyboard, -self.dx)

                if self.x0 == -10 and self.touch_start is not None:
                    self.touch_start()


                self.x0 = xValue
                self.y0 = yValue

                # when moving, remember the vector
                self.last_dx = self.dx
                self.last_dy = self.dy

            else:
                if self.x0 != -10 and self.touch_end is not None:
                    self.touch_end()
                
                self.x0 = -10
                self.y0 = -10
                

                # when not moving, start the automatic movement
                # self._fling()

    def create_fling_motion(self, keyboard):
        def handle_task():
            if self._fling_task is not None:
                cancel_task(self._fling_task)
            if (self.last_dx < -self.MIN_VELOCITY or self.last_dx > self.MIN_VELOCITY) or (self.last_dy < -self.MIN_VELOCITY or self.last_dy > self.MIN_VELOCITY):
                self._fling_task = create_task(self._fling, after_ms=100)
                
                self.last_dx *= self.AUTOMOVE_DECAY
                self.last_dy *= self.AUTOMOVE_DECAY
                AX.X.move(keyboard, int(self.last_dy))
                AX.Y.move(keyboard, int(-self.last_dx))
        
        return handle_task



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
        return (x, y)


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


