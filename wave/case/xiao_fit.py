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

class SingleSwitchXiaoCase:
    dims = CaseDimensions()


    def __init__(self, with_knurl=False):
        self.with_knurl = with_knurl
        self.rows = 2
        self.cols = 2
        self.width_y = Xiao.board.depth_y + 3 * self.dims.wall_thickness + self.rows*Choc.cap.length_y
        self.length_x = max(Xiao.board.width_x, self.cols*Choc.cap.width_x) + 2 * self.dims.wall_thickness + 4*self.dims.wall_thickness + self.dims.wall_thickness

        print(f"Case dimensions: {self.length_x} x {self.width_y}")
        
        self.choc_hole_size = Choc.bottom_housing.width_x + self.dims.clearance
        self.key_y = self.width_y/2 - (self.rows*Choc.cap.length_y)/2 - self.dims.wall_thickness/2
        self.wall_height = Choc.bottom_housing.height_z + Choc.posts.post_height_z
        self.keywell_height_z = Choc.base.thickness_z + Choc.upper_housing.height_z + Choc.stem.height_z + Choc.cap.height_z

        self.keywell_holder_width_y = 20

        if self.with_knurl:
            distance = 2
        else:
            distance = 15

        print("creating snaking pattern")
        self.create_snaking_lines(distance=distance, rotation_angle=30, width_x=self.length_x, height_y=self.width_y)
        print("snaking pattern created")

        self.create_keywell()
        print("keywell created")
        self.create_case()
        print("case created")
        self.create_bottom_plate()
        print("bottom plate created")

        self.create_accessories()
        print("accessories created")

    def create_snaking_lines(self, distance=2, rotation_angle=0, width_x=0, height_y=0):
        face_width=width_x
        face_height=height_y

        with BuildLine() as line:
            y_positions = [-face_height/2 + i * distance for i in range(-7, int(face_height // distance) + 15)]

            polyline_points = []
            for i, y in enumerate(y_positions):
                if i % 2 == 0:  # Even rows: left to right
                    start_point = (-face_width, y)
                    end_point = (face_width, y)
                else:  # Odd rows: right to left
                    start_point = (face_width, y)
                    end_point = (-face_width, y)

                polyline_points.extend([start_point, end_point])
            
            FilletPolyline(*polyline_points, radius=distance/3)
        snake_face = offset(line.line, 0.2*distance)
        with BuildSketch() as sketch:
            add(snake_face.rotate(Axis.Z, rotation_angle))
            make_face()

            add(snake_face.rotate(Axis.Z, -rotation_angle))
            make_face()
        self.snake = sketch.sketch
        self.snake.name = "Snaking Pattern"
        self.snake.distance = distance


    def create_case(self):
        with BuildPart() as self.case:
            self.case.name = "Case"
            with BuildSketch() as base:
                Rectangle(self.length_x, self.width_y)
                with Locations((-self.length_x/2+2*self.dims.wall_thickness+self.dims.clearance, 0),
                               (self.length_x/2-2*self.dims.wall_thickness-self.dims.clearance, 0)):
                    Rectangle(2*self.dims.wall_thickness+2*self.dims.clearance, 20+2*self.dims.clearance, mode=Mode.SUBTRACT)
            extrude(amount=self.dims.wall_thickness)

            with BuildSketch() as keyhole:
                with Locations((0, self.key_y)):
                    with GridLocations(Choc.cap.width_x, Choc.cap.length_y, self.cols, self.rows):
                        Rectangle(self.choc_hole_size + self.dims.clearance, self.choc_hole_size + self.dims.clearance)
            extrude(amount=self.dims.wall_thickness, mode=Mode.SUBTRACT)

            with BuildSketch() as walls:
                outer=Rectangle(self.length_x, self.width_y)
                offset(
                    outer,
                    -self.dims.wall_thickness,
                    mode=Mode.SUBTRACT,
                    kind=Kind.INTERSECTION,
                )
            extrude(amount=-self.wall_height)

            with BuildSketch() as xiao_holder:
                with Locations((0, -self.width_y/2 + Xiao.board.depth_y/2 + self.dims.wall_thickness + self.dims.clearance)):
                    Rectangle(Xiao.board.width_x+2*self.dims.clearance, Xiao.board.depth_y+2*self.dims.clearance)
            extrude(amount=self.dims.wall_thickness/2, mode=Mode.SUBTRACT)

            with BuildSketch() as xiao_hole:
                with Locations((0, -self.width_y/2 + Xiao.board.depth_y/2 + self.dims.wall_thickness + self.dims.clearance)):
                    Rectangle(Xiao.board.width_x -1, Xiao.board.depth_y -4)
            extrude(amount=2, mode=Mode.SUBTRACT)

            usb_face = self.case.faces().sort_by(Axis.Y)[0]
            with BuildSketch(usb_face) as usb_hole:
                usb_z_position = self.wall_height/2 - Xiao.usb.height_z/2 - self.dims.wall_thickness/2 - Xiao.board.thickness_z/2
                with Locations((0, usb_z_position)):
                    RectangleRounded(Xiao.usb.width_x + 2*self.dims.clearance, Xiao.usb.height_z+2*self.dims.clearance, radius=Xiao.usb.radius+self.dims.clearance)
                with Locations((Xiao.usb.width_x/2+1, usb_z_position+1)):
                    Circle(0.5)
            extrude(amount=-7, mode=Mode.SUBTRACT)

            with BuildSketch(usb_face) as case_pin_holes:
                pin_y_position = 0
                with Locations((self.length_x/2-2*self.dims.wall_thickness, pin_y_position), 
                               (-self.length_x/2+2*self.dims.wall_thickness, pin_y_position)):
                    Circle(self.dims.pin_radius + self.dims.clearance)
            extrude(amount=-self.width_y+self.dims.wall_thickness/2, mode=Mode.SUBTRACT)
            with BuildSketch(usb_face) as case_pin_recess:
                with Locations((self.length_x/2-2*self.dims.wall_thickness - 2, pin_y_position), 
                               (-self.length_x/2+2*self.dims.wall_thickness + 2, pin_y_position)):
                    RectangleRounded(5, 2*self.dims.pin_radius + 2*self.dims.clearance, self.dims.pin_radius)
            extrude(amount=-1.5*self.dims.pin_radius, mode=Mode.SUBTRACT)

            with BuildSketch() as power_switch_hole:
                with Locations((
                    self.length_x/2 - PowerSwitch.dims.width_x/2 - 3*self.dims.wall_thickness - 2*self.dims.clearance, 
                    -self.width_y/2 + PowerSwitch.dims.length_y/2 + self.dims.wall_thickness + self.dims.clearance)):
                    Rectangle(PowerSwitch.dims.width_x + 2*self.dims.clearance, PowerSwitch.dims.length_y + 2*self.dims.clearance)
            extrude(amount=self.wall_height - self.dims.wall_thickness/3 - PowerSwitch.dims.thickness_z + 3*self.dims.clearance, mode=Mode.SUBTRACT)
            with BuildSketch() as power_switch_pin_holes:
                with Locations((
                    self.length_x/2 - PowerSwitch.dims.width_x/2 - 3*self.dims.wall_thickness - 2*self.dims.clearance, 
                    -self.width_y/2 + PowerSwitch.dims.length_y + self.dims.wall_thickness + self.dims.clearance)):
                    Rectangle(0.75*PowerSwitch.dims.width_x, 1)
            extrude(amount=self.dims.wall_thickness, mode=Mode.SUBTRACT)

            chamfer(self.case.faces().sort_by(Axis.Y)[0].edges().sort_by(Axis.Z)[-1], length=self.dims.shadow_line_depth_x/2)

            chamfer(self.case.faces().sort_by(Axis.Y)[0].edges().sort_by(Axis.Z)[0], length=self.dims.wall_thickness/3)
            chamfer(self.case.faces().sort_by(Axis.Y)[-1].edges().sort_by(Axis.Z)[0], length=self.dims.wall_thickness/3)
            chamfer(self.case.faces().sort_by(Axis.X)[0].edges().sort_by(Axis.Z)[0], length=self.dims.wall_thickness/3)
            chamfer(self.case.faces().sort_by(Axis.X)[0].edges().sort_by(Axis.Y)[0], length=self.dims.wall_thickness/3)
            chamfer(self.case.faces().sort_by(Axis.X)[0].edges().sort_by(Axis.Y)[-1], length=self.dims.wall_thickness/3)
            chamfer(self.case.faces().sort_by(Axis.X)[-1].edges().sort_by(Axis.Z)[0], length=self.dims.wall_thickness/3)
            chamfer(self.case.faces().sort_by(Axis.X)[-1].edges().sort_by(Axis.Y)[0], length=self.dims.wall_thickness/3)
            chamfer(self.case.faces().sort_by(Axis.X)[-1].edges().sort_by(Axis.Y)[-1], length=self.dims.wall_thickness/3)

            print("Adding pattern to case")
            for pattern_loc in [
                (0, 0, -self.wall_height),
                (self.length_x/2, 0, 0),
                (-self.length_x/2, 0, 0),
                (0, self.width_y/2, 0),
                (0, -self.width_y/2, 0),
            ]:
                with BuildSketch(Plane(pattern_loc, z_dir=Vector(pattern_loc))):
                    add(self.snake)
            extrude(amount=-self.dims.pattern_depth, mode=Mode.SUBTRACT)

            print("Pattern added to case")


    def create_keywell(self):
        with BuildPart() as self.keywell:
            self.keywell.name = "Keywell"
            keywell_extra_clearance_x = 0.47
            keywell_extra_clearance_y = 0.1

            bottom_left = (-self.length_x/2, -self.width_y/2 )
            bottom_right = (self.length_x/2, -self.width_y/2)  

            top_right = (self.length_x/2, self.width_y/2)

            keywell_top_right = (self.cols*(Choc.cap.width_x/2)+keywell_extra_clearance_x, self.width_y/2)
            keywell_bottom_right = (self.cols*(Choc.cap.width_x/2)+keywell_extra_clearance_x, self.width_y/2 - self.rows*(Choc.cap.length_y) - self.dims.wall_thickness + keywell_extra_clearance_y)
            keywell_bottom_left = (-self.cols*(Choc.cap.width_x/2)-keywell_extra_clearance_x, self.width_y/2 - self.rows*(Choc.cap.length_y) - self.dims.wall_thickness + keywell_extra_clearance_y)
            keywell_top_left = (-self.cols*(Choc.cap.width_x/2)-keywell_extra_clearance_x, self.width_y/2)

            top_left = (-self.length_x/2, self.width_y/2)
            with BuildSketch():
                Polygon(
                    bottom_left, bottom_right, top_right,
                    keywell_top_right, keywell_bottom_right, 
                    keywell_bottom_left, keywell_top_left,
                    top_left
                )
            extrude(amount=self.keywell_height_z)

            with BuildSketch() as keywell_holder_sketch:
                with Locations((-self.length_x/2+2*self.dims.wall_thickness+self.dims.clearance, 0),
                               (self.length_x/2-2*self.dims.wall_thickness-self.dims.clearance, 0)):
                    Rectangle(2*self.dims.wall_thickness, self.keywell_holder_width_y)
            keywell_holder = extrude(amount=-self.wall_height + self.dims.clearance)

            keywell_holder_front_face = keywell_holder.faces().filter_by(Axis.Y)[0:3:2]
            with BuildSketch(keywell_holder_front_face) as keywell_pin_holes:
                pin_y_position = -self.dims.wall_thickness/2 - 0.58*self.dims.clearance
                with Locations((self.dims.clearance, pin_y_position)):
                    Circle(self.dims.pin_radius + self.dims.clearance)
            extrude(amount=-self.width_y+self.dims.wall_thickness/2, mode=Mode.SUBTRACT)

            with BuildSketch() as keywell_magnets:
                with Locations((0, -self.width_y/2 + self.dims.magnet_radius + self.dims.wall_thickness + 2*self.dims.clearance, 0)):
                    Circle(self.dims.magnet_radius + self.dims.clearance)
            extrude(amount=self.keywell_height_z-self.dims.wall_thickness, mode=Mode.SUBTRACT)

            with BuildSketch() as keywell_weight:
                with Locations((0, -self.width_y/2 + self.dims.weight_y/2 + self.dims.wall_thickness + self.dims.clearance, 0)):
                    Rectangle(self.dims.weight_x + self.dims.clearance, self.dims.weight_y + self.dims.clearance)
            extrude(amount=self.keywell_height_z-self.dims.wall_thickness-0.3, mode=Mode.SUBTRACT)

            with BuildSketch() as keywell_battery:
                with Locations((0, -self.width_y/2 + self.dims.battery_y/2 + self.dims.wall_thickness  + self.dims.clearance, 0)):
                    Rectangle(self.dims.battery_x + self.dims.clearance, self.dims.battery_y + self.dims.clearance)
            extrude(amount=self.keywell_height_z-self.dims.wall_thickness-0.6, mode=Mode.SUBTRACT)

            shadowline_y = -self.keywell_height_z/2 + self.dims.shadow_line_height_z/2
            keywell_left_outer_face = self.keywell.faces().sort_by(Axis.X)[0]
            keywell_front_outer_face = self.keywell.faces().sort_by(Axis.Y)[0]
            keywell_left_back_face = self.keywell.faces().filter_by(Axis.Y).sort_by(Axis.X)[0]

            with BuildSketch(keywell_left_outer_face) as left_shadow_line:
                with Locations((0, shadowline_y)):
                    Rectangle(self.width_y, self.dims.shadow_line_height_z)
            extrude(amount=-self.dims.shadow_line_depth_x, mode=Mode.SUBTRACT)

            with BuildSketch(keywell_left_back_face) as left_back_shadow_line:
                with BuildLine():
                    backleft_shadowline_y = shadowline_y + self.dims.shadow_line_height_z/2
                    top=Line((3*self.dims.wall_thickness, backleft_shadowline_y), (-1.5*self.dims.wall_thickness, backleft_shadowline_y))
                    right=Line((3*self.dims.wall_thickness, backleft_shadowline_y), (3*self.dims.wall_thickness, backleft_shadowline_y-self.dims.shadow_line_height_z))
                    bottom=Line((3*self.dims.wall_thickness, backleft_shadowline_y-self.dims.shadow_line_height_z), (-1.5*self.dims.wall_thickness-0.28, backleft_shadowline_y-self.dims.shadow_line_height_z))
                    left=RadiusArc(bottom@1, top@1, self.dims.shadow_line_height_z, short_sagitta=True)
                make_face()
            extrude(amount=-self.dims.shadow_line_depth_x, mode=Mode.SUBTRACT)

            chamfer(self.keywell.faces().sort_by(Axis.Y)[0].edges().sort_by(Axis.Z)[0], length=self.dims.shadow_line_depth_x/2)

            chamfer(self.keywell.faces().sort_by(Axis.Z)[-1].edges(), length=self.dims.wall_thickness/3)

            chamfer(self.keywell.faces().sort_by(Axis.X)[0].edges().sort_by(Axis.Y)[0], length=self.dims.wall_thickness/3)
            chamfer(self.keywell.faces().sort_by(Axis.X)[0].edges().sort_by(Axis.Y)[-1], length=self.dims.wall_thickness/3)
            chamfer(self.keywell.faces().sort_by(Axis.X)[-1].edges().sort_by(Axis.Y)[0], length=self.dims.wall_thickness/3)
            chamfer(self.keywell.faces().sort_by(Axis.X)[-1].edges().sort_by(Axis.Y)[-1], length=self.dims.wall_thickness/3)

            self.keywell.part = self.keywell.part.translate((0, 0, self.dims.wall_thickness))
            print("Adding pattern to keywell")
            for pattern_loc in [
                (0, 0, self.keywell_height_z+self.dims.wall_thickness),
                (self.length_x/2, 0, 0),
                (-self.length_x/2,0, 0),
                (0, self.width_y/2, 0),
                (0, -self.width_y/2, 0),
            ]:
                p = Plane(pattern_loc, z_dir=Vector(pattern_loc))
                with BuildSketch(p):
                    add(self.snake)
            extrude(amount=-self.dims.pattern_depth, mode=Mode.SUBTRACT)
  
            print("Pattern added to keywell")


    def create_bottom_plate(self):
        with BuildPart() as self.bottom:
            self.bottom.name = "Bottom Plate"
            bottom_width_y = self.width_y - 2*self.dims.wall_thickness - 2*self.dims.clearance
            bottom_length_x = self.length_x - 2*self.dims.wall_thickness - 2*self.dims.clearance
            with BuildSketch():
                Rectangle(bottom_length_x, bottom_width_y)
            extrude(amount=self.dims.wall_thickness-self.dims.pattern_depth)

            usb_hole_bottom_face = self.bottom.faces().sort_by(Axis.Y)[0]
            with BuildSketch(usb_hole_bottom_face) as usb_hole_bottom:
                with Locations((0, - Xiao.usb.height_z/2 + self.wall_height - Xiao.board.thickness_z - self.dims.clearance)):
                    RectangleRounded(Xiao.usb.width_x + 2*self.dims.clearance, Xiao.usb.height_z+2*self.dims.clearance, radius=Xiao.usb.radius+self.dims.clearance)
            extrude(amount=-6+2*self.dims.clearance, mode=Mode.SUBTRACT)

            with BuildSketch() as bottom_holder:
                remaining = (self.width_y - 2*self.dims.wall_thickness - self.keywell_holder_width_y)/2
                with Locations((bottom_length_x/2 - self.dims.wall_thickness, (bottom_width_y - remaining)/2 + self.dims.clearance),
                               (-bottom_length_x/2 + self.dims.wall_thickness, (bottom_width_y - remaining)/2 + self.dims.clearance),
                               (bottom_length_x/2 - self.dims.wall_thickness, -(bottom_width_y - remaining)/2 - self.dims.clearance),
                               (-bottom_length_x/2 + self.dims.wall_thickness, -(bottom_width_y - remaining)/2 - self.dims.clearance),):
                    Rectangle(2*self.dims.wall_thickness, remaining-2*self.dims.clearance)
            extrude(amount=self.wall_height-self.dims.clearance)

            bottom_front_face = self.bottom.faces().sort_by(Axis.Y)[0]
            with BuildSketch(bottom_front_face) as bottom_pin_holes:
                pin_y_position = (self.wall_height-self.dims.wall_thickness)/2+1.5*self.dims.clearance
                with Locations((self.length_x/2-2*self.dims.wall_thickness, pin_y_position), (-self.length_x/2+2*self.dims.wall_thickness, pin_y_position)):
                    Circle(self.dims.pin_radius + self.dims.clearance)
            extrude(amount=-self.width_y+self.dims.wall_thickness/2, mode=Mode.SUBTRACT)

            print("Adding pattern to bottom plate")
            with BuildSketch() as bottom_pattern:
                add(Rectangle(bottom_length_x, bottom_width_y))
                add(offset(self.snake, -2*self.dims.clearance, mode=Mode.PRIVATE), mode=Mode.INTERSECT)
            extrude(amount=-self.dims.pattern_depth, mode=Mode.ADD)
            self.bottom.part = self.bottom.part.translate((0, 0, self.dims.pattern_depth))
            print("Pattern added to bottom plate")


            lever_width_x = 1
            lever_pos_x = -Xiao.components.reset_button_x
            lever_pos_y = -self.width_y/2 + 5
            with BuildSketch() as reset_lever:
                with BuildLine():
                    l1 = Line((-lever_width_x/2+lever_pos_x, 4+lever_pos_y), (-lever_width_x/2+lever_pos_x, -1+lever_pos_y))
                    l2 = Line((lever_width_x/2+lever_pos_x, 4+lever_pos_y), (lever_width_x/2+lever_pos_x, -1+lever_pos_y))
                    RadiusArc(l1@1, l2@1, 1, short_sagitta=False)

                    offset(amount=0.15)
                make_face()
            extrude(amount=2, mode=Mode.SUBTRACT)

            with BuildSketch() as reset_push:
                with BuildLine():
                    l1 = Line((-lever_width_x/2+lever_pos_x, lever_pos_y), (-lever_width_x/2+lever_pos_x, -1+lever_pos_y))
                    l2 = Line((lever_width_x/2+lever_pos_x, lever_pos_y), (lever_width_x/2+lever_pos_x, -1+lever_pos_y))
                    RadiusArc(l1@1, l2@1, 1, short_sagitta=False)
                    Line(l1@0, l2@0)
                    offset(amount=-0.15)
                make_face()
            extrude(amount=3.5-self.dims.clearance, mode=Mode.ADD)

            with BuildSketch() as power_switch_lever_hole:
                pswitch_x = self.length_x/2 - PowerSwitch.dims.width_x/2 - 3*self.dims.wall_thickness - 2*self.dims.clearance
                pswitch_y = -(self.width_y/2 - PowerSwitch.dims.lever_width_x/2 - self.dims.wall_thickness)
                with Locations((pswitch_x, pswitch_y)):
                    Rectangle(PowerSwitch.dims.lever_clearance + 2*self.dims.clearance, PowerSwitch.dims.lever_width_x + PowerSwitch.dims.lever_offset_y)
            extrude(amount=self.dims.wall_thickness, mode=Mode.SUBTRACT)

            self.bottom.part = self.bottom.part.translate((0, 0, -self.wall_height))


    def create_accessories(self):
        self.accessories = []
        xiao = Xiao()
        xiao = xiao.model.part \
            .translate((0, -self.width_y/2 + xiao.board.depth_y/2 + self.dims.wall_thickness + self.dims.clearance, self.dims.clearance-self.dims.wall_thickness/2)) \
            .rotate(axis=Axis.Y, angle=180)
        xiao.name = "Xiao"
        self.accessories.append(xiao)
        

        choc = Choc()

        locs = GridLocations(Choc.cap.width_x, Choc.cap.length_y, self.cols, self.rows).local_locations
        chocs = [copy.copy(choc.model.part).locate(loc * Location((0, self.key_y, Choc.base.thickness_z + self.dims.wall_thickness))) for loc in locs]
        chocs = Compound(chocs)
        chocs.name = "Choc Switches"
        self.accessories.append(chocs)

        power_switch = PowerSwitch()
        pswitch = power_switch.model.part \
            .rotate(axis=Axis.X, angle=180) \
            .translate((
                self.length_x/2 - PowerSwitch.dims.width_x/2 - 3*self.dims.wall_thickness - 2*self.dims.clearance, 
                -(self.width_y/2 - PowerSwitch.dims.length_y/2 - self.dims.wall_thickness- self.dims.clearance), 
                -self.wall_height + PowerSwitch.dims.thickness_z/2+self.dims.wall_thickness+self.dims.clearance))
        pswitch.name = "Power Switch"
        self.accessories.append(pswitch)

# main method
if __name__ == "__main__":
    set_port(3939)
    show_clear()
    set_defaults(ortho=True, default_edgecolor="#121212", reset_camera=Camera.KEEP)
    set_colormap(ColorMap.seeded(colormap="rgb", alpha=1, seed_value="wave"))

    knurl = True

    proto = SingleSwitchXiaoCase(with_knurl=knurl)
    # push_object(proto.snake) if hasattr(proto, "snake") else None
    # push_object(proto.keywell) if hasattr(proto, "keywell") else None
    # push_object(proto.case) if hasattr(proto, "case") else None
    # push_object(proto.bottom) if hasattr(proto, "bottom") else None
    # if hasattr(proto, "accessories"):
    #     for accessory in proto.accessories:
    #         push_object(accessory)
    # show_objects()

    if knurl:
        export_stl(proto.case.part, "wave_case.stl", tolerance=0.01) if hasattr(proto, "case") else None
        export_stl(proto.keywell.part, "wave_keywell.stl", tolerance=0.01) if hasattr(proto, "keywell") else None
        export_stl(proto.bottom.part, "wave_bottom.stl", tolerance=0.01) if hasattr(proto, "bottom") else None

