from kmk.keys import KC
from kmk.utils import Debug

debug = Debug(__name__)

class TapDetector:
    def __init__(self, keyboard, tap_timeout=200):
        self.keyboard = keyboard
        self.tap_timeout = tap_timeout
        self.tap_timer = None
        self.drag_timer = None
        self.dragging = False

    def touch_start(self):
        self.tap_timer = self.keyboard.set_timeout(self.tap_timeout, self._tap_timeout)
        if self.drag_timer:
            self.keyboard.cancel_timeout(self.drag_timer)
            self.drag_timer = None
            self.dragging = True
            self.keyboard.add_key(KC.MB_LMB)
            debug("Drag started")


    def touch_end(self):
        if self.dragging:
            self.dragging = False
            self.keyboard.remove_key(KC.MB_LMB)
            debug("Drag finished")

        if self.tap_timer:
            self.keyboard.cancel_timeout(self.tap_timer)
            self.tap_timer = None
            debug("might be a tap - better wait and see if it's a drag")
            self.drag_timer = self.keyboard.set_timeout(self.tap_timeout, self._drag_timeout)
        

    def is_tapping(self):
        return self.tap_timer is not None or self.drag_timer is not None

    def _tap_timeout(self):
        self.tap_timer = None
        debug("Tap timed out")

    def _drag_timeout(self):
        self.drag_timer = None
        self.keyboard.add_key(KC.MB_LMB)
        self.keyboard.set_timeout(2, lambda: self.keyboard.remove_key(KC.MB_LMB))
        debug("Tap drag timed out - registering a tap instead")


