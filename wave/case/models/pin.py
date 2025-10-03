from build123d import *
import math
from ocp_vscode import *
from dataclasses import dataclass

@dataclass
class PinDimensions:
    radius: float = 0.6
    length: float = 13
    point: float = 3
    shaft: float = length - point

class Pin:

    dims = PinDimensions()

    def __init__(self):
        with BuildPart() as pin:
            with BuildPart(Plane.XY.offset(self.dims.shaft/2)) as shaft:
                Cylinder(radius=self.dims.radius, height=self.dims.shaft)
            with BuildPart(Plane.XY.offset(self.dims.shaft + self.dims.point/2)) as point:
                Cone(self.dims.radius, 0, self.dims.point)
            with BuildPart(Plane.XY.offset(-0.1)) as head:
                Cylinder(radius=self.dims.radius+0.5, height=0.2)

        self.model = pin.part




# main method
if __name__ == "__main__":
    import time
    from ocp_vscode import *

    set_port(3939)
    show_clear()
    set_defaults(ortho=True, default_edgecolor="#121212", reset_camera=Camera.KEEP)
    set_colormap(ColorMap.seeded(colormap="rgb", alpha=1, seed_value="wave"))

    pin = Pin()
    show_object(pin.model, name="pin")