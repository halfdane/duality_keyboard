from build123d import *
import math
from ocp_vscode import *
from dataclasses import dataclass

@dataclass
class PinDimensions:
    radius: float = 0.5

class Pin:

    dims = PinDimensions()

    def __init__(self, length):
        self.length = length

        with BuildPart() as pin:
            with BuildLine():
                FilletPolyline([
                    (0, 0), # bottom
                    (0, self.length), # top
                    # at the top, bend to the right, 
                    (2, self.length), # right
                    (2, self.length, -1.05), # then bend down
                    (0, self.length, -1.05), # back to center
                ], radius=0.5)
            with BuildSketch(Plane.XZ):
                Circle(radius=self.dims.radius)
            sweep()
        self.model = pin.part



# main method
if __name__ == "__main__":
    import time
    from ocp_vscode import *

    set_port(3939)
    show_clear()
    set_defaults(ortho=True, default_edgecolor="#121212", reset_camera=Camera.KEEP)
    set_colormap(ColorMap.seeded(colormap="rgb", alpha=1, seed_value="wave"))

    pin = Pin(length = 50)
    show_object(pin.model, name="pin")