import board

from kmk.kmk_keyboard import KMKKeyboard as _KMKKeyboard
from kmk.scanners import DiodeOrientation


class KMKKeyboard(_KMKKeyboard):
    col_pins = (
        board.GP2, board.GP3, board.GP4, board.GP5, board.GP6, board.GP7
    )
    row_pins = (
        board.GP8, board.GP9, board.GP10
    )
    diode_orientation = DiodeOrientation.COL2ROW

# pin 0(white)/1(yellow)
    SPLIT_TX=board.TX 
    SPLIT_RX=board.RX

    CIRQUE_SCL=board.GP13
    CIRQUE_SDA=board.GP12

    coord_mapping = [
      0,  1,  2,  3,  4,           22, 21, 20, 19, 18,
      6,  7,  8,  9,  10,          28, 27, 26, 25, 24,
      12, 13, 14, 15, 16,          34, 33, 32, 31, 30,
                      17, 11,  29, 35 
    ]





