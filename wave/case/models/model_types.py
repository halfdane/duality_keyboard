from dataclasses import dataclass
from build123d import *

class RectDimensions(Vector):
    pass

class RoundDimensions(Vector):
    def __init__(self, radius: float, z: float):
        super().__init__(radius, 0, z)

    @property
    def radius(self):
        return self.X

@dataclass(frozen=True)
class PosAndDims:
    p: Vector
    d: RectDimensions | RoundDimensions