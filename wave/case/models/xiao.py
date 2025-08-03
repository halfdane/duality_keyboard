from build123d import *


class SeeedXiaoBLE:

    def __init__(self, position=(0, 0, 0), rotation=0):
        self.position = position
        self.rotation = rotation


    def build(self):
        xiao = Pos(6.11, -12.28, 0.25) * Rot(90, 90, 0) * \
            import_step('assets/XIAO-nRF52840 v15.step')

        return xiao
