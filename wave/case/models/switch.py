import os
from dataclasses import dataclass
from build123d import *

@dataclass
class BaseDimensions:
    width_x: float = 15
    length_y: float = 15
    thickness_z: float = 0.8

@dataclass
class BottomHousingDimensions:
    width_x: float = 13.8
    depth_y: float = 13.8
    height_z: float = 2.2

@dataclass
class PostDimensions:
    post_height_z: float = 2.65
    center_post_radius: float = 1.6
    alignment_pin_radius: float = 0.9
    alignment_pin_x_offset: float = 5.5

@dataclass
class PinsDimensions:
    pin1_x: float = 0
    pin1_y: float = 5.9
    pin2_x: float = -5
    pin2_y: float = 3.8

    radius: float = 0.2
    height_z: float = 3

@dataclass
class ClampDimensions:
    width_x: float = 0.35
    height_z: float = 0.9
    depth_y: float = 3.154
    offset_between: float = 3.5

    clearance_z: float = BottomHousingDimensions.height_z - height_z

@dataclass
class UpperHousingDimensions:
    height_z: float = 2.5
    width_x: float = 13.6
    depth_y: float = 13.8

@dataclass
class StemDimensions:
    height_z: float = 2.5
    width_x: float = 10
    depth_y: float = 4.5
    ext_width_x: float = 3
    ext_depth_y: float = 1.2

@dataclass
class CapDimensions:
    width_x: float = 18
    length_y: float = 17.1
    height_z: float = 2.25

    width_x_without_space: float = 17.45
    length_y_without_space: float = 16.571

class Choc:
    base = BaseDimensions()
    bottom_housing = BottomHousingDimensions()
    posts = PostDimensions()
    pins = PinsDimensions()
    clamps = ClampDimensions()
    upper_housing = UpperHousingDimensions()
    stem = StemDimensions()
    cap = CapDimensions()

    def __init__(self, show_model=False, show_step_file=False):
        with BuildPart() as self.model:
            with BuildPart() as main_housing_base:
                with Locations((0, 0, +self.base.thickness_z / 2)):
                    Box(self.base.width_x, self.base.length_y, self.base.thickness_z)

            with BuildPart(main_housing_base.faces().sort_by(Axis.Z)[0]) as bottom_housing:
                with Locations((0, 0, self.bottom_housing.height_z / 2)):
                    Box(self.bottom_housing.width_x, self.bottom_housing.depth_y, self.bottom_housing.height_z)

            with BuildPart(bottom_housing.faces().sort_by(Axis.Z)[0]) as posts:
                with Locations((0, 0, self.posts.post_height_z / 2)):
                    Cylinder(self.posts.center_post_radius, self.posts.post_height_z)
                with Locations((self.posts.alignment_pin_x_offset, 0, self.posts.post_height_z / 2), 
                            (-self.posts.alignment_pin_x_offset, 0, self.posts.post_height_z / 2)):
                    Cylinder(self.posts.alignment_pin_radius, self.posts.post_height_z)
                with Locations((self.pins.pin1_x, self.pins.pin1_y, self.pins.height_z / 2),
                            (self.pins.pin2_x, self.pins.pin2_y, self.pins.height_z / 2)):
                    Cylinder(self.pins.radius, self.pins.height_z)

            with BuildPart(bottom_housing.faces().filter_by(Axis.X)) as snap_in_clamps:
                with Locations(((self.bottom_housing.height_z-self.clamps.height_z)/2, self.clamps.offset_between, self.clamps.width_x/2), 
                            ((self.bottom_housing.height_z-self.clamps.height_z)/2, -self.clamps.offset_between, self.clamps.width_x/2)):
                    Box(self.clamps.height_z, self.clamps.depth_y, self.clamps.width_x)

            with BuildPart(main_housing_base.faces().sort_by(Axis.Z)[-1]) as upper_housing:
                with Locations((0, 0, self.upper_housing.height_z / 2)):
                    Box(self.upper_housing.width_x, self.upper_housing.depth_y, self.upper_housing.height_z)

            with BuildPart(upper_housing.faces().sort_by(Axis.Z)[-1]) as stem:
                with Locations((0, 0, self.stem.height_z / 2)):
                    Box(self.stem.width_x, self.stem.depth_y, self.stem.height_z)
                with Locations((0, -(self.stem.depth_y+self.stem.ext_depth_y)/2, self.stem.height_z / 2)):
                    Box(self.stem.ext_width_x, self.stem.ext_depth_y, self.stem.height_z)

            with BuildPart() as cap:
                with BuildSketch(stem.faces().sort_by(Axis.Z)[-1]):
                    with Locations((0, 0.05)):
                        RectangleRounded(self.cap.width_x_without_space, self.cap.length_y_without_space, 2)
                extrude(amount=self.cap.height_z)
                fillet(cap.faces().sort_by(Axis.Z)[-1].edges(), 1.5)
                s = 40
                with Locations((0, 0, s+6.7)):
                    Sphere(s, mode=Mode.SUBTRACT, rotation=(90, 0, 0))

        if show_model:
            from ocp_vscode import show_all
            if show_step_file:
                step_file = import_step('/home/tvollert/Downloads/MBK_Keycap_-_1u.step')
                step_file = step_file.translate((0, -0.15, 3.6+self.base.thickness_z/2))
                pass
                
            show_all()



# main method
if __name__ == "__main__":
    from ocp_vscode import show_object, set_defaults, Camera
    set_defaults(ortho=True, default_edgecolor="#121212", reset_camera=Camera.KEEP)
    switch = Choc(show_model=True, show_step_file=True)
    # show_object(switch.model, name="Kailh Choc Switch")
