import supervisor
import board
import digitalio
import storage
import usb_cdc
import usb_hid
import microcontroller

from kmk.utils import Debug

debug = Debug(__name__)

def check(sense, source):
    if isinstance(sense, microcontroller.Pin):
        sense = digitalio.DigitalInOut(sense)
        sense.direction = digitalio.Direction.INPUT
        sense.pull = digitalio.Pull.UP

    if isinstance(source, microcontroller.Pin):
        source = digitalio.DigitalInOut(source)
        source.direction = digitalio.Direction.OUTPUT
        source.value = False

    result = sense.value
     
    sense.deinit()
    source.deinit()

    return not result

from kmk.hid_reports import pointer
devices = []
devices.append(usb_hid.Device.KEYBOARD)
devices.append(usb_hid.Device.MOUSE) 
usb_hid.enable(devices, 0)

# Hide storage on boot unless a thumb key is held during boot.
if check(board.GP7, board.GP9) or check(board.GP7, board.GP10):
    debug('keep everything enabled')
else:
    debug('disable usb etc')
    # usb_cdc.enable(console=False)
    storage.disable_usb_drive()


