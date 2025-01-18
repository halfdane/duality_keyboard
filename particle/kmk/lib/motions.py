import math
from kmk.keys import AX
from kmk.utils import Debug
from circularScroller import CircularScroller
from tapDetector import TapDetector
from debouncer import Debouncer
from fling_handler import FlingHandler
from automove import Automover

debug = Debug(__name__)

class MotionScanner:
    def __init__(self, keyboard,
                 invert_x=False, invert_y=False, swap_xy=False, tap_timeout=100, fling_decay=0.95, fling_min_velocity=10,
                 scroll_sensitivity=4, scroll_zone_percentage=20, invert_scroll=False, touchpad_size=1024,
                 debounce_samples=10):
        """Initializes the motion scanner."""

        # Configuration values
        self.keyboard = keyboard
        self.invert_x = invert_x
        self.invert_y = invert_y
        self.swap_xy = swap_xy
        self.touchpad_size = touchpad_size

        # Coordinate variables
        self.current_x = 0
        self.current_y = 0

        # Callbacks and state
        self.touch_start_callback = lambda *args: None
        self.touch_end_callback = lambda *args: None
        self.is_touching = False

        # Initialize scroller
        self.scroller = CircularScroller(keyboard, touchpad_size, scroll_sensitivity, scroll_zone_percentage, invert_scroll=invert_scroll)
        self.tap_detector = TapDetector(keyboard, tap_timeout)
        self.debouncer = Debouncer(debounce_samples)
        self.fling_handler = FlingHandler(keyboard, fling_decay, fling_min_velocity)
        # self.automover = Automover(keyboard, touchpad_size, scroll_zone_percentage)


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
        self.touch_start_callback()
        
        if not self.scroller.start_scroll(x, y):
            self.tap_detector.touch_start()
        else:
            self.tap_detector.tap_timer = None

        self.fling_handler.stop_fling()

    def _handle_touch_end(self, x, y):
        """Handles the end of a touch event."""
        self.is_touching = False
        self.touch_end_callback()
        debug("Touch ended")

        self.tap_detector.touch_end()
        self.scroller.end_scroll()
        self.fling_handler.fling(x, y)


      # Mouse movement and scroll handling
    def _handle_mouse_movement(self, x, y):
        """Handles mouse movement or scrolling."""
        if self.tap_detector.is_tapping():
            return

        if self.scroller.scroll_active:
            self.scroller.scroll(x, y)
        # elif self.automover.automove_active(x, y):
        #     self.automover.automove()
        else:
            relative_x = int(x - self.current_x)
            relative_y = int(y - self.current_y)
                
            AX.X.move(self.keyboard, relative_x)
            AX.Y.move(self.keyboard, relative_y)
            self.current_x = x
            self.current_y = y
            self.fling_handler.move(relative_x, relative_y)
            # self.automover.move(relative_x, relative_y)

    def scan(self, x, y, is_touching):
        """Handles touch events and mouse movement."""
        if self.swap_xy:
            x, y = y, x
        
        if self.invert_x:
            x = self.touchpad_size - x
        if self.invert_y:
            y = self.touchpad_size - y

        if is_touching and not self.is_touching:
            self.debouncer.start_debounce(x, y)
            self._handle_touch_start(x, y)
        elif not is_touching and self.is_touching:
            self._handle_touch_end(x, y)
        elif is_touching and self.is_touching:
            x, y = self.debouncer.debounce(x, y)
            self._handle_mouse_movement(x, y)