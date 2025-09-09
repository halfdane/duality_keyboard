from dataclasses import dataclass
import math
import copy
from build123d import *
from models.switch import Choc
from models.xiao import Xiao
from models.power_switch import PowerSwitch
from models.knurl import Knurl
from models.symbol import Symbol

from ocp_vscode import *


@dataclass
class CaseDimensions:
    clearance: float = 0.02
    wall_thickness: float = 1.3
    pin_radius: float = 0.5
    magnet_radius: float = 5
    magnet_thickness_z: float = 2
    weight_x: float = 19
    weight_y: float = 11.5
    weight_z: float = 4
    battery_x: float = 31
    battery_y: float = 17
    battery_z: float = 5.5

    shadow_line_height_z: float = 0.3
    shadow_line_depth_x: float = 0.3

    pattern_depth: float = 0.2

    case_height_z: float = Choc.bottom_housing.height_z + Choc.posts.post_height_z
    keywell_height_z: float = Choc.base.thickness_z + Choc.upper_housing.height_z + Choc.stem.height_z + Choc.cap.height_z


class DualityWaveCase:
    dims = CaseDimensions()

    def __init__(self, with_knurl=False, debug=False):
        self.with_knurl = with_knurl
        self.debug = debug

        self.create_case()

    def create_case(self):
        with BuildPart() as self.case:
            self.case.name = "Case"

            Box(200, 200, self.dims.wall_thickness)

            pinkie_y = -Choc.cap.length_y / 2
            with BuildSketch() as pinkie:
                with Locations((0, pinkie_y), (0, Choc.cap.length_y + pinkie_y), (0, 2*Choc.cap.length_y + pinkie_y)):
                    Rectangle(Choc.base.width_x, Choc.base.length_y)
                pinkie = pinkie.sketch.rotate(Axis.Z, 8)
            ring_y = Choc.cap.length_y / 3
            middle_y = 15
            pointer_y = 10
            inner_y = 5
            with BuildSketch() as fingers:
                with Locations(
                    (Choc.cap.width_x, ring_y), (Choc.cap.width_x, Choc.cap.length_y + ring_y), (Choc.cap.width_x, 2*Choc.cap.length_y + ring_y),
                    (2*Choc.cap.width_x, middle_y), (2*Choc.cap.width_x, Choc.cap.length_y + middle_y), (2*Choc.cap.width_x, 2*Choc.cap.length_y + middle_y),
                    (3*Choc.cap.width_x, pointer_y), (3*Choc.cap.width_x, Choc.cap.length_y + pointer_y), (3*Choc.cap.width_x, 2*Choc.cap.length_y + pointer_y),
                    (4*Choc.cap.width_x, inner_y), (4*Choc.cap.width_x, Choc.cap.length_y + inner_y), (4*Choc.cap.width_x, 2*Choc.cap.length_y + inner_y)
                ):
                    Rectangle(Choc.base.width_x, Choc.base.length_y)
                fingers = fingers.sketch

            with BuildSketch(self.case.faces().sort_by(Axis.Z)[-1]) as outline:
                add(pinkie)
                add(fingers)
            extrude(amount=-self.dims.wall_thickness, mode=Mode.SUBTRACT)

            if (self.debug):
                push_object(outline, name="outline")

if __name__ == "__main__":
    set_port(3939)
    show_clear()
    set_defaults(ortho=True, default_edgecolor="#121212", reset_camera=Camera.KEEP)
    set_colormap(ColorMap.seeded(colormap="rgb", alpha=1, seed_value="wave"))

    knurl = False
    case = DualityWaveCase(with_knurl=knurl, debug=True)

    push_object(case.case) if hasattr(case, "case") else None
    show_objects()