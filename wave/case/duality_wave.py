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
    keyplate_offset: float = 1.8

    ribs_xy: float = 2
    ribs_z: float = 1.5

@dataclass
class KeyplateDimensions:
    keys: Keys
    outline: Outline

    size_z: float = Choc.bottom_housing.height_z + Choc.posts.post_height_z + BottomDimensions.size_z
    switch_clamp_clearance: float = size_z - Choc.clamps.clearance_z

    xiao_offset: float = BottomDimensions.keyplate_offset + BottomDimensions.ribs_xy
    xiao_pos_x: float = 10 + Xiao.board.width_x/2
    xiao_pos_y: float = Outline.dims.base_length_y - Xiao.board.depth_y/2 - xiao_offset
    xiao_pos_z: float = -(Choc.bottom_housing.height_z + Choc.posts.post_height_z - Xiao.board.thickness_z - Xiao.usb.height_z)
    xiao_position: Location = (xiao_pos_x, xiao_pos_y, xiao_pos_z)
    xiao_mirror_position: Location = (-xiao_pos_x, xiao_pos_y, xiao_pos_z)

    connector_width: float = 2
    connector_depth_z: float = Choc.posts.post_height_z

    rubber_bumper_height_z: float = 1
    rubber_bumper_radius: float = 4
    bottom_holder_radius: float = rubber_bumper_radius+1
    bottom_holder_height_z: float = 0.5
    bottom_holder_deflect: float = 0.2

    def bumper_holder_locations(self) -> list[Vector]:
        return [
            Vector(self.outline.dims.base_width_x, self.outline.dims.base_length_y) - Vector(self.rubber_bumper_radius, self.rubber_bumper_radius) + Vector(-2, -2)*2,
            Vector(0, 0) + Vector(self.rubber_bumper_radius, self.rubber_bumper_radius) + Vector(2, 2)*2,
            Vector(0, self.outline.dims.base_length_y) + Vector(self.rubber_bumper_radius, -self.rubber_bumper_radius) + Vector(2, -2)*2,
        ]
    
    def bottom_holder_locations(self) -> list[Vector]:
        return [
            (self.keys.pointer.locs[1] + self.keys.middle.locs[0]) / 2-(0, 2),
            (self.keys.thumb.locs[0] + self.keys.thumb.locs[1]) / 2 + (-0.5, Choc.cap.length_y/2),
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

        usb_cut = self.xiao.create_usb_cut(2*self.dims.clearance)
        usb_cut_for_bottom = self.xiao.create_usb_cut(6*self.dims.clearance)
        push_object(usb_cut.translate(self.keyplate_dims.xiao_position), name="usb_cut") if self.debug else None

        self.keyplate_left = self.create_keyplate()
        self.keyplate_left = self.keyplate_left - usb_cut.translate(self.keyplate_dims.xiao_position)
        push_object(self.keyplate_left, name="keyplate_left") if self.debug else None
        self.keywell_left = self.create_keywell()
        push_object(self.keywell_left, name="keywell_left") if self.debug else None
        self.bottom_left = self.create_bottom()
        self.bottom_left = self.bottom_left - usb_cut_for_bottom.translate(self.keyplate_dims.xiao_position)
        push_object(self.bottom_left, name="bottom_left") if self.debug else None


        # self.keyplate_right = mirror(self.keyplate_left, about=Plane.YZ)
        # self.keyplate_right = self.keyplate_right - usb_cut.translate(self.keyplate_dims.xiao_mirror_position)
        # self.keywell_right = mirror(self.keywell_left, about=Plane.YZ)
        # self.bottom_right = mirror(self.bottom_left, about=Plane.YZ)
        # self.bottom_right = self.bottom_right - usb_cut_for_bottom.translate(self.keyplate_dims.xiao_mirror_position)
        # push_object(self.keyplate_right, name="keyplate_right") if self.debug else None
        # push_object(self.keywell_right, name="keywell_right") if self.debug else None
        # push_object(self.bottom_right, name="bottom_right") if self.debug else None

        self.create_accessories()


    def create_keyplate(self):
        print("Creating keyplate...")

        with BuildPart() as keyplate:
            with BuildSketch() as base:
                add(self.outline.sketch)
            extrude(amount=self.keyplate_dims.size_z)
            keyplate.part = keyplate.part.translate((0,0,-self.keyplate_dims.size_z))
            fillet(objects=keyplate.faces().sort_by(Axis.Z)[0].edges(), radius=1)
            self.debug_content.append({"base": base}) if self.debug else None

            if self.with_knurl:
                print("Adding knurl...")
                tops = keyplate.faces().filter_by(Axis.Z)
                walls = keyplate.faces().filter_by(lambda f: f not in tops).sort_by(Axis.X, reverse=True)
                self.knurl.patternize(walls + [tops[0]], pattern_depth=self.dims.pattern_depth, distance=self.dims.pattern_size)

            add(self.create_bottom_outline(self.dims.clearance))
            extrude(amount=self.bottom_dims.size_z + self.bottom_dims.ribs_z + self.dims.clearance, mode=Mode.SUBTRACT)

            add(self.create_bottom_wall(self.dims.clearance))
            extrude(amount=self.keyplate_dims.size_z - self.bottom_dims.size_z - Choc.clamps.clearance_z  + self.dims.clearance, mode=Mode.SUBTRACT)
            fillet(objects=keyplate.faces().filter_by(Axis.Z).group_by(Axis.Z)[1].edges() 
                   + keyplate.faces().filter_by(Axis.Z).group_by(Axis.Z)[2].edges(), 
                   radius=self.bottom_dims.ribs_z/4 - self.dims.clearance)

            with BuildSketch() as key_holes:
                for keycol in self.keys.keycols:
                    with Locations(keycol.locs):
                        Rectangle(Choc.bottom_housing.width_x, Choc.bottom_housing.depth_y, rotation=keycol.rotation)
            self.debug_content.append({"key_holes (keyplate)": key_holes}) if self.debug else None
            extrude(amount=-Choc.clamps.clearance_z, mode=Mode.SUBTRACT)
            with BuildSketch(Plane.XY.offset(-Choc.clamps.clearance_z)) as keyholes_with_space:
                offset(key_holes.sketch, 1)
            extrude(amount=-self.keyplate_dims.size_z, mode=Mode.SUBTRACT)

            ribs_sketch = self.create_bottom_ribs_sketch()
            extrude(to_extrude=ribs_sketch, amount=self.bottom_dims.ribs_z, mode=Mode.SUBTRACT)

            with BuildSketch(Plane(self.keyplate_dims.xiao_position)) as xiao_hole:
                Rectangle(Xiao.board.width_x - 1.5, Xiao.board.depth_y - 1.5)
            extrude(amount=self.keyplate_dims.size_z, mode=Mode.SUBTRACT)
            with BuildSketch(Plane(self.keyplate_dims.xiao_position)) as xiao_cut:
                Rectangle(Xiao.board.width_x + 2*self.dims.clearance, Xiao.board.depth_y + 2*self.dims.clearance)
            extrude(amount=-self.keyplate_dims.size_z, mode=Mode.SUBTRACT)

            with_topline = False
            connector_sketch = self.create_connector_sketch(with_topline=with_topline)
            extrude(to_extrude=connector_sketch, amount=self.keyplate_dims.connector_depth_z, mode=Mode.SUBTRACT)

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

            with BuildSketch(Plane.XY.offset(-self.keyplate_dims.size_z+self.bottom_dims.size_z+self.bottom_dims.ribs_z)) as bumper_holder_sketch:
                with Locations(self.keyplate_dims.bumper_holder_locations()):
                    Circle(self.keyplate_dims.rubber_bumper_radius)
            extrude(amount=-self.bottom_dims.size_z-self.bottom_dims.ribs_z + self.keyplate_dims.rubber_bumper_height_z)

            with BuildSketch(Plane.XY.offset(-self.keyplate_dims.size_z+self.bottom_dims.size_z+self.bottom_dims.ribs_z)) as bottom_holder_sketch:
                with Locations(self.keyplate_dims.bottom_holder_locations()):
                    Circle(self.keyplate_dims.rubber_bumper_radius)
            extrude(amount=-self.bottom_dims.size_z-self.bottom_dims.ribs_z + self.keyplate_dims.rubber_bumper_height_z)
            chamfer(keyplate.edges(Select.LAST).group_by(Axis.Z)[-1], length=0.5)
            extrude(to_extrude=offset(bottom_holder_sketch.sketch, amount=-0.5, mode=Mode.PRIVATE), amount=1.8, taper=60)

            with BuildSketch(Plane.XY.offset(-self.keyplate_dims.size_z+self.keyplate_dims.rubber_bumper_height_z+self.keyplate_dims.bottom_holder_height_z)):
                with Locations(self.keyplate_dims.bottom_holder_locations()):
                    Circle(self.keyplate_dims.bottom_holder_radius)
                    Circle(self.keyplate_dims.rubber_bumper_radius, mode=Mode.SUBTRACT)
            bottom_holder = extrude(amount=-self.keyplate_dims.rubber_bumper_height_z-self.keyplate_dims.bottom_holder_height_z)
        
            chamfer(bottom_holder.edges().group_by(Edge.length)[-1], length=0.5)
            fillet(keyplate.edges(Select.LAST).edges().filter_by(GeomType.CIRCLE).group_by(Edge.length)[-1],
                   radius=self.keyplate_dims.bottom_holder_deflect/2)

            with BuildSketch(Plane.XY.offset(-self.keyplate_dims.size_z)):
                with Locations(self.keyplate_dims.bottom_holder_locations()):
                    Rectangle(10, 1)
                    Rectangle(1, 10)
            extrude(amount=self.bottom_dims.size_z + self.bottom_dims.ribs_z, mode=Mode.SUBTRACT)


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
    
    def create_bottom_outline(self, clearance = 0):
        print("Creating bottom outline...")

        with BuildSketch(Plane.XY.offset(-self.keyplate_dims.size_z)) as bottom_outline:
            offset(self.outline.sketch, -self.bottom_dims.keyplate_offset + clearance, kind=Kind.INTERSECTION)
            fillet(bottom_outline.vertices(), radius=1)

        return bottom_outline.sketch

    def create_bottom_wall(self, clearance = 0):
        print("Creating bottom wall...")

        with BuildSketch(Plane.XY.offset(-self.keyplate_dims.size_z+self.bottom_dims.size_z)) as bottom_wall:
            add(self.create_bottom_outline(clearance))
            offset(self.outline.sketch, -self.bottom_dims.keyplate_offset - self.bottom_dims.ribs_xy - clearance, kind=Kind.INTERSECTION, mode=Mode.SUBTRACT)
            fillet(bottom_wall.vertices(), radius=1)
        return bottom_wall.sketch

    def create_bottom(self):
        print("Creating bottom...")

        with BuildPart() as bottom:
            add(self.create_bottom_outline())
            extrude(amount=self.bottom_dims.size_z)

            add(self.create_bottom_wall())
            extrude(amount=self.keyplate_dims.size_z - self.bottom_dims.size_z - Choc.clamps.clearance_z)
            fillet(objects=bottom.faces().group_by(Axis.Z)[-1].edges()
                   + bottom.faces().group_by(Axis.Z)[1].edges(), 
                   radius=self.bottom_dims.ribs_z/2 - self.dims.clearance)

            ribs_sketch = self.create_bottom_ribs_sketch()
            ribs_sketch = offset(objects=ribs_sketch, amount=-2*self.dims.clearance, mode=Mode.PRIVATE)
            extrude(to_extrude=ribs_sketch, amount=self.bottom_dims.ribs_z, mode=Mode.ADD)

            with BuildSketch(Plane.XY.offset(-self.keyplate_dims.size_z)): 
                with Locations(self.keyplate_dims.bottom_holder_locations() + self.keyplate_dims.bumper_holder_locations()):
                    Circle(self.keyplate_dims.rubber_bumper_radius + 2*self.dims.clearance)
            extrude(amount=self.bottom_dims.size_z+self.bottom_dims.ribs_z, mode=Mode.SUBTRACT)

            with BuildSketch(Plane.XY.offset(-self.keyplate_dims.size_z+self.keyplate_dims.rubber_bumper_height_z)): 
                with Locations(self.keyplate_dims.bottom_holder_locations()):
                    Circle(self.keyplate_dims.bottom_holder_radius - self.keyplate_dims.bottom_holder_deflect)
            bottom_holder_cut1 = extrude(amount=self.bottom_dims.size_z+self.bottom_dims.ribs_z-self.keyplate_dims.rubber_bumper_height_z, mode=Mode.SUBTRACT)

            with BuildSketch(Plane.XY.offset(-self.keyplate_dims.size_z)): 
                with Locations(self.keyplate_dims.bottom_holder_locations()):
                    Circle(self.keyplate_dims.bottom_holder_radius + self.dims.clearance)
            extrude(amount=self.keyplate_dims.rubber_bumper_height_z + self.dims.clearance, mode=Mode.SUBTRACT)
            chamfer(
                bottom.edges(Select.LAST).edges().filter_by(GeomType.CIRCLE).group_by(Edge.length)[0]
                + bottom_holder_cut1.edges().group_by(Axis.Z)[-1],
                length=self.keyplate_dims.bottom_holder_deflect)
            fillet(bottom.edges(Select.LAST).edges().filter_by(GeomType.CIRCLE).group_by(Edge.length)[0],
                   radius=self.keyplate_dims.bottom_holder_deflect/2)

        return bottom.part

    def create_connector_sketch(self, with_topline=True):
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
        
        self.debug_content.append({"connector_sketch": connector_sketch}) if self.debug else None
        return connector_sketch.sketch            


    def create_bottom_ribs_sketch(self):
        with BuildSketch(Plane.XY.offset(-self.keyplate_dims.size_z+self.bottom_dims.size_z)) as bottom_ribs:
            for keycol in [self.keys.pinkie, self.keys.pointer, self.keys.middle, self.keys.ring]:
                with BuildSketch(Plane.XY.rotated((0,0,keycol.rotation)), mode=Mode.PRIVATE) as col:
                    Rectangle(Choc.cap.width_x+2, 3*Choc.cap.length_y+self.bottom_dims.ribs_xy/2)
                add(col.sketch.translate(keycol.locs[1]))
            for keycol in [self.keys.pinkie, self.keys.pointer, self.keys.middle, self.keys.ring]:
                with BuildSketch(Plane.XY.rotated((0,0,keycol.rotation)), mode=Mode.PRIVATE) as col:
                    Rectangle(Choc.bottom_housing.width_x+2, 3*Choc.cap.length_y - self.bottom_dims.ribs_xy)
                add(col.sketch.translate(keycol.locs[1]), mode=Mode.SUBTRACT)
            for keycol in [self.keys.pinkie, self.keys.pointer, self.keys.middle, self.keys.ring]:
                with BuildSketch(Plane.XY.rotated((0,0,keycol.rotation)), mode=Mode.PRIVATE) as col:
                    with Locations((0,-Choc.cap.length_y/2), (0,Choc.cap.length_y/2)):
                        Rectangle(Choc.cap.width_x, self.bottom_dims.ribs_xy)
                add(col.sketch.translate(keycol.locs[1]))

            # there's a weird gap between lower pinkie and the outline, that wants to be filled
            with BuildSketch(Plane.XY, mode=Mode.PRIVATE) as col:
                a = Vector(24.5,4)
                b = Vector(31,5.5)
                c = Vector(31,4)
                Triangle(a=(b-a).length*2, b=(c-b).length*2, c=(a-c).length*2)
            add(col.sketch.translate(self.keys.pinkie.locs[0] + (5, -Choc.cap.length_y/2)))

            with Locations(self.keys.inner.locs):
                with Locations((-1, 0)):
                    Rectangle(Choc.bottom_housing.width_x +4, Choc.bottom_housing.depth_y + 4, rotation=self.keys.inner.rotation)
                with Locations((-0.5, 0)):
                    Rectangle(Choc.bottom_housing.width_x+1, Choc.bottom_housing.depth_y, rotation=self.keys.inner.rotation, mode=Mode.SUBTRACT)
            
            keycol = self.keys.thumb
            with BuildSketch(Plane.XY.rotated((0,0,keycol.rotation)), mode=Mode.PRIVATE) as col:
                Rectangle(2*Choc.cap.width_x, self.bottom_dims.ribs_xy)
            add(col.sketch.translate((keycol.locs[1] + keycol.locs[0])/2 + (0, Choc.cap.length_y/2)))

            with BuildSketch(Plane.XY):
                with Locations(self.keyplate_dims.bottom_holder_locations()):
                    Circle(self.keyplate_dims.bottom_holder_radius+1.2)

        self.debug_content.append({"bottom_ribs": bottom_ribs}) if self.debug else None        
        return bottom_ribs.sketch

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
    knurl = False
    case = DualityWaveCase(with_knurl=knurl, debug=True)
    show_clear()
    set_defaults(ortho=True, default_edgecolor="#121212", reset_camera=Camera.KEEP)
    set_colormap(ColorMap.seeded(colormap="rgb", alpha=1, seed_value="wave"))
    show_objects() 