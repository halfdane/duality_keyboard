from kmk.keys import KC
from kmk.utils import Debug

debug = Debug(__name__)

class TapDetector:
    def __init__(self, keyboard, tap_timeout):
        self.keyboard = keyboard
        self.tap_timeout = tap_timeout
        self.tap_timer = None
        self.tap_drag_timer = None
        self.dragging = False

    def touch_start(self):
        if self.tap_drag_timer is not None:
            debug("tap drag registered")
            self.keyboard.cancel_timeout(self.tap_drag_timer)
            self.tap_drag_timer = None
            self.dragging = True
            self.keyboard.add_key(KC.MB_LMB)
        if self.tap_timer is not None:
            self.keyboard.cancel_timeout(self.tap_timer)
        self.tap_timer = self.keyboard.set_timeout(self.tap_timeout, self._tap_timeout)

    def touch_end(self):
        if self.tap_timer:
            if self.tap_timer:
                self.keyboard.cancel_timeout(self.tap_timer)
            self.tap_timer = None
            if not self.dragging:
                debug("Tap registered")
                self.keyboard.tap_key(KC.MB_LMB)
                self.tap_drag_timer = self.keyboard.set_timeout(self.tap_timeout, self._tap_drag_timeout)
        if self.dragging:
            self.keyboard.remove_key(KC.MB_LMB)
            if self.tap_drag_timer:
                self.keyboard.cancel_timeout(self.tap_drag_timer)
            self.tap_drag_timer = None
            self.dragging = False

    def is_tapping(self):
        return self.tap_timer is not None or self.tap_drag_timer is not None

    def _tap_timeout(self):
        self.tap_timer = None
        debug("Tap timed out")

    def _tap_drag_timeout(self):
        self.tap_drag_timer = None
        debug("Tap drag timed out")