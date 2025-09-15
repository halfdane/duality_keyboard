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

@dataclass
class BottomDimensions:
    size_z: float = 1.3
    keyplate_offset: float = 2

@dataclass
class KeyplateDimensions:
    size_z: float = Choc.bottom_housing.height_z + Choc.posts.post_height_z + BottomDimensions.size_z
    switch_clamp_clearance: float = size_z - Choc.clamps.clearance_z

    xiao_offset: float = BottomDimensions.keyplate_offset
    xiao_pos_x: float = xiao_offset + Xiao.board.width_x/2
    xiao_pos_y: float = Outline.dims.base_length_y - Xiao.board.depth_y/2 - xiao_offset
    xiao_pos_z: float = -(Choc.bottom_housing.height_z + Choc.posts.post_height_z - Xiao.board.thickness_z - Xiao.usb.height_z)
    xiao_position: Location = (xiao_pos_x, xiao_pos_y, xiao_pos_z)
    xiao_mirror_position: Location = (-xiao_pos_x, xiao_pos_y, xiao_pos_z)

    connector_width: float = 2
    connector_depth_z: float = Choc.posts.post_height_z

@dataclass
class KeywellDimensions:
    size_z: float = Choc.base.thickness_z + Choc.upper_housing.height_z + Choc.stem.height_z + Choc.cap.height_z + CaseDimensions.pattern_depth

class DualityWaveCase:
    dims = CaseDimensions()
    bottom_dims = BottomDimensions()
    keyplate_dims = KeyplateDimensions()
    keywell_dims = KeywellDimensions()
    outline = Outline()
    keys = Keys(outline.dims.switch_offset)

    xiao = Xiao()

    def __init__(self, with_knurl=False, debug=False):
        self.with_knurl = with_knurl
        self.debug = debug
        if self.with_knurl:
            self.knurl = Knurl(debug=debug)

        self.keyplate_left = self.create_keyplate()
        self.keyplate_right = mirror(self.keyplate_left, about=Plane.YZ)

        usb_cut = self.xiao.create_usb_cut(self.dims.clearance)
        self.keyplate_left = self.keyplate_left - usb_cut.translate(self.keyplate_dims.xiao_position)
        self.keyplate_right = self.keyplate_right - usb_cut.translate(self.keyplate_dims.xiao_mirror_position)

        push_object(self.keyplate_left, name="keyplate_left") if self.debug else None
        push_object(self.keyplate_right, name="keyplate_right") if self.debug else None

        self.keywell_left = self.create_keywell()
        self.keywell_right = mirror(self.keywell_left, about=Plane.YZ)
        push_object(self.keywell_left, name="keywell_left") if self.debug else None
        push_object(self.keywell_right, name="keywell_right") if self.debug else None

        self.bottom_left = self.create_bottom()
        self.bottom_right = mirror(self.bottom_left, about=Plane.YZ)
        push_object(self.bottom_left, name="bottom_left") if self.debug else None
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
                self.knurl.patternize(walls, pattern_depth=self.dims.pattern_depth, distance=1.5 if not self.debug else 10)

            with BuildSketch(Plane.XY.offset(-self.keyplate_dims.size_z)) as bottom_walls:
                offset(self.outline.sketch, -self.bottom_dims.keyplate_offset, kind=Kind.INTERSECTION)
            extrude(amount=self.bottom_dims.size_z, mode=Mode.SUBTRACT)
            push_object(bottom_walls, name="bottom_walls") if self.debug else None

            with BuildSketch() as key_holes:
                for keycol in self.keys.keycols:
                    with Locations(keycol.locs):
                        Rectangle(Choc.bottom_housing.width_x, Choc.bottom_housing.depth_y, rotation=keycol.rotation)
            push_object(key_holes, name="key_holes") if self.debug else None
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


            with BuildSketch() as connector_sketch:
                top_y = self.keys.middle.locs[2].Y+Choc.cap.length_y/2

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

                for col in [self.keys.pointer, self.keys.middle, self.keys.ring]:
                    column_to_topline = Line(col.locs[0], (col.locs[0].X, top_y))
                    offset(column_to_topline, amount=self.keyplate_dims.connector_width/2, side=Side.BOTH)
                    make_face()
                
                with BuildLine() as pinkie_to_topline:
                    pts = [ self.keys.pinkie.locs[0], self.keys.pinkie.locs[2], (self.keys.pinkie.locs[2].X, top_y) ]
                    Polyline(*pts)
                    offset(amount=self.keyplate_dims.connector_width/2, side=Side.BOTH)
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

            connector_sketch = connector_sketch.sketch \
                .translate((0,0, -self.keyplate_dims.size_z + self.bottom_dims.size_z))
            extrude(to_extrude=connector_sketch, amount=self.keyplate_dims.connector_depth_z, mode=Mode.SUBTRACT)
            push_object(connector_sketch, name="connector_sketch") if self.debug else None

            with BuildSketch(Plane.XY.offset(-self.keyplate_dims.size_z+self.bottom_dims.size_z)) as connector_holder1:
                with Locations(
                    self.keys.middle.locs[2] + (0, Choc.cap.length_y/2 + self.keyplate_dims.connector_width/2),
                    self.keys.middle.locs[2] + (-25, Choc.cap.length_y/2 -self.keyplate_dims.connector_width/2),
                    self.keys.middle.locs[2] + (25, Choc.cap.length_y/2 -self.keyplate_dims.connector_width/2),
                    ):
                    RectangleRounded(10, 1.5*self.keyplate_dims.connector_width, radius=0.5*self.keyplate_dims.connector_width)
            extrude(to_extrude=connector_holder1.sketch, amount=0.25, mode=Mode.ADD)
            push_object(connector_holder1, name="connector_holder1") if self.debug else None
        
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
                self.knurl.patternize(walls, pattern_depth=self.dims.pattern_depth, distance=1.5 if not self.debug else 10)
            
            with BuildSketch() as key_holes:
                for keycol in self.keys.finger_cols:
                    with Locations(keycol.locs):
                        Rectangle(Choc.cap.width_x +1, Choc.cap.length_y + 1, rotation=keycol.rotation)
                with Locations(self.keys.thumb.locs):
                    with Locations((1,0)):
                        Rectangle(Choc.cap.width_x+4, Choc.cap.length_y + 11, rotation=self.keys.thumb.rotation)
            push_object(key_holes, name="key_holes2") if self.debug else None
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
                self.knurl.patternize([bottom_face], pattern_depth=self.dims.pattern_depth, distance=1.5 if not self.debug else 10)
            
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

    knurl = True
    case = DualityWaveCase(with_knurl=knurl, debug=True)

    show_objects() 