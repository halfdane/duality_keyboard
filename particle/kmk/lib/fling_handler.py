import math
from kmk.keys import AX


from kmk.utils import Debug
debug = Debug(__name__)

class FlingHandler:
    def __init__(self, keyboard, decay=0.95, min_velocity=10):
        self.keyboard = keyboard
        self.decay = decay
        self.min_velocity = min_velocity
        self.fling_x = 0
        self.fling_y = 0
        self.fling_timer = None
    
    def move(self, x, y):
        self.fling_x = x
        self.fling_y = y

    def fling(self, x, y):
        fling_magnitude = math.sqrt(self.fling_x**2 + self.fling_y**2)
        if fling_magnitude > self.min_velocity:
            self.current_x = x
            self.current_y = y
            self.fling_timer = self.keyboard.set_timeout(10, self._handle_fling)
            debug("Fling started")

    def _handle_fling(self):
        """Handles the fling motion."""
        relative_x = int(self.fling_x)
        relative_y = int(self.fling_y)

        self.fling_x *= self.decay
        self.fling_y *= self.decay

        if abs(relative_x) > 0 or abs(relative_y) > 0:
            AX.X.move(self.keyboard, relative_x)
            AX.Y.move(self.keyboard, relative_y)
            debug(f"Flinging by: ({relative_x}, {relative_y})")
            self.fling_timer = self.keyboard.set_timeout(10, self._handle_fling)
        else:
            self.fling_timer = None
            debug("Fling ended")

    def stop_fling(self):
        if self.fling_timer:
            self.keyboard.cancel_timeout(self.fling_timer)
            self.fling_timer = None
        self.fling_x = 0
        self.fling_y = 0
