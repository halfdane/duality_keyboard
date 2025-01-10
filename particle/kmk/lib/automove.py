import math
from kmk.keys import AX


from kmk.utils import Debug
debug = Debug(__name__)

class Automover:
    def __init__(self, keyboard, touchpad_size, outer_percentage):
        self.keyboard = keyboard
        self.outer_percentage = outer_percentage
        self.radius = touchpad_size / 2 

        self.dx = 0
        self.dy = 0
    
    def move(self, dx, dy):
        self.dx = dx
        self.dy = dy

    def automove_active(self, x, y):
        distance_from_center = math.sqrt((x - self.radius) ** 2 + (y - self.radius) ** 2)
        inner_radius = self.radius * (1 - (self.outer_percentage / 100))
        if distance_from_center > inner_radius:
            debug("nearing the outer reaches!")
            return True
        else:
            return False
    
    def automove(self):
        AX.X.move(self.keyboard, self.dx)
        AX.Y.move(self.keyboard, self.dy)