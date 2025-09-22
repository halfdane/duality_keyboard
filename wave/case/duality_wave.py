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
from models.rubber_bumper import RubberBumper, BumperDimensions

from ocp_vscode import *


@dataclass
class BottomDimensions:
    size_z: float = 1.3
    keyplate_offset: float = 1.8

    ribs_xy: float = 2
    ribs_z: float = 1.5

@dataclass
class KeyplateDimensions:
    size_z: float = Choc.bottom_housing.height_z + Choc.posts.post_height_z + BottomDimensions.size_z
    switch_clamp_clearance: float = size_z - Choc.clamps.clearance_z

    connector_width: float = 2
    connector_depth_z: float = Choc.posts.post_height_z

    clip_position_z: float = 0.6*(size_z - Choc.clamps.clearance_z)
    clip_xy: float = 0.4
    clip_z: float = 1

@dataclass
class BumperHolderDimensions:
    keys: Keys
    outline: Outline

    radius: float = BumperDimensions.radius+1
    height_z: float = 0.5
    deflect: float = 0.4

    def bumper_locations(self) -> list[Vector]:
        o_dims = self.outline.dims
        radius = BumperDimensions.radius
        return [
            (self.keys.thumb.locs[0] + self.keys.thumb.locs[1])/2 + (-0.5, -Choc.cap.length_y/4+1.1),
            Vector(o_dims.base_width_x, o_dims.base_length_y) - Vector(radius, radius) + Vector(-2, -2)*2,
            Vector(0, 0) + Vector(radius, radius) + Vector(2, 2)*2,
            Vector(0, o_dims.base_length_y) + Vector(radius, -radius) + Vector(2, -2)*2,
        ]
    
    def bottom_holder_locations(self) -> list[Vector]:
        return [
            (self.keys.pointer.locs[1] + self.keys.middle.locs[0]) / 2 + (0, -2),
        ]


@dataclass
class CaseDimensions:
    clearance: float = 0.02
    pin_radius: float = 0.5    

    xiao_offset: float = BottomDimensions.keyplate_offset + BottomDimensions.ribs_xy
    xiao_pos_x: float = 10 + Xiao.board.width_x/2
    xiao_pos_y: float = Outline.dims.base_length_y - Xiao.board.depth_y/2 - xiao_offset
    xiao_pos_z: float = -(Choc.bottom_housing.height_z + Choc.posts.post_height_z - Xiao.board.thickness_z - Xiao.usb.height_z)
    xiao_position: Location = (xiao_pos_x, xiao_pos_y, xiao_pos_z)
    xiao_mirror_position: Location = (-xiao_pos_x, xiao_pos_y, xiao_pos_z)


@dataclass
class KeywellDimensions:
    size_z: float = Choc.base.thickness_z + Choc.upper_housing.height_z + Choc.stem.height_z + Choc.cap.height_z

class DualityWaveCase:
    outline = Outline()
    keys = Keys()

    dims = CaseDimensions()
    keywell_dims = KeywellDimensions()
    keyplate_dims = KeyplateDimensions()
    bottom_dims = BottomDimensions()

    bumperholder_dims = BumperHolderDimensions(keys, outline)

    xiao = Xiao()
    bumper = RubberBumper()

    debug_content: list = []

    def __init__(self, debug=False, both_sides=False):
        print("Creating case...")

        self.debug = debug

        push_object(self.debug_content, name="debug_content") if self.debug else None

        self.create_accessories()

        usb_cut = self.xiao.create_usb_cut(2*self.dims.clearance).translate(self.dims.xiao_position)
        usb_cut_for_bottom = self.xiao.create_usb_cut(6*self.dims.clearance).translate(self.dims.xiao_position)
        self.debug_content.append({"usb_cut": usb_cut}) if self.debug else None

        self.keywell_left = self.create_keywell()
        push_object(self.keywell_left, name="keywell_left") if self.debug else None

        self.keyplate_left = self.create_keyplate()# - usb_cut
        push_object(self.keyplate_left, name="keyplate_left") if self.debug else None

        self.bottom_left = self.create_bottom() - usb_cut_for_bottom
        push_object(self.bottom_left, name="bottom_left") if self.debug else None

        push_object(self.chocs, name="chocs")
        push_object(self.xiao.model, name="xiao")
        push_object(self.bumpers, name="bumpers")

        if both_sides:
            self.keywell_right = mirror(self.keywell_left, about=Plane.YZ)
            push_object(self.keywell_right, name="keywell_right") if self.debug else None

            self.keyplate_right = mirror(self.keyplate_left, about=Plane.YZ) - usb_cut.translate(self.dims.xiao_mirror_position)
            push_object(self.keyplate_right, name="keyplate_right") if self.debug else None

            self.bottom_right = mirror(self.bottom_left, about=Plane.YZ) - usb_cut_for_bottom.translate(self.dims.xiao_mirror_position)
            push_object(self.bottom_right, name="bottom_right") if self.debug else None

            push_object(mirror(self.chocs, about=Plane.YZ), name="chocs") if self.debug else None
            push_object(self.xiao.model.translate(self.dims.xiao_mirror_position), name="xiao")
        print("Done creating case.")

    def create_keyplate(self):
        print("Creating keyplate...")

        with BuildPart() as keyplate:
            with BuildSketch() as base:
                add(self.outline.sketch)
            extrude(amount=self.keyplate_dims.size_z)
            keyplate.part = keyplate.part.translate((0,0,-self.keyplate_dims.size_z))
            fillet(objects=keyplate.faces().sort_by(Axis.Z)[0].edges(), radius=1)
            self.debug_content.append({"base": base}) if self.debug else None

            bottom_outline = self.create_bottom_outline(self.dims.clearance)
            add(bottom_outline)
            extrude(amount=self.bottom_dims.size_z, mode=Mode.SUBTRACT)
            add(offset(bottom_outline, amount=-2.5*self.bottom_dims.keyplate_offset, mode=Mode.PRIVATE))
            extrude(amount=self.bottom_dims.size_z + self.bottom_dims.ribs_z, mode=Mode.SUBTRACT)

            # inner wall
            add(self.create_bottom_wall(self.dims.clearance, 4*self.dims.clearance))
            extrude(amount=self.keyplate_dims.size_z - self.bottom_dims.size_z - Choc.clamps.clearance_z  + self.dims.clearance, mode=Mode.SUBTRACT)
            fillet(objects=keyplate.faces().filter_by(Axis.Z).group_by(Axis.Z)[-4].edges()
                   + keyplate.faces().filter_by(Axis.Z).group_by(Axis.Z)[-2].edges(), 
                   radius=self.bottom_dims.ribs_z/2 - self.dims.clearance)

            bottom_clips = self.create_bottom_clips(bottom_outline, outward_facing=False, camera_position=keyplate.part.center())
            bottom_clips = bottom_clips.translate((0,0, 1*self.dims.clearance))
            add(bottom_clips)

            print("  key holes...")
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

            print("  xiao hole...")
            with BuildSketch(Plane(self.dims.xiao_position)) as xiao_hole:
                Rectangle(Xiao.board.width_x - 1.5, Xiao.board.depth_y - 1.5)
            extrude(amount=self.keyplate_dims.size_z, mode=Mode.SUBTRACT)
            with BuildSketch(Plane(self.dims.xiao_position)) as xiao_cut:
                Rectangle(Xiao.board.width_x + 2*self.dims.clearance, Xiao.board.depth_y + 2*self.dims.clearance)
            extrude(amount=-self.keyplate_dims.size_z, mode=Mode.SUBTRACT)

            print("  connector cut...")
            connector_sketch = self.create_connector_sketch()
            extrude(to_extrude=connector_sketch, amount=self.keyplate_dims.connector_depth_z, mode=Mode.SUBTRACT)

            print("  bumpers...")
            with BuildPart() as bumper_holder:
                with BuildSketch(Plane.XY.offset(-self.keyplate_dims.size_z+self.bottom_dims.size_z+self.bottom_dims.ribs_z)) as bumper_holder_sketch:
                    with Locations(self.bumperholder_dims.bumper_locations()):
                        Circle(self.bumper.dims.radius)
                extrude(amount=-self.bottom_dims.size_z-self.bottom_dims.ribs_z + self.bumper.dims.base_z)

                with BuildSketch(Plane.XY.offset(-self.keyplate_dims.size_z+self.bottom_dims.size_z+self.bottom_dims.ribs_z)) as bottom_holder_sketch:
                    with Locations(self.bumperholder_dims.bottom_holder_locations()):
                        Circle(self.bumperholder_dims.radius - 1.5*self.bumperholder_dims.deflect)
                extrude(amount=-self.bottom_dims.size_z-self.bottom_dims.ribs_z + self.bumper.dims.base_z)
                chamfer(edges(Select.LAST).group_by(Axis.Z)[-1], length=0.5 - self.dims.clearance)
                extrude(to_extrude=offset(bottom_holder_sketch.sketch, amount=-0.5, mode=Mode.PRIVATE), amount=1.8, taper=60)

                with BuildSketch(Plane.XY.offset(-self.keyplate_dims.size_z+self.bumper.dims.base_z+self.bumperholder_dims.height_z)):
                    with Locations(self.bumperholder_dims.bottom_holder_locations()):
                        Circle(self.bumperholder_dims.radius)
                        Circle(self.bumper.dims.radius, mode=Mode.SUBTRACT)
                extrude(amount=-self.bumper.dims.base_z-self.bumperholder_dims.height_z)
            
                chamfer(edges(Select.LAST).group_by(Edge.length)[-1], length=0.5)
                fillet(edges(Select.LAST).edges().filter_by(GeomType.CIRCLE).group_by(Edge.length)[-1],
                    radius=self.bumperholder_dims.deflect/2)

                with BuildSketch(Plane.XY.offset(-self.keyplate_dims.size_z)):
                    with Locations(self.bumperholder_dims.bottom_holder_locations()):
                        Rectangle(10, 1)
                        Rectangle(1, 10)
                extrude(amount=self.bottom_dims.size_z + self.bottom_dims.ribs_z, mode=Mode.SUBTRACT)

            self.debug_content.append({"small faces": faces().filter_by(lambda f: f.area < 1)}) if self.debug else None

        return keyplate.part
    
    def create_keywell(self):
        print("Creating keywell...")

        with BuildPart() as keywell:
            with BuildSketch():
                add(self.outline.sketch)
            extrude(amount=self.keywell_dims.size_z)

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
        with BuildSketch(Plane.XY.offset(-self.keyplate_dims.size_z)) as bottom_outline:
            offset(self.outline.sketch, -self.bottom_dims.keyplate_offset + clearance, kind=Kind.INTERSECTION)
            # fillet(bottom_outline.vertices(), radius=1)

        return bottom_outline.sketch

    def create_bottom_wall(self, outer_clearance = 0, inner_clearance = 0):
        print("  bottom wall...")

        with BuildSketch(Plane.XY.offset(-self.keyplate_dims.size_z+self.bottom_dims.size_z)) as bottom_wall:
            add(self.create_bottom_outline(outer_clearance))
            offset(self.outline.sketch, -self.bottom_dims.keyplate_offset - self.bottom_dims.ribs_xy - inner_clearance, kind=Kind.INTERSECTION, mode=Mode.SUBTRACT)
            # fillet(bottom_wall.vertices(), radius=1)
        return bottom_wall.sketch

    def create_bottom_clips(self, bottom_outline: Sketch, outward_facing=False, camera_position=Vector((0,1,0))):
        print("  bottom clips...")
        def correct_direction(face: Face) -> bool:
            normal = face.normal_at()
            look_direction = face.center() - camera_position
            direction_scalar = normal.dot(look_direction)
            return direction_scalar < 0 and normal.Z == 0

        z_position = bottom_outline.edges()[0].start_point().Z + self.keyplate_dims.clip_position_z
        camera_position = Vector(camera_position.X, camera_position.Y, z_position) 

        with BuildPart() as clips:
            for e in bottom_outline.edges().filter_by(GeomType.LINE):
                clip_length = e.length * self.keyplate_dims.clip_xy
                direction = (e.start_point() - e.end_point())
                total_height = 2*self.keyplate_dims.clip_z
                add(
                    Box(self.keyplate_dims.clip_z, clip_length, total_height, mode=Mode.PRIVATE)
                .rotate(Axis.Z, -math.degrees(math.atan2(direction.X, direction.Y)))
                .translate(e.center() + (0,0, self.keyplate_dims.clip_position_z)))
            selected_faces = faces()\
                .filter_by(correct_direction) \
                .filter_by(lambda f: f.area > self.keyplate_dims.clip_z * total_height)
            chamfer(selected_faces.edges(), length=self.keyplate_dims.clip_z/2)
            fillet(edges(Select.LAST), radius=self.keyplate_dims.clip_z/3)
            self.debug_content.append({f"clips_{"bottom" if outward_facing else "keyplate"}":
                                       {"clips": clips.part, 
                                        "selected_faces": selected_faces, 
                                        "edges": selected_faces.edges(), 
                                        "camera": Sphere(0.5, mode=Mode.PRIVATE).translate(camera_position)}}) if self.debug else None

        return clips.part

    def create_bottom(self):
        print("Creating bottom...")

        with BuildPart() as bottom:
            fingernail_recess_for_easier_removal = 0.5

            bottom_outline = self.create_bottom_outline()
            extrude(to_extrude=bottom_outline, amount=fingernail_recess_for_easier_removal)
            chamfer(objects=bottom.faces().sort_by(Axis.Z)[-1].edges(), length=fingernail_recess_for_easier_removal-self.dims.clearance)
            extrude(to_extrude=bottom_outline.translate((0, 0, fingernail_recess_for_easier_removal)), amount=self.bottom_dims.size_z-fingernail_recess_for_easier_removal)

            add(self.create_bottom_wall())
            extrude(amount=self.keyplate_dims.size_z - self.bottom_dims.size_z - Choc.clamps.clearance_z)
            fillet(objects=bottom.faces().group_by(Axis.Z)[-1].edges()
                   + bottom.faces().group_by(Axis.Z)[-2].edges(), 
                   radius=self.bottom_dims.ribs_z/2 - self.dims.clearance)

            add(self.create_bottom_clips(bottom_outline, outward_facing=True, camera_position=bottom.part.center()), mode=Mode.SUBTRACT)

            ribs_sketch = self.create_bottom_ribs_sketch()
            ribs_sketch = offset(objects=ribs_sketch, amount=-2*self.dims.clearance, mode=Mode.PRIVATE)
            extrude(to_extrude=ribs_sketch, amount=self.bottom_dims.ribs_z, mode=Mode.ADD)

            print("  bumper cutouts...")
            with BuildSketch(Plane.XY.offset(-self.keyplate_dims.size_z)): 
                with Locations(self.bumperholder_dims.bottom_holder_locations() + self.bumperholder_dims.bumper_locations()):
                    Circle(self.bumper.dims.radius + 2*self.dims.clearance)
            extrude(amount=self.bottom_dims.size_z+self.bottom_dims.ribs_z, mode=Mode.SUBTRACT)

            with BuildSketch(Plane.XY.offset(-self.keyplate_dims.size_z+self.bumper.dims.base_z)): 
                with Locations(self.bumperholder_dims.bottom_holder_locations()):
                    Circle(self.bumperholder_dims.radius - self.bumperholder_dims.deflect)
            bottom_holder_cut1 = extrude(amount=self.bottom_dims.size_z+self.bottom_dims.ribs_z-self.bumper.dims.base_z, mode=Mode.SUBTRACT)

            with BuildSketch(Plane.XY.offset(-self.keyplate_dims.size_z)): 
                with Locations(self.bumperholder_dims.bottom_holder_locations()):
                    Circle(self.bumperholder_dims.radius + self.dims.clearance)
            extrude(amount=self.bumper.dims.base_z + self.dims.clearance, mode=Mode.SUBTRACT)
            chamfer(
                bottom.edges(Select.LAST).edges().filter_by(GeomType.CIRCLE).group_by(Edge.length)[0]
                + bottom_holder_cut1.edges().group_by(Axis.Z)[-1],
                length=self.bumperholder_dims.deflect)
            fillet(bottom.edges(Select.LAST).edges().filter_by(GeomType.CIRCLE).group_by(Edge.length)[0],
                   radius=self.bumperholder_dims.deflect/2)

        return bottom.part

    def create_connector_sketch(self):
        with BuildSketch(Plane.XY.offset(-self.keyplate_dims.size_z+self.bottom_dims.size_z)) as connector_sketch:
            top_y = self.keys.middle.locs[2].Y+Choc.cap.length_y/2

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
        print("  bottom ribs...")
        with BuildSketch(Plane.XY.offset(-self.keyplate_dims.size_z+self.bottom_dims.size_z)) as bottom_ribs:

            with BuildSketch() as key_holes:
                for keycol in self.keys.finger_cols:
                    with BuildSketch() as keycol_sketch:
                        with Locations((keycol.locs[0] + keycol.locs[len(keycol.locs)-1]) / 2):
                            Rectangle(Choc.cap.width_x+2, 3*Choc.cap.length_y+self.bottom_dims.ribs_xy/2, rotation=keycol.rotation)
                        with Locations(keycol.locs):
                            Rectangle(Choc.bottom_housing.width_x+2, Choc.bottom_housing.depth_y+1, mode=Mode.SUBTRACT, rotation=keycol.rotation)

                keycol = self.keys.thumb
                with BuildSketch() as keycol_sketch:
                    with Locations((keycol.locs[0] + keycol.locs[len(keycol.locs)-1]) / 2):
                        with Locations((0, Choc.cap.length_y / 2)):
                            Rectangle(2*Choc.cap.width_x, self.bottom_dims.ribs_xy, rotation=keycol.rotation)


            with Locations(self.bumperholder_dims.bottom_holder_locations()):
                Circle(self.bumperholder_dims.radius+1.2)

            # fill the weird gap between lower pinkie and the outline
            with BuildSketch(Plane.XY, mode=Mode.PRIVATE) as filler:
                with BuildLine():
                    Polyline((20,3.75), 
                             (30.6,3.75),
                             (31.6,5.4),
                             (30.5, 8.3),
                             (20,3.9),
                             close=True)
                make_face() 
                with BuildLine():
                    Polyline((45,19), 
                             (46,19),
                             (46,21),
                             (45,21), 
                             close=True)
                make_face() 
            filler = filler.sketch
            add(filler)
            self.debug_content.append({"filler": filler}) if self.debug else None

        self.debug_content.append({"bottom_ribs": bottom_ribs}) if self.debug else None        
        return bottom_ribs.sketch

    def create_accessories(self):
        if not self.debug:
            return
        
        choc = Choc()        
        with BuildPart() as self.chocs:
            self.chocs.name = "Choc Switches"

            for keycol in self.keys.finger_cols:
                with Locations(keycol.locs):
                    add(copy.copy(choc.model.part).rotate(Axis.Z, keycol.rotation))
                keycol = self.keys.thumb
                with Locations(keycol.locs):
                    add(copy.copy(choc.model.part).rotate(Axis.Z, keycol.rotation+180))
        self.chocs = self.chocs.part

        self.xiao.model = self.xiao.model\
            .rotate(Axis.X, 180)\
            .translate(self.dims.xiao_position)
        
        self.bumper.model = self.bumper.model.rotate(Axis.X, 180).translate((0,0,-self.keyplate_dims.size_z + self.bumper.dims.base_z))
        with BuildPart() as self.bumpers:
            with Locations(self.bumperholder_dims.bumper_locations() + self.bumperholder_dims.bottom_holder_locations()):
                add(copy.copy(self.bumper.model))
        self.bumpers = self.bumpers.part
            

if __name__ == "__main__":
    set_port(3939)
    case = DualityWaveCase(debug=True)
    show_clear()
    set_defaults(ortho=True, default_edgecolor="#121212", reset_camera=Camera.KEEP)
    set_colormap(ColorMap.seeded(colormap="rgb", alpha=1, seed_value="wave"))
    show_objects() 