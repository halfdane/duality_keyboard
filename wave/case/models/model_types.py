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

class WaveDimensions:
    clearance: float
    wall_thickness: float

    above_z: float
    add_below_choc_posts: float
    below_z: float
    bottom_plate_z: float
    keyplate_z: float

    clip_protusion: float
    clip_lower_z: float
    clip_upper_z: float

    xiao_position: Vector
    xiao_mirror_position: Vector

    powerswitch_position: Vector
    powerswitch_rotation: Vector

    pin_radius: float
    pin_plane: Plane
    pin_locations: list[Vector]

    battery_pd: PosAndDims

    magnet_d: RoundDimensions
    magnet_positions: list[Vector]

    weight_d: Vector
    weight_positions: list[Vector]

    bumper_locations: list[Vector]

    space_invader: Location = None