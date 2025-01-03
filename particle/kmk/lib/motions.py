import math
from kmk.keys import AX, KC
from kmk.utils import Debug
from circularScroller import CircularScroller
from tapDetector import TapDetector

debug = Debug(__name__)

class MotionScanner:
    def __init__(self, keyboard,
                 invert_x=False, invert_y=False, swap_xy=False, tap_timeout=200, fling_decay=0.95, fling_min_velocity=10,
                 scroll_sensitivity=4, scroll_zone_percentage=20, touchpad_size=1024):
        """Initializes the motion scanner."""

        # Configuration values
        self.keyboard = keyboard
        self.invert_x = invert_x
        self.invert_y = invert_y
        self.swap_xy = swap_xy
        self.fling_decay = fling_decay
        self.fling_min_velocity = fling_min_velocity

        # Coordinate variables
        self.current_x = 0
        self.current_y = 0
        self.last_x = None
        self.last_y = None
        self.fling_x = 0
        self.fling_y = 0

        # Callbacks and state
        self.touch_start_callback = None
        self.touch_end_callback = None
        self.is_touching = False
        self.fling_timer = None

        # Initialize scroller
        self.scroller = CircularScroller(keyboard, touchpad_size, scroll_sensitivity, scroll_zone_percentage)
        self.tap_detector = TapDetector(keyboard, tap_timeout)


    def set_touch_start_callback(self, callback):
        self.touch_start_callback = callback

    def set_touch_end_callback(self, callback):
        self.touch_end_callback = callback

    # Touch handling functions
    def _handle_touch_start(self, x, y):
        """Handles the start of a touch event."""
        self.is_touching = True
        self.current_x = x
        self.current_y = y
        self.last_x = x
        self.last_y = y

        if self.touch_start_callback:
            self.touch_start_callback()
        
        if not self.scroller.start_scroll(x, y):
            self.tap_detector.touch_start()
        else:
            self.tap_detector.tap_timer = None

        if self.fling_timer:
            self.keyboard.cancel_timeout(self.fling_timer)
            self.fling_timer = None
            debug("Fling aborted due to new touch")

    def _handle_touch_end(self, x, y):
        """Handles the end of a touch event."""
        self.is_touching = False

        if self.touch_end_callback:
            self.touch_end_callback()
        debug("Touch ended")

        self.tap_detector.touch_end()
        if self.scroller.scroll_active: #Only check for scrolling if it was started
            debug("touch is ending while scrolling")
            self.scroller.end_scroll()
        else: #If no tap and no scroll, handle the fling
            fling_magnitude = math.sqrt(self.fling_x**2 + self.fling_y**2)
            if fling_magnitude > self.fling_min_velocity:
                self.current_x = x
                self.current_y = y
                self.fling_timer = self.keyboard.set_timeout(10, self._handle_fling)
                debug("Fling started")

        self.last_x = None
        self.last_y = None


      # Mouse movement and scroll handling
    def _handle_mouse_movement(self, x, y):
        """Handles mouse movement or scrolling."""
        if self.tap_detector.is_tapping():
            return

        if self.scroller.scroll_active:
            self.scroller.scroll(x, y)
        else:
            relative_x = int(x - self.current_x)
            relative_y = int(y - self.current_y)

            if self.invert_x:
                relative_x *= -1
            if self.invert_y:
                relative_y *= -1
                
            AX.X.move(self.keyboard, relative_x)
            AX.Y.move(self.keyboard, relative_y)
            self.current_x = x
            self.current_y = y
            self.fling_x = relative_x
            self.fling_y = relative_y
        self.last_x = x
        self.last_y = y

    # Fling handling
    def _handle_fling(self):
        """Handles the fling motion."""
        relative_x = int(self.fling_x)
        relative_y = int(self.fling_y)

        self.fling_x *= self.fling_decay
        self.fling_y *= self.fling_decay

        if abs(relative_x) > 0 or abs(relative_y) > 0:
            AX.X.move(self.keyboard, relative_x)
            AX.Y.move(self.keyboard, relative_y)
            debug(f"Flinging by: ({relative_x}, {relative_y})")
            self.fling_timer = self.keyboard.set_timeout(10, self._handle_fling)
        else:
            self.fling_timer = None
            debug("Fling ended")

    def scan(self, x, y, is_touching):
        """Handles touch events and mouse movement."""
        if self.swap_xy:
            x, y = y, x

        if is_touching and not self.is_touching:
            self._handle_touch_start(x, y)
        elif not is_touching and self.is_touching:
            self._handle_touch_end(x, y)
        elif is_touching and self.is_touching:
            self._handle_mouse_movement(x, y)