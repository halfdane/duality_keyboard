from kmk.keys import KC
from kmk.utils import Debug

debug = Debug(__name__)

class TapDetector:
    def __init__(self, keyboard, tap_timeout=200):
        self.keyboard = keyboard
        self.tap_timeout = tap_timeout
        self.tap_timer = None

    def touch_start(self):
        self.tap_timer = self.keyboard.set_timeout(self.tap_timeout, self._tap_timeout)

    def touch_end(self):
        if self.tap_timer:
            self.keyboard.cancel_timeout(self.tap_timer)
            self.tap_timer = None
            self.keyboard.tap_key(KC.MB_LMB)

    def is_tapping(self):
        return self.tap_timer is not None

    def _tap_timeout(self):
        self.tap_timer = None

