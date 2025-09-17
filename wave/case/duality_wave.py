from dataclasses import dataclass, field
import math
import copy
from build123d import *
from models.switch import Choc
from models.xiao import Xiao
from models.power_switch import PowerSwitch
from models.knurl import Knurl
from models.symbol import Symbol
from models.keys import Keys
from models.outline import Outline

from ocp_vscode import *

@dataclass
class CaseDimensions:
    clearance: float = 0.02
    pin_radius: float = 0.5
    pattern_depth: float = 0.2
    pattern_size: float = 2

@dataclass
class BottomDimensions:
    size_z: float = 1.3
    keyplate_offset: float = 2

@dataclass
class KeyplateDimensions:
    keys: Keys
    outline: Outline

    size_z: float = Choc.bottom_housing.height_z + Choc.posts.post_height_z + BottomDimensions.size_z
    switch_clamp_clearance: float = size_z - Choc.clamps.clearance_z

    xiao_offset: float = BottomDimensions.keyplate_offset
    xiao_pos_x: float = 10 + Xiao.board.width_x/2
    xiao_pos_y: float = Outline.dims.base_length_y - Xiao.board.depth_y/2 - xiao_offset
    xiao_pos_z: float = -(Choc.bottom_housing.height_z + Choc.posts.post_height_z - Xiao.board.thickness_z - Xiao.usb.height_z)
    xiao_position: Location = (xiao_pos_x, xiao_pos_y, xiao_pos_z)
    xiao_mirror_position: Location = (-xiao_pos_x, xiao_pos_y, xiao_pos_z)

    connector_width: float = 2
    connector_depth_z: float = Choc.posts.post_height_z

    rubber_bumper_radius: float = 4
    bottom_holder_radius: float = rubber_bumper_radius + 2

    def bottom_holder_locations(self) -> list[Vector]:
        holder_radius = self.bottom_holder_radius
        return [
            (self.keys.thumb.locs[0] + self.keys.thumb.locs[1]) / 2,
            (self.keys.pointer.locs[1] + self.keys.middle.locs[1]) / 2,
            Vector(self.outline.dims.base_width_x, self.outline.dims.base_length_y) - Vector(holder_radius, holder_radius),
            Vector(0, 0) + Vector(holder_radius, holder_radius),
            Vector(0, self.outline.dims.base_length_y) + Vector(holder_radius, -holder_radius),
        ]
    

@dataclass
class KeywellDimensions:
    size_z: float = Choc.base.thickness_z + Choc.upper_housing.height_z + Choc.stem.height_z + Choc.cap.height_z + CaseDimensions.pattern_depth

class DualityWaveCase:
    outline = Outline()
    keys = Keys(outline.dims.switch_offset)

    dims = CaseDimensions()
    keywell_dims = KeywellDimensions()
    keyplate_dims = KeyplateDimensions(keys, outline)
    bottom_dims = BottomDimensions()

    xiao = Xiao()

    debug_content: list = []

    def __init__(self, with_knurl=False, debug=False):
        self.with_knurl = with_knurl
        self.debug = debug
        if self.with_knurl:
            self.knurl = Knurl(debug=debug)
        if self.debug:
            self.dims.pattern_size = 15

        push_object(self.debug_content, name="debug_content") if self.debug else None

        usb_cut = self.xiao.create_usb_cut(self.dims.clearance)

        self.keyplate_left = self.create_keyplate()
        self.keyplate_left = self.keyplate_left - usb_cut.translate(self.keyplate_dims.xiao_position)
        self.keywell_left = self.create_keywell()
        self.bottom_left = self.create_bottom()
        push_object(self.keyplate_left, name="keyplate_left") if self.debug else None
        push_object(self.keywell_left, name="keywell_left") if self.debug else None
        push_object(self.bottom_left, name="bottom_left") if self.debug else None


        self.keyplate_right = mirror(self.keyplate_left, about=Plane.YZ)
        self.keyplate_right = self.keyplate_right - usb_cut.translate(self.keyplate_dims.xiao_mirror_position)
        self.keywell_right = mirror(self.keywell_left, about=Plane.YZ)
        self.bottom_right = mirror(self.bottom_left, about=Plane.YZ)
        push_object(self.keyplate_right, name="keyplate_right") if self.debug else None
        push_object(self.keywell_right, name="keywell_right") if self.debug else None
        push_object(self.bottom_right, name="bottom_right") if self.debug else None

        self.create_accessories()


    def create_keyplate(self):
        print("Creating keyplate...")

        with BuildPart() as keyplate:
            with BuildSketch():
                add(self.outline.sketch)
            extrude(amount=self.keyplate_dims.size_z)
            keyplate.part = keyplate.part.translate((0,0,-self.keyplate_dims.size_z))

            if self.with_knurl: 
                print("Adding knurl...")
                tops = keyplate.faces().filter_by(Axis.Z)
                walls = keyplate.faces().filter_by(lambda f: f not in tops).sort_by(Axis.X, reverse=True)
                self.knurl.patternize(walls + [tops[0]], pattern_depth=self.dims.pattern_depth, distance=self.dims.pattern_size)

            with BuildSketch(Plane.XY.offset(-self.keyplate_dims.size_z)) as bottom_walls:
                offset(self.outline.sketch, -self.bottom_dims.keyplate_offset, kind=Kind.INTERSECTION)
            extrude(amount=self.bottom_dims.size_z, mode=Mode.SUBTRACT)
            self.debug_content.append({"bottom_walls": bottom_walls}) if self.debug else None

            with BuildSketch() as key_holes:
                for keycol in self.keys.keycols:
                    with Locations(keycol.locs):
                        Rectangle(Choc.bottom_housing.width_x, Choc.bottom_housing.depth_y, rotation=keycol.rotation)
            self.debug_content.append({"key_holes (keyplate)": key_holes}) if self.debug else None
            extrude(amount=-Choc.clamps.clearance_z, mode=Mode.SUBTRACT)
            with BuildSketch(Plane.XY.offset(-Choc.clamps.clearance_z)) as keyholes_with_space:
                offset(key_holes.sketch, 1)
            extrude(amount=-self.keyplate_dims.size_z, mode=Mode.SUBTRACT)

            with BuildSketch(Plane(self.keyplate_dims.xiao_position)) as xiao_hole:
                Rectangle(Xiao.board.width_x - 1.5, Xiao.board.depth_y - 1.5)
            extrude(amount=self.keyplate_dims.size_z, mode=Mode.SUBTRACT)
            with BuildSketch(Plane(self.keyplate_dims.xiao_position)) as xiao_cut:
                Rectangle(Xiao.board.width_x + 2*self.dims.clearance, Xiao.board.depth_y + 2*self.dims.clearance)
            extrude(amount=-self.keyplate_dims.size_z, mode=Mode.SUBTRACT)


            with_topline = False
            with BuildSketch(Plane.XY.offset(-self.keyplate_dims.size_z+self.bottom_dims.size_z)) as connector_sketch:
                top_y = self.keys.middle.locs[2].Y+Choc.cap.length_y/2

                if with_topline:
                    with BuildLine() as top_line:
                        FilletPolyline(
                            (self.keys.pinkie.locs[2].X, top_y),
                            (self.keys.inner.locs[2].X, top_y),
                            (self.keys.inner.locs[2].X, self.keys.inner.locs[0].Y),
                            radius=2
                        )
                        offset(amount=self.keyplate_dims.connector_width/2, side=Side.BOTH)
                    make_face()

                for row in range(3):
                    with BuildLine() as row_line:
                        pts = [ keycol.locs[row] + (Choc.pins.pin2_x, -Choc.pins.pin2_y) for keycol in self.keys.finger_cols]
                        Polyline(*pts)
                        offset(amount=self.keyplate_dims.connector_width/2, side=Side.BOTH)
                    make_face()

                for col in [self.keys.inner, self.keys.pointer, self.keys.middle, self.keys.ring]:
                    column_to_topline = Line(col.locs[0], col.locs[2])
                    offset(column_to_topline, amount=self.keyplate_dims.connector_width/2, side=Side.BOTH)
                    make_face()
                
                with BuildLine() as pinkie_to_topline:
                    pts = [ self.keys.pinkie.locs[0], self.keys.pinkie.locs[2], (self.keys.pinkie.locs[2].X, top_y) ]
                    Polyline(*pts)
                    offset(amount=self.keyplate_dims.connector_width, side=Side.BOTH)
                make_face()

                l = Line(self.keys.thumb.locs[0]+ (Choc.pins.pin2_x, -Choc.pins.pin2_y), self.keys.thumb.locs[1]+ (Choc.pins.pin2_x, -Choc.pins.pin2_y))
                offset(l, amount=self.keyplate_dims.connector_width/2, side=Side.BOTH)
                make_face()
                l = Line(self.keys.thumb.locs[0]+ (Choc.pins.pin2_x, Choc.pins.pin2_y), self.keys.thumb.locs[1]+ (Choc.pins.pin2_x, Choc.pins.pin2_y))
                offset(l, amount=self.keyplate_dims.connector_width/2, side=Side.BOTH)
                make_face()
                for t in self.keys.thumb.locs:
                    l = Line(t, self.keys.inner.locs[0])
                    offset(l, amount=self.keyplate_dims.connector_width/2, side=Side.BOTH)
                    make_face()

            extrude(amount=self.keyplate_dims.connector_depth_z, mode=Mode.SUBTRACT)
            self.debug_content.append({"connector_sketch": connector_sketch}) if self.debug else None

            if with_topline:
                with BuildSketch(Plane.XY.offset(-self.keyplate_dims.size_z+self.bottom_dims.size_z)) as connector_holder:
                    with Locations(
                        self.keys.middle.locs[2] + (0, Choc.cap.length_y/2 + self.keyplate_dims.connector_width/2),
                        self.keys.middle.locs[2] + (-25, Choc.cap.length_y/2 -self.keyplate_dims.connector_width/2),
                        self.keys.middle.locs[2] + (25, Choc.cap.length_y/2 -self.keyplate_dims.connector_width/2),
                        ):
                        RectangleRounded(10, 1.5*self.keyplate_dims.connector_width, radius=0.5*self.keyplate_dims.connector_width)
                extrude(amount=0.25, mode=Mode.ADD)
                self.debug_content.append({"connector_holder": connector_holder}) if self.debug else None

            with BuildSketch(Plane.XY.offset(-self.keyplate_dims.size_z+self.bottom_dims.size_z)): 
                with Locations(self.keyplate_dims.bottom_holder_locations()):
                    Circle(self.keyplate_dims.bottom_holder_radius -1)
            bumpers = extrude(amount=-self.bottom_dims.size_z, mode=Mode.ADD)
            with BuildSketch([s.faces().sort_by(Axis.Z)[0] for s in bumpers.solids()]) as bumper_cut:
                Circle(self.keyplate_dims.bottom_holder_radius)
            bottom_holders = extrude(amount=-0.75, mode=Mode.ADD)
            fillet(bottom_holders.edges(), radius=0.3)
            with BuildSketch([s.faces().sort_by(Axis.Z)[0] for s in bottom_holders.solids()]) as bumper_cut:
                Circle(self.keyplate_dims.rubber_bumper_radius)
            extrude(amount=-1, mode=Mode.SUBTRACT)

        return keyplate.part
    
    def create_keywell(self):
        print("Creating keywell...")

        with BuildPart() as keywell:
            with BuildSketch():
                add(self.outline.sketch)
            extrude(amount=self.keywell_dims.size_z)

            if self.with_knurl: 
                print("Adding knurl...")
                tops = keywell.faces().filter_by(Axis.Z)
                walls = keywell.faces().filter_by(lambda f: f not in tops).sort_by(Axis.X, reverse=True)
                self.knurl.patternize(walls + [tops[-1]], pattern_depth=self.dims.pattern_depth, distance=self.dims.pattern_size)

            with BuildSketch() as key_holes:
                for keycol in self.keys.finger_cols:
                    with Locations(keycol.locs):
                        Rectangle(Choc.cap.width_x +1, Choc.cap.length_y + 1, rotation=keycol.rotation)
                with Locations(self.keys.thumb.locs[0]):
                    Rectangle(Choc.cap.width_x+2, Choc.cap.length_y + 11, rotation=self.keys.thumb.rotation)
                with Locations(self.keys.thumb.locs[1]):
                    Rectangle(Choc.cap.width_x+4, Choc.cap.length_y + 5, rotation=self.keys.thumb.rotation)

            self.debug_content.append({"key_holes (keywell)": key_holes}) if self.debug else None
            extrude(amount=self.keywell_dims.size_z, mode=Mode.SUBTRACT)


        return keywell.part

    def create_bottom(self):
        print("Creating bottom...")

        with BuildPart() as bottom:
            with BuildSketch(Plane.XY.offset(-self.keyplate_dims.size_z)):
                offset(self.outline.sketch, -self.bottom_dims.keyplate_offset, kind=Kind.INTERSECTION)
            extrude(amount=self.bottom_dims.size_z)

            if self.with_knurl: 
                print("Adding knurl...")
                bottom_face = bottom.faces().sort_by(Axis.Z)[0]
                self.knurl.patternize([bottom_face], pattern_depth=self.dims.pattern_depth, distance=self.dims.pattern_size)

            with BuildSketch(Plane.XY.offset(-self.keyplate_dims.size_z)): 
                with Locations(self.keyplate_dims.bottom_holder_locations()):
                    Circle(self.keyplate_dims.bottom_holder_radius - 2 + 2*self.dims.clearance)
            extrude(amount=self.bottom_dims.size_z + 0.1, mode=Mode.SUBTRACT)

            with BuildSketch(Plane.XY.offset(-self.keyplate_dims.size_z)): 
                with Locations(self.keyplate_dims.bottom_holder_locations()):
                    Circle(self.keyplate_dims.bottom_holder_radius + 2*self.dims.clearance)
            extrude(amount=1, mode=Mode.SUBTRACT)
        return bottom.part



    def create_accessories(self):
        if not self.debug:
            return
        
        choc = Choc()
        with BuildPart() as self.chocs:
            self.chocs.name = "Choc Switches"

            for keycol in self.keys.keycols:
                with Locations(keycol.locs):
                    add(copy.copy(choc.model.part).rotate(Axis.Z, keycol.rotation))
        self.chocs = self.chocs.part + mirror(self.chocs.part, about=Plane.YZ)
        push_object(self.chocs, name="chocs")

        xiao = self.xiao.model\
            .rotate(Axis.X, 180)\
            .translate(self.keyplate_dims.xiao_position)
        xiao = xiao + mirror(xiao, about=Plane.YZ)
        push_object(xiao, name="xiao")

            

if __name__ == "__main__":
    set_port(3939)
    show_clear()
    set_defaults(ortho=True, default_edgecolor="#121212", reset_camera=Camera.KEEP)
    set_colormap(ColorMap.seeded(colormap="rgb", alpha=1, seed_value="wave"))

    knurl = False
    case = DualityWaveCase(with_knurl=knurl, debug=True)

    show_objects() 