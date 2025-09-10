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

class KeyCol:
    rotation: float = 0
    locs: list[Location] = []

@dataclass
class PinkieDimensions(KeyCol):
    x: float = 0
    y: float = 0
    offset: float = -2
    rotation: float = 8
    locs: list[Location] = (
        Location((0, 0)), 
        Location((-Choc.cap.width_x/rotation, Choc.cap.length_y)), 
        Location((-2*Choc.cap.width_x/rotation, 2*Choc.cap.length_y))
    )

@dataclass
class RingFingerDimensions(KeyCol):
    x: float = Choc.cap.width_x + PinkieDimensions.offset
    y: float = 14
    rotation: float = 0
    locs: list[Location] = (
        Location((x, y)), 
        Location((x, Choc.cap.length_y + y)), 
        Location((x, 2*Choc.cap.length_y + y))
    )

@dataclass
class MiddleFingerDimensions(KeyCol):
    x: float = 2*Choc.cap.width_x + PinkieDimensions.offset
    y: float = 22.4
    rotation: float = 0
    locs: list[Location] = (
        Location((x, y)), 
        Location((x, Choc.cap.length_y + y)), 
        Location((x, 2*Choc.cap.length_y + y))
    )

@dataclass
class PointerFingerDimensions(KeyCol):
    x: float = 3*Choc.cap.width_x + PinkieDimensions.offset
    y: float = 18
    rotation: float = 0
    locs: list[Location] = (
        Location((x, y)), 
        Location((x, Choc.cap.length_y + y)), 
        Location((x, 2*Choc.cap.length_y + y))
    )

@dataclass
class InnerFingerDimensions(KeyCol):
    x: float = 4*Choc.cap.width_x + PinkieDimensions.offset
    y: float = 14
    rotation: float = 0
    locs: list[Location] = (
        Location((x, y)), 
        Location((x, Choc.cap.length_y + y)), 
        Location((x, 2*Choc.cap.length_y + y))
    )

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
    pinkie = PinkieDimensions()
    ring = RingFingerDimensions()
    middle = MiddleFingerDimensions()
    pointer = PointerFingerDimensions()
    inner = InnerFingerDimensions()

    def __init__(self, with_knurl=False, debug=False):
        self.with_knurl = with_knurl
        self.debug = debug

        self.create_case()

    def create_case(self):
        with BuildPart() as self.case:
            self.case.name = "Case"

            plate = Box(200, 200, self.dims.wall_thickness, mode=Mode.PRIVATE)
            plate = plate.translate((80, 90, -self.dims.wall_thickness/2))
            add(plate)
            
            
            with BuildSketch() as outline:
                for keycol in [self.pinkie, self.ring, self.middle, self.pointer, self.inner]:
                    with Locations(*keycol.locs):
                        Rectangle(Choc.bottom_housing.width_x, Choc.bottom_housing.depth_y, rotation=keycol.rotation)
            extrude(amount=-self.dims.wall_thickness, mode=Mode.SUBTRACT)
            if (self.debug):
                push_object(outline, name="outline")

            choc = Choc()
            for keycol in [self.pinkie, self.ring, self.middle, self.pointer, self.inner]:
                with Locations(*keycol.locs):
                    add(copy.copy(choc.model.part).rotate(Axis.Z, keycol.rotation))



            

if __name__ == "__main__":
    set_port(3939)
    show_clear()
    set_defaults(ortho=True, default_edgecolor="#121212", reset_camera=Camera.KEEP)
    set_colormap(ColorMap.seeded(colormap="rgb", alpha=1, seed_value="wave"))

    knurl = False
    case = DualityWaveCase(with_knurl=knurl, debug=True)

    push_object(case.case) if hasattr(case, "case") else None
    show_objects()