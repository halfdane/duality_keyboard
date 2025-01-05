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
        self._mouse_up("starting over")
        if self.drag_timer:
            self.keyboard.cancel_timeout(self.drag_timer)
            self.drag_timer = None
            self.dragging = True
            self._mouse_down("drag start", 1)
        else:
            self.tap_timer = self.keyboard.set_timeout(self.tap_timeout, self._tap_timeout)
            

    def touch_end(self):
        if self.dragging:
            self.dragging = False
            # self._mouse_up("drag finished")
            self.drag_timer = self.keyboard.set_timeout(self.tap_timeout, self._drag_timeout)
        
        elif self.tap_timer:
            self.keyboard.cancel_timeout(self.tap_timer)
            self.tap_timer = None
            self._mouse_down("drag / tap")
            self.drag_timer = self.keyboard.set_timeout(self.tap_timeout, self._drag_timeout)
        

    def is_tapping(self):
        return self.tap_timer is not None or self.drag_timer is not None 

    def _tap_timeout(self):
        self.tap_timer = None
        debug("Tap timed out")

    def _drag_timeout(self):
        self.drag_timer = None
        self._mouse_up("drag was tap")

    def _mouse_up(self, message, timeout=0):
        def handler():
            self.keyboard.remove_key(KC.MB_LMB)
            debug(f"mouse up {message }")
        return  self.keyboard.set_timeout(timeout, handler)
  
    def _mouse_down(self, message, timeout=0):
        def handler():
            self.keyboard.add_key(KC.MB_LMB)
            debug(f"mouse down {message }")
        return  self.keyboard.set_timeout(timeout, handler)
  

