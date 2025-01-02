import board
from kb import KMKKeyboard
keyboard = KMKKeyboard()

from kmk.modules.split import Split, SplitType, SplitSide
split = Split(
    data_pin=keyboard.SPLIT_RX,
    data_pin2=keyboard.SPLIT_TX,
    uart_flip=True,
    use_pio=True)
keyboard.modules.append(split)

cirque = None
try:
    from cirque import Cirque   
    import busio
    cirque = Cirque(busio.I2C(keyboard.CIRQUE_SCL, keyboard.CIRQUE_SDA))
    keyboard.modules.append(cirque)

    from motions import MotionScanner
    scan = MotionScanner(keyboard,
                 invert_x=False, invert_y=True, swap_xy=True,
                 tap_timeout=150, fling_min_velocity=15,
                 scroll_zone_percentage=10, scroll_sensitivity=5)
    cirque.set_motionscanner(scan)
except RuntimeError:
    print("No cirque found - maybe wrong side") 

from miryoku import miryokufy
miryokufy(keyboard, scan)

# keyboard.debug_enabled = True
if __name__ == '__main__':
    keyboard.go()