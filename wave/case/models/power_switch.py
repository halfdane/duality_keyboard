if __name__ == "__main__":
    import sys, os
    # add parent directory to path
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from build123d import *
from dataclasses import dataclass
from build123d import *
from models.model_types import RectDimensions, RoundDimensions, PosAndDims

@dataclass
class PowerSwitchDimensions:
    d: RectDimensions = RectDimensions(9, 3.4, 4)
    pin_length: float = 4

@dataclass
class LeverDimensions:
    d: RectDimensions = RectDimensions(1.5, 1.5, 1.8)
    clearance: float = 3.5
    p: Vector = Vector(0, 0.8, 0)

class PowerSwitch:
    dims = PowerSwitchDimensions()
    lever = LeverDimensions()

    def __init__(self):
        with BuildPart() as self.model:
            with BuildPart() as base:
                Box(self.dims.d.X, self.dims.d.Y, self.dims.d.Z)

                with Locations((0, self.lever.p.Y, self.dims.d.Z/2-0.05)):
                    Box(self.lever.clearance, self.lever.d.X, 0.1, mode=Mode.SUBTRACT)

            with BuildPart() as lever:
                with Locations((self.lever.clearance/2 - self.lever.d.Y/2, self.lever.p.Y, self.dims.d.Z/2+self.lever.d.Y/2)):
                    Box(self.lever.d.Y, self.lever.d.X, self.lever.d.Z)
            with BuildPart(self.model.faces().sort_by(Axis.Y)[0]) as pins:
                with Locations((0, 0, self.dims.d.Y/2)):
                    with GridLocations(3.5, 2.5, 2, 3):
                        Cylinder(0.1, self.dims.pin_length)
        self.model = self.model.part.translate((0, 0, -self.dims.d.Z/2))
            

# main method
if __name__ == "__main__":
    from ocp_vscode import *

    set_port(3939)
    show_clear()
    set_defaults(ortho=True, default_edgecolor="#121212", reset_camera=Camera.KEEP)
    set_colormap(ColorMap.seeded(colormap="rgb", alpha=1, seed_value="wave"))


    switch = PowerSwitch()
    show_object(switch.model, name="power_switch")

    