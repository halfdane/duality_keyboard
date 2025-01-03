import math
from kmk.keys import AX
from kmk.utils import Debug

debug = Debug(__name__)

def normalize_angle(angle):
    """Normalizes an angle to be between -pi and pi."""
    return (angle + math.pi) % (2 * math.pi) - math.pi

class CircularScroller:
    """Handles circular scrolling logic, including fling."""
    def __init__(self, keyboard, 
            touchpad_size, scroll_sensitivity, scroll_zone_percentage, invert_scroll=False,
            fling_decay=0.97, fling_min_velocity=1):
        self.keyboard = keyboard
        self.touchpad_size = touchpad_size
        self.scroll_zone_percentage = scroll_zone_percentage
        self.scroll_start_angle = None
        self.scroll_active = False
        self.fling_decay = fling_decay
        self.fling_min_velocity = fling_min_velocity
        self.fling_scroll_amount = 0
        self.fling_angle = 0
        self.fling_timer = None
        self.invert_scroll = invert_scroll

        # Pre-calculate center, radius, and scroll_scale
        self.center_x = self.touchpad_size / 2
        self.center_y = self.touchpad_size / 2
        self.radius = self.touchpad_size / 2
        self.scroll_scale = scroll_sensitivity * 5.72958

    def start_scroll(self, x, y):
        """Starts a scroll action if in the rightmost scroll zone (vertical strip)."""
        scroll_zone_width = self.touchpad_size * (self.scroll_zone_percentage / 100)
        scroll_zone_left = self.touchpad_size - scroll_zone_width

        if scroll_zone_left <= x <= self.touchpad_size:
            self.scroll_active = True
            self.scroll_start_angle = math.atan2(y - self.center_y, x - self.center_x)
            debug("Scroll started")
            return True
        else:
            self.scroll_active = False
            return False

    def scroll(self, x, y):
        """Performs a scroll step if scrolling is active."""
        if not self.scroll_active:
            return

        if self.scroll_start_angle is None:
            return

        current_angle = math.atan2(y - self.center_y, x - self.center_x)
        angle_delta = normalize_angle(current_angle - self.scroll_start_angle)

        scroll_amount = int(angle_delta * self.scroll_scale)

        if self.invert_scroll:
            scroll_amount *= -1

        if scroll_amount != 0:
            AX.W.move(self.keyboard, scroll_amount)
            self.scroll_start_angle = current_angle
            self.fling_scroll_amount = scroll_amount
            self.fling_angle = angle_delta #Set fling angle
            debug(f"Scrolling by angle delta: {angle_delta}, amount: {scroll_amount}")
 
    def end_scroll(self):
        """Ends the scroll action and potentially initiates a fling."""
        if self.scroll_active:
            debug("Scroll ended")
            self.scroll_active = False

            if abs(self.fling_scroll_amount) > self.fling_min_velocity: #Check scroll amount against min velocity
                self.fling_timer = self.keyboard.set_timeout(10, self._handle_fling)
                debug("Scroll fling started")
        self.scroll_start_angle = None

    def _handle_fling(self):
        """Handles the fling motion."""
        scroll = int(self.fling_scroll_amount)
        self.fling_scroll_amount *=  self.fling_decay
        if abs(scroll) > 0:
            AX.W.move(self.keyboard, int(scroll))
            debug(f"Scroll flinging by: {scroll}")
            self.fling_timer = self.keyboard.set_timeout(10, self._handle_fling)
        else:
            self.fling_timer = None
            debug("Scroll fling ended")
