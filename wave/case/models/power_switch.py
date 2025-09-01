from build123d import *

from dataclasses import dataclass
from build123d import *

@dataclass
class PowerSwitchDimensions:
    width_x: float = 9
    length_y: float = 3.5
    thickness_z: float = 4

    lever_clearance: float = 3.5
    lever_width_x: float = 1.5
    lever_length_y: float = 1.5
    lever_height_z: float = 1.5
    lever_offset_y: float = 0.8

    pin_length: float = 3.5

class PowerSwitch:
    dims = PowerSwitchDimensions()

    def __init__(self):
        with BuildPart() as self.model:
            with BuildPart() as base:
                Box(self.dims.width_x, self.dims.length_y, self.dims.thickness_z)

                with Locations((0, self.dims.lever_offset_y, self.dims.thickness_z/2-0.05)):
                    Box(self.dims.lever_clearance, self.dims.lever_width_x, 0.1, mode=Mode.SUBTRACT)

    
            with BuildPart() as lever:
                with Locations((self.dims.lever_clearance/2 - self.dims.lever_length_y/2, self.dims.lever_offset_y, self.dims.thickness_z/2+self.dims.lever_length_y/2)):
                    Box(self.dims.lever_length_y, self.dims.lever_width_x, self.dims.lever_height_z)
            with BuildPart(self.model.faces().sort_by(Axis.Y)[0]) as pins:
                with Locations((0, 0, self.dims.length_y/2)):
                    with GridLocations(3.5, 2.2, 2, 3):
                        Cylinder(0.1, self.dims.pin_length)
            

# main method
if __name__ == "__main__":
    from ocp_vscode import *

    set_port(3939)
    show_clear()
    set_defaults(ortho=True, default_edgecolor="#121212", reset_camera=Camera.KEEP)
    set_colormap(ColorMap.seeded(colormap="rgb", alpha=1, seed_value="wave"))


    switch = PowerSwitch()

    