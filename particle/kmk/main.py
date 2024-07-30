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
    import board
    from kmk.modules.mouse_keys import MouseKeys
    keyboard.modules.append(MouseKeys())
    cirque = Cirque(busio.I2C(keyboard.CIRQUE_SCL, keyboard.CIRQUE_SDA))
    keyboard.modules.append(cirque)
except RuntimeError:
    print("No cirque found - maybe wrong side")

from kmk.keys import KC
from kmk.modules.combos import Combos, Chord, Sequence
from kmk.modules.layers import Layers;

from kmk.modules.mouse_keys import MouseKeys; keyboard.modules.append(MouseKeys())
from kmk.modules.power import Power; keyboard.modules.append(Power())
from kmk.modules.tapdance import TapDance; keyboard.modules.append(TapDance())
from kmk.extensions.media_keys import MediaKeys; keyboard.extensions.append(MediaKeys())
from kmk.modules.capsword import CapsWord; keyboard.modules.append(CapsWord())
from kmk.modules.holdtap import HoldTap; keyboard.modules.append(HoldTap())


# R_ALT=KC.HT(KC.R, KC.LALT, prefer_hold=False, tap_interrupted=True, tap_time=150)

# keyboard.keymap = [ [
#    KC.TD(KC.CW, KC.CAPS, tap_time=200), KC.F, R_ALT,  
# ] ]

from miryoku import miryokufy
miryokufy(keyboard, cirque)

# keyboard.debug_enabled = True
if __name__ == '__main__':
    keyboard.go()