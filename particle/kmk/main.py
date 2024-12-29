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
    cirque = Cirque(busio.I2C(keyboard.CIRQUE_SCL, keyboard.CIRQUE_SDA))
    keyboard.modules.append(cirque)
except RuntimeError:
    print("No cirque found - maybe wrong side")

from miryoku import miryokufy
miryokufy(keyboard, cirque)

# keyboard.debug_enabled = True
if __name__ == '__main__':
    keyboard.go()