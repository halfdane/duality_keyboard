Cirquitpython-based firmware for duality/particle

Using kmk, it's supporting the integrated touchpad (with automagic layer switching) as well as most of miryoku.

There are some notable deviations from miryoku, however: 
- Thumb key combos are global, not dependent on the current layer
- Tap both left thumb keys: ESCAPE
- Hold both left thumb keys: MOUSE-Layer
- Tap both right thumb keys: DELETE
- Hold both right thumb keys: FN-Layer

There's no need to build it, just copy it over after installing cirquitpython on the device.
Or run `make` to copy over the necessary files from kmk as well.

## Development
Usually circuitpython will offer the device for mounting as a USB mass storage - this is disabled in the boot.py.
To mount the board, keep a thumb key pressed on the side with the USB cable while the board boots (plug out, then in).
