from dataclasses import dataclass, field
import math
import copy
from build123d import *
from models.switch import Choc
from models.xiao import Xiao
from models.power_switch import PowerSwitch
from models.symbol import Symbol
from models.keys import Keys
from models.outline import Outline
from models.rubber_bumper import RubberBumper, BumperDimensions

from ocp_vscode import *


@dataclass
class BottomDimensions:
    size_z: float = 2.8
    keyplate_offset: float = 1.8


@dataclass
class KeyplateDimensions:
    size_z: float = Choc.below.d.Z + 1.3/2
    switch_clamp_clearance: float = size_z - Choc.clamps.clearance_z

    connector_width: float = 2
    connector_depth_z: float = Choc.posts.center.d.Z

    clip_xy: float = 0.4
    clip_protusion: float = 0.4
    clip_position_z: float = -size_z + 1.3

@dataclass
class BumperHolderDimensions:
    keys: Keys
    outline: Outline

    radius: float = BumperDimensions.radius+1
    height_z: float = 0.5
    deflect: float = 0.4

    def bumper_locations(self) -> list[Vector]:
        o_dims = self.outline.dims
        base_offset = 2.5
        radius = BumperDimensions.radius + base_offset
        return [
            self.keys.thumb.locs[1] + Vector(Choc.cap.d.X/2 - radius + BottomDimensions.keyplate_offset, -Choc.cap.d.Y/2 + radius - BottomDimensions.keyplate_offset).rotate(Axis.Z, Keys.thumb.rotation),
            Vector(o_dims.base.X, o_dims.base.Y) + Vector(-radius, -radius),
            Vector(0, 0) + Vector(radius, radius),
            Vector(0, o_dims.base.Y) + Vector(radius, -radius),
        ]
    
    def bottom_holder_locations(self) -> list[Vector]:
        return [
            (self.keys.middle.locs[0] + self.keys.middle.locs[1]) / 2 + (8, 0),
        ]


@dataclass
class CaseDimensions:
    clearance: float = 0.02
    pin_radius: float = 0.5    

    xiao_offset: float = BottomDimensions.keyplate_offset + Xiao.usb.forward_y + 2*clearance
    xiao_pos_x: float = 10 + Xiao.dims.d.X/2
    xiao_pos_y: float = Outline.dims.base.Y - Xiao.dims.d.Y/2 - xiao_offset
    xiao_pos_z: float = 0
    xiao_position: Vector = Vector(xiao_pos_x, xiao_pos_y, xiao_pos_z)
    xiao_mirror_position: Vector = Vector(-xiao_pos_x, xiao_pos_y, xiao_pos_z)


@dataclass
class KeywellDimensions:
    size_z: float = Choc.above.d.Z

class DualityWaveCase:
    outline = Outline(wall_thickness=BottomDimensions.keyplate_offset)
    keys = Keys()
    upside_down_locations = (
        Keys.pointer.locs[1],
    )

    dims = CaseDimensions()
    keywell_dims = KeywellDimensions()
    keyplate_dims = KeyplateDimensions()
    bottom_dims = BottomDimensions()

    bumperholder_dims = BumperHolderDimensions(keys, outline)

    bumper = RubberBumper()

    debug_content: list = []

    def __init__(self, debug=False, both_sides=False):
        print("Creating case...")

        self.debug = debug

        push_object(self.debug_content, name="debug_content") if self.debug else None

        self.create_accessories()
        
        xiao_plane = Plane.XY
        xiao_plane = xiao_plane.rotated((180,0,0)).move(Location(self.dims.xiao_position))
        xiao_mirrored_plane = xiao_plane.rotated((180,0,0)).move(Location(self.dims.xiao_mirror_position))
        self.xiao = Xiao(xiao_plane, clearance=self.dims.clearance)

        self.keywell_left = self.create_keywell()
        self.keywell_left = self.xiao.add_usb_cutouts(self.keywell_left)
        push_object(self.keywell_left, name="keywell_left") if self.debug else None

        self.keyplate_left = self.create_keyplate()
        self.keyplate_left = self.xiao.add_large_usb_cutouts(self.keyplate_left)
        push_object(self.keyplate_left, name="keyplate_left") if self.debug else None

        self.bottom_left = self.create_bottom()
        self.bottom_left = self.xiao.add_large_usb_cutouts(self.bottom_left)
        self.bottom_left = self.xiao.add_reset_lever(self.bottom_left, xiao_plane.offset(self.keyplate_dims.size_z - self.bottom_dims.size_z))
        push_object(self.bottom_left, name="bottom_left") if self.debug else None

        push_object(self.chocs, name="chocs")
        push_object(self.xiao.model, name="xiao_left")
        push_object(self.bumpers, name="bumpers")

        if both_sides:
            self.keywell_right = mirror(self.keywell_left, about=Plane.YZ)
            self.keywell_right = self.xiao.add_usb_cutouts(self.keywell_right)
            push_object(self.keywell_right, name="keywell_right") if self.debug else None

            self.keyplate_right = mirror(self.keyplate_left, about=Plane.YZ)
            self.keyplate_right = self.xiao.add_large_usb_cutouts(self.keyplate_right)
            push_object(self.keyplate_right, name="keyplate_right") if self.debug else None

            self.bottom_right = mirror(self.bottom_left, about=Plane.YZ)
            self.bottom_right = self.xiao.add_large_usb_cutouts(self.bottom_right)
            self.bottom_right = self.xiao.add_reset_lever(self.bottom_right, xiao_mirrored_plane.offset(self.keyplate_dims.size_z - self.bottom_dims.size_z))
            push_object(self.bottom_right, name="bottom_right") if self.debug else None

            push_object(mirror(self.chocs, about=Plane.YZ), name="chocs") if self.debug else None
            push_object(Xiao(xiao_mirrored_plane).model, name="xiao_right")
        print("Done creating case.")

    def create_keyplate(self):
        print("Creating keyplate...")

        with BuildPart() as keyplate:
            base=add(self.outline.create_inner_outline(offset_by=-self.bottom_dims.keyplate_offset - 2*self.dims.clearance))
            extrude(amount=-self.keyplate_dims.size_z+self.bottom_dims.size_z)
            self.debug_content.append({"base": base}) if self.debug else None

            print("  key holes...")
            with BuildSketch() as key_holes:
                for keycol in self.keys.keycols:
                    with Locations(keycol.locs):
                        Rectangle(Choc.below.d.X, Choc.below.d.Y, rotation=keycol.rotation)
            self.debug_content.append({"key_holes (keyplate)": key_holes}) if self.debug else None
            extrude(amount=-Choc.clamps.clearance_z, mode=Mode.SUBTRACT)

            with BuildSketch(Plane.XY.offset(-Choc.clamps.clearance_z)) as keyholes_with_space:
                offset(key_holes.sketch, 0.5)
            extrude(amount=-self.keyplate_dims.size_z, mode=Mode.SUBTRACT)

            print("  xiao hole...")
            with BuildSketch(Plane(self.dims.xiao_position)) as xiao_hole:
                Rectangle(Xiao.dims.d.X - 1.5, Xiao.dims.d.Y - 1.5)
            extrude(amount=self.keyplate_dims.size_z, mode=Mode.SUBTRACT)
            with BuildSketch(Plane(self.dims.xiao_position)) as xiao_cut:
                Rectangle(Xiao.dims.d.X + 2*self.dims.clearance, Xiao.dims.d.Y + 2*self.dims.clearance)
            extrude(amount=-self.keyplate_dims.size_z, mode=Mode.SUBTRACT)

            print("  connector cut...")
            connector_sketch = self.create_connector_sketch()
            extrude(to_extrude=connector_sketch, amount=self.keyplate_dims.connector_depth_z, mode=Mode.SUBTRACT)

            print("  bumpers...")
            with BuildPart() as bumper_holder:
                raising = 1
                with BuildSketch(Plane.XY.offset(-self.keyplate_dims.size_z+self.bottom_dims.size_z-raising)) as bottom_holder_sketch:
                    with Locations(self.bumperholder_dims.bottom_holder_locations()):
                        Circle(self.bumperholder_dims.radius - 1.5*self.bumperholder_dims.deflect)
                extrude(amount=-self.bottom_dims.size_z + self.bumper.dims.base_z + raising)
                chamfer(edges(Select.LAST).group_by(Axis.Z)[-1], length=0.5 - self.dims.clearance)
                extrude(to_extrude=offset(bottom_holder_sketch.sketch, amount=-0.5, mode=Mode.PRIVATE), amount=3, taper=45)

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
                extrude(amount=self.bottom_dims.size_z - raising/2, mode=Mode.SUBTRACT)

            self.debug_content.append({"small faces": faces().filter_by(lambda f: f.area < 1)}) if self.debug else None

        return keyplate.part
    
    def create_keywell(self):
        print("Creating keywell...")

        with BuildPart() as keywell:
            with BuildSketch():
                add(self.outline.create_keywell_outline())
            extrude(amount=self.keywell_dims.size_z)

            with BuildSketch() as wall_sketch:
                add(self.outline.create_outline())
                keywell_wall = self.outline.create_inner_outline(-self.bottom_dims.keyplate_offset)
                add(keywell_wall, mode=Mode.SUBTRACT)
            extrude(to_extrude=wall_sketch.sketch, amount=Choc.upper_housing.d.Z+Choc.base.d.Z)
            extrude(to_extrude=wall_sketch.sketch, amount=-self.keyplate_dims.size_z)


            clips = self.create_bottom_clips(keywell_wall, clips_on_outside=False, z_position=self.keyplate_dims.clip_position_z)
            for clip in clips:
                extrude(to_extrude=clip, amount=-self.keyplate_dims.clip_protusion + self.dims.clearance, mode=Mode.SUBTRACT)
                chamfer(clip.edges(), length=self.keyplate_dims.clip_protusion - 2*self.dims.clearance)

        return keywell.part

    def create_bottom_clips(self, outline: Sketch, clips_on_outside: bool = False, z_position: float = 0) -> list[Sketch]:
        print("  bottom clips...")

        clips = []
        for e in outline.edges().filter_by(GeomType.LINE):
            edge_center = e.center()
            edge_direction = (e.end_point() - e.start_point()).normalized()
            plane_normal = Vector(edge_direction.Y, -edge_direction.X, 0)  # Perpendicular to edge in XY plane
            plane_origin = Vector(edge_center.X, edge_center.Y, z_position)
            plane = Plane(origin=plane_origin, z_dir=plane_normal, x_dir=edge_direction)
            clip_length = e.length * self.keyplate_dims.clip_xy
            if clips_on_outside:
                plane = plane.offset(-self.keyplate_dims.clip_protusion)
                total_height = 4*self.keyplate_dims.clip_protusion
            else:
                total_height = 2*self.keyplate_dims.clip_protusion + 4*self.dims.clearance
                clip_length -= 2*self.keyplate_dims.clip_protusion - 2*self.dims.clearance

            
            with BuildSketch(plane) as clip:
                Rectangle(clip_length, total_height)
            clips.append(clip.sketch)

        self.debug_content.append({"clips": clips}) if self.debug else None
        return clips

    def create_bottom(self):
        print("Creating bottom...")

        with BuildPart() as bottom:
            outline = self.outline.create_inner_outline(offset_by=-self.bottom_dims.keyplate_offset - 2*self.dims.clearance)
            
            with BuildSketch(Plane.XY.offset(-self.keyplate_dims.size_z)) as base:
                add(outline)
            extrude(amount=self.bottom_dims.size_z)
            chamfer(objects=bottom.faces().filter_by(Axis.Z).edges(), length=0.3)

            clips = self.create_bottom_clips(base.sketch, clips_on_outside=True, z_position=self.keyplate_dims.clip_position_z)
            for clip in clips:
                extrude(to_extrude=clip, amount=self.keyplate_dims.clip_protusion, mode=Mode.ADD)
                chamfer(clip.edges(), length=self.keyplate_dims.clip_protusion - self.dims.clearance)

            print("  xiao support...")
            with BuildSketch(Plane.XY.offset(-self.keyplate_dims.size_z)) as xiao_support:
                with Locations((self.dims.xiao_position.X, self.dims.xiao_position.Y)):
                    Rectangle(5, 5)
            extrude(amount=self.keyplate_dims.size_z + self.dims.xiao_position.Z - Xiao.dims.d.Z - Xiao.processor.d.Z - self.dims.clearance)

            print("  bumper cutouts...")
            with BuildSketch(Plane.XY.offset(-self.keyplate_dims.size_z)):
                with Locations(self.bumperholder_dims.bumper_locations()):
                    Circle(self.bumper.dims.radius)
            extrude(amount=self.bumper.dims.base_z, mode=Mode.SUBTRACT)

            with BuildSketch(Plane.XY.offset(-self.keyplate_dims.size_z)): 
                with Locations(self.bumperholder_dims.bottom_holder_locations()):
                    Circle(self.bumper.dims.radius + 2*self.dims.clearance)
            extrude(amount=self.bottom_dims.size_z, mode=Mode.SUBTRACT)

            with BuildSketch(Plane.XY.offset(-self.keyplate_dims.size_z)): 
                with Locations(self.bumperholder_dims.bottom_holder_locations()):
                    Circle(self.bumper.dims.radius + 2)
            extrude(amount=self.bottom_dims.size_z)

            with BuildSketch(Plane.XY.offset(-self.keyplate_dims.size_z+self.bumper.dims.base_z)): 
                with Locations(self.bumperholder_dims.bottom_holder_locations()):
                    Circle(self.bumperholder_dims.radius - self.bumperholder_dims.deflect)
            bottom_holder_cut1 = extrude(amount=self.bottom_dims.size_z - self.bumper.dims.base_z, mode=Mode.SUBTRACT)

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


            with BuildSketch(Plane.XY.offset(-Choc.below.d.Z)) as choc_posts:
                for keycol in self.keys.keycols:
                    with Locations([l for l in keycol.locs if l not in self.upside_down_locations]):
                        for post in Choc.posts.posts:
                            with BuildSketch(mode=Mode.PRIVATE) as choc_post_sketch:
                                with Locations(post.p):
                                    Circle(post.d.radius + 0.25)
                            add(choc_post_sketch.sketch.mirror(Plane.XZ).rotate(Axis.Z, keycol.rotation))
            extrude(amount=5, mode=Mode.SUBTRACT)
            self.debug_content.append({"chocs posts": choc_posts}) if self.debug else None

            with BuildSketch(Plane.XY.offset(-Choc.below.d.Z)) as choc_posts:
                for keycol in self.keys.keycols:
                    with Locations([l for l in keycol.locs if l in self.upside_down_locations]):
                        for post in Choc.posts.posts:
                            with BuildSketch(mode=Mode.PRIVATE) as choc_post_sketch:
                                with Locations(post.p):
                                    Circle(post.d.radius + 0.25)
                            add(choc_post_sketch.sketch.mirror(Plane.XZ).rotate(Axis.Z, 180+keycol.rotation))
            extrude(amount=5, mode=Mode.SUBTRACT)
            self.debug_content.append({"chocs posts rotated": choc_posts}) if self.debug else None

        return bottom.part

    def create_connector_sketch(self):
        with BuildSketch(Plane.XY.offset(-self.keyplate_dims.size_z+self.bottom_dims.size_z)) as connector_sketch:
            top_y = self.keys.middle.locs[2].Y+Choc.cap.d.Y/2

            for row in range(3):
                with BuildLine() as row_line:
                    pts = [ keycol.locs[row] + (Choc.posts.p2.d.X, -Choc.posts.p2.d.Y) for keycol in self.keys.finger_cols]
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

            l = Line(self.keys.thumb.locs[0]+ Choc.posts.p2.d, self.keys.thumb.locs[1]+ Choc.posts.p2.d)
            offset(l, amount=self.keyplate_dims.connector_width/2, side=Side.BOTH)
            make_face()
            for t in self.keys.thumb.locs:
                l = Line(t, self.keys.inner.locs[0])
                offset(l, amount=self.keyplate_dims.connector_width/2, side=Side.BOTH)
                make_face()
        
        self.debug_content.append({"connector_sketch": connector_sketch}) if self.debug else None
        return connector_sketch.sketch            

    def create_accessories(self):
        if not self.debug:
            return
        
        choc = Choc()        
        with BuildPart() as self.chocs:
            self.chocs.name = "Choc Switches"

            for keycol in self.keys.keycols:
                with Locations([l for l in keycol.locs if l not in self.upside_down_locations]):
                    add(choc.model.part.rotate(Axis.Z, keycol.rotation))

            for keycol in self.keys.keycols:
                with Locations([l for l in keycol.locs if l in self.upside_down_locations]):
                    add(choc.model.part.rotate(Axis.Z, 180+keycol.rotation))
        self.chocs = self.chocs.part
        
        self.bumper.model = self.bumper.model.rotate(Axis.X, 180).translate((0,0,-self.keyplate_dims.size_z + self.bumper.dims.base_z))
        with BuildPart() as self.bumpers:
            with Locations(self.bumperholder_dims.bumper_locations() + self.bumperholder_dims.bottom_holder_locations()):
                add(copy.copy(self.bumper.model))
        self.bumpers = self.bumpers.part

        powerswitch = PowerSwitch()
        powerswitch = powerswitch.model.part\
            .rotate(Axis.Y, 180)\
            .rotate(Axis.Z, 90)\
            .translate((self.dims.xiao_pos_x + Xiao.dims.d.X/2 + 3, self.dims.xiao_pos_y + 5, -(PowerSwitch.dims.thickness_z/2 + self.bottom_dims.size_z - PowerSwitch.dims.lever_height_z)))
        push_object(powerswitch, name="power_switch") if self.debug else None


if __name__ == "__main__":
    set_port(3939)
    case = DualityWaveCase(debug=True, both_sides=False)
    show_clear()
    set_defaults(ortho=True, default_edgecolor="#121212", reset_camera=Camera.KEEP)
    set_colormap(ColorMap.seeded(colormap="rgb", alpha=1, seed_value="wave"))
    show_objects() 