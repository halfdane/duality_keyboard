from dataclasses import dataclass, field, InitVar
import math
import copy

from wave_generator import WaveCase
from build123d import *
from models.choc import Choc
from models.cherry import Cherry
from models.switch import Switch
from models.xiao import Xiao
from models.power_switch import PowerSwitch
from models.symbol import Symbol
from models.space_invader import SpaceInvader
from models.keys import ErgoKeys, Point, get_points
from models.rubber_bumper import RubberBumper, BumperDimensions
from models.pin import Pin
from models.model_types import RoundDimensions, PosAndDims, RectDimensions, WaveDimensions

from ocp_vscode import *

from models.outline import Outline


@dataclass
class CaseDimensions(WaveDimensions):
    switch: InitVar[Switch]
    outline: InitVar[Outline]
    keys: InitVar[ErgoKeys]

    clearance: float = 0.02
    wall_thickness: float = 1.8

    clip_protusion: float = 0.4

    def __post_init__(self, switch: Switch, outline: Outline, keys: ErgoKeys):
        self.add_below_choc_posts: float = 0.7
        self.bottom_plate_z: float = 3.0
        self.above_z: float = switch.above.d.Z
        self.below_z: float = switch.below.d.Z + self.add_below_choc_posts
        self.keyplate_z: float = self.below_z - self.bottom_plate_z

        self.clip_lower_z: float = -self.below_z + self.bottom_plate_z/2
        self.clip_upper_z: float = -self.keyplate_z/2

        xiao_pos_x: float = outline.top_left.X + Xiao.dims.d.X/2 + 3.5*self.wall_thickness
        xiao_pos_y: float = outline.top_left.Y - Xiao.dims.d.Y/2 - Xiao.usb.forward_y - self.wall_thickness - 2*self.clearance
        xiao_pos_z: float = -1.45
        self.xiao_position: Vector = Vector(xiao_pos_x, xiao_pos_y, xiao_pos_z)
        self.xiao_mirror_position: Vector = Vector(-xiao_pos_x, xiao_pos_y, xiao_pos_z)

        xiao_to_power_switch: float = PowerSwitch.dims.d.Y/2 + PowerSwitch.dims.pin_length/2
        self.powerswitch_rotation: Vector = Vector(0, 180, -90)
        self.powerswitch_position: Vector = Vector(
                xiao_pos_x + Xiao.dims.d.X/2 + xiao_to_power_switch, 
                xiao_pos_y - 1, 
                -(self.below_z - 0.75*PowerSwitch.lever.d.Z))
        
        self.pin_radius: float = Pin.dims.radius + self.clearance
        self.pin_x: float = outline.top_right.X/2
        self.pin_plane: Plane = Plane(
            (self.pin_x, outline.top_right.Y, -self.keyplate_z), 
            z_dir=-Axis.Y.direction, x_dir=Axis.X.direction)
        self.pin_location: Vector = Vector(0, 0)

        battery_d: RectDimensions = RectDimensions(31, 17 , 5.5)
        self.battery_pd = PosAndDims(
            d=battery_d,
            p=outline.top_left \
                + ((self.wall_thickness + self.clearance), -(self.wall_thickness + self.clearance)) \
                + (battery_d.X/2, - battery_d.Y/2, (self.above_z - battery_d.Z/2 - self.wall_thickness)))
        
        self.magnet_d: RoundDimensions = RoundDimensions(5, 2)
        magnet_z: float = self.above_z - 0.5
        self.magnet_positions: list[Vector] = (
            outline.top_right + (-self.wall_thickness - self.clearance - self.magnet_d.radius - 6, -self.wall_thickness - self.clearance - self.magnet_d.radius - 1, magnet_z),
            keys.finger_clusters[0][0][2].p + Vector(0, switch.cap.d.Y/2 + self.magnet_d.radius + 4, magnet_z).rotate(Axis.Z, keys.finger_clusters[0][0][2].r),
            keys.finger_clusters[0][2][2].p + Vector(0, switch.cap.d.Y/2 + self.magnet_d.radius + 1.5, magnet_z).rotate(Axis.Z, keys.finger_clusters[0][2][2].r),
            keys.finger_clusters[0][2][0].p + Vector(0, -switch.cap.d.Y/2 - self.magnet_d.radius - 1.5, magnet_z).rotate(Axis.Z, keys.finger_clusters[0][2][0].r),
            keys.finger_clusters[0][3][0].p + Vector(-3, -switch.cap.d.Y/2 - self.magnet_d.radius - 2, magnet_z),

        )

        self.weight_d: Vector = Vector(22.9, 12.0, 4.4)
        self.weight_positions: list[Vector] = (
            outline.top_right + (-self.wall_thickness - self.clearance - self.weight_d.X/2, -self.wall_thickness - self.clearance - self.weight_d.Y/2, self.magnet_positions[0].Z - self.magnet_d.Z),
        )

        bumpers_base_offset = 2.5
        bumpers_radius = BumperDimensions.radius + bumpers_base_offset
        self.bumper_locations = [
            keys.thumb_clusters[0][1][0].p + Vector(switch.cap.d.X/2 - bumpers_radius/2 - 0.5, -switch.cap.d.Y/2+bumpers_radius/2 + 0.5).rotate(Axis.Z, keys.thumb_clusters[0][1][0].r),
            outline.top_right + Vector(-bumpers_radius, -bumpers_radius),
            outline.bottom_left + Vector(bumpers_radius, bumpers_radius),
            outline.top_left + Vector(bumpers_radius, -bumpers_radius),
            (keys.finger_clusters[0][2][0].p + keys.finger_clusters[0][2][1].p) / 2 + (8, 0),
        ]

        self.space_invader: Location = Location(
            outline.cirque_recess_position + (outline.cirque_recess_radius-2, outline.cirque_recess_radius),
            (0, 0, -40))


if __name__ == "__main__":
    set_port(3939)
    switch = Choc()
    config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ergogen', 'wave.yml')
    points = get_points(file_path=config_path)
    keys = ErgoKeys(points=points)
    outline = Outline(switch=switch, keys=keys, wall_thickness=CaseDimensions.wall_thickness)
    dims = CaseDimensions(switch=switch, outline=outline, keys=keys)
    case = WaveCase(switch=switch, keys=keys, caseDimensions=dims, outline=outline, debug=True, both_sides=False)
    show_clear()
    set_defaults(ortho=True, default_edgecolor="#121212", reset_camera=Camera.KEEP)
    set_colormap(ColorMap.seeded(colormap="rgb", alpha=1, seed_value="wave"))
    show_objects() 

    export_stl(case.keywell_left, "keywell_left.stl", tolerance=0.01) if hasattr(case, "keywell_left") else None
    export_stl(case.keyplate_left, "keyplate_left.stl", tolerance=0.01) if hasattr(case, "keyplate_left") else None
    export_stl(case.bottom_left, "bottom_left.stl", tolerance=0.01) if hasattr(case, "bottom_left") else None
