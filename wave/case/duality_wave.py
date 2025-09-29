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
class CaseDimensions:
    clearance: float = 0.02
    pin_radius: float = 0.5
    
    wall_thickness: float = 1.8

    above_z: float = Choc.above.d.Z
    add_below_choc_posts: float = 0.7
    below_z: float = Choc.below.d.Z + add_below_choc_posts
    bottom_plate_z: float = 3
    keyplate_z: float = below_z - bottom_plate_z

    clip_xy: float = 0.4
    clip_protusion: float = 0.4
    clip_position_z: float = -below_z + 1.5

    xiao_offset: float = wall_thickness + Xiao.usb.forward_y + 2*clearance
    xiao_pos_x: float = 10 + Xiao.dims.d.X/2
    xiao_pos_y: float = Outline.dims.base.Y - Xiao.dims.d.Y/2 - xiao_offset
    xiao_pos_z: float = -0.2
    xiao_position: Vector = Vector(xiao_pos_x, xiao_pos_y, xiao_pos_z)
    xiao_mirror_position: Vector = Vector(-xiao_pos_x, xiao_pos_y, xiao_pos_z)

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
            self.keys.thumb.locs[1] + Vector(Choc.cap.d.X/2 - radius + CaseDimensions.wall_thickness, -Choc.cap.d.Y/2 + radius - CaseDimensions.wall_thickness).rotate(Axis.Z, Keys.thumb.rotation),
            Vector(o_dims.base.X, o_dims.base.Y) + Vector(-radius, -radius),
            Vector(0, 0) + Vector(radius, radius),
            Vector(0, o_dims.base.Y) + Vector(radius, -radius),
        ]
    
    def bottom_holder_locations(self) -> list[Vector]:
        return [
            (self.keys.middle.locs[0] + self.keys.middle.locs[1]) / 2 + (8, 0),
        ]

class DualityWaveCase:
    outline = Outline(wall_thickness=CaseDimensions.wall_thickness)
    keys = Keys()
    upside_down_locations = (
        Keys.pointer.locs[1],
    )

    dims = CaseDimensions()
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

        push_object(self.chocs, name="chocs")
        push_object(self.xiao.model, name="xiao_left")
        push_object(self.bumpers, name="bumpers")

        self.keywell_left = self.create_keywell()
        self.keywell_left = self.xiao.add_usb_cutouts(self.keywell_left)
        push_object(self.keywell_left, name="keywell_left") if self.debug else None

        self.keyplate_left = self.create_keyplate()
        self.keyplate_left = self.xiao.add_large_usb_cutouts(self.keyplate_left)
        push_object(self.keyplate_left, name="keyplate_left") if self.debug else None

        self.bottom_left = self.create_bottom()
        self.bottom_left = self.xiao.add_large_usb_cutouts(self.bottom_left)
        self.bottom_left = self.xiao.add_reset_lever(self.bottom_left, xiao_plane.offset(self.dims.keyplate_z))
        push_object(self.bottom_left, name="bottom_left") if self.debug else None

        if both_sides:
            self.keywell_right = mirror(self.keywell_left, about=Plane.YZ)
            self.keywell_right = self.xiao.add_usb_cutouts(self.keywell_right)
            push_object(self.keywell_right, name="keywell_right") if self.debug else None

            self.keyplate_right = mirror(self.keyplate_left, about=Plane.YZ)
            self.keyplate_right = self.xiao.add_large_usb_cutouts(self.keyplate_right)
            push_object(self.keyplate_right, name="keyplate_right") if self.debug else None

            self.bottom_right = mirror(self.bottom_left, about=Plane.YZ)
            self.bottom_right = self.xiao.add_large_usb_cutouts(self.bottom_right)
            self.bottom_right = self.xiao.add_reset_lever(self.bottom_right, xiao_mirrored_plane.offset(self.dims.keyplate_z))
            push_object(self.bottom_right, name="bottom_right") if self.debug else None

            push_object(mirror(self.chocs, about=Plane.YZ), name="chocs") if self.debug else None
            push_object(Xiao(xiao_mirrored_plane).model, name="xiao_right")
        print("Done creating case.")

    def create_keyplate(self):
        print("Creating keyplate...")

        with BuildPart() as keyplate:
            base=add(self.outline.create_inner_outline(offset_by=-self.dims.wall_thickness - 2*self.dims.clearance))
            extrude(amount=-self.dims.keyplate_z)
            self.debug_content.append({"base": base}) if self.debug else None

            bottom_edges = faces().filter_by(Axis.Z)[-1].edges()
            chamfer(objects=bottom_edges, length=0.5)

            print("  key holes...")
            with BuildSketch() as key_holes:
                for keycol in self.keys.keycols:
                    with Locations(keycol.locs):
                        Rectangle(Choc.below.d.X, Choc.below.d.Y, rotation=keycol.rotation)
            self.debug_content.append({"key_holes (keyplate)": key_holes}) if self.debug else None
            extrude(amount=-Choc.clamps.clearance_z, mode=Mode.SUBTRACT)

            with BuildSketch(Plane.XY.offset(-Choc.clamps.clearance_z)) as keyholes_with_space:
                offset(key_holes.sketch, 0.5)
            extrude(amount=-self.dims.below_z, mode=Mode.SUBTRACT)

            print("  xiao hole...")
            with BuildSketch(Plane(self.dims.xiao_position)) as xiao_hole:
                Rectangle(Xiao.dims.d.X - 1.5, Xiao.dims.d.Y - 1.5)
            extrude(amount=self.dims.below_z, mode=Mode.SUBTRACT)
            with BuildSketch(Plane(self.dims.xiao_position)) as xiao_cut:
                Rectangle(Xiao.dims.d.X + 2*self.dims.clearance, Xiao.dims.d.Y + 2*self.dims.clearance)
            extrude(amount=-self.dims.below_z, mode=Mode.SUBTRACT)

            print("  connector cut...")
            connector_sketch = self.create_connector_sketch()
            extrude(to_extrude=connector_sketch, amount=self.dims.keyplate_z - Choc.bottom_housing.d.Z, mode=Mode.SUBTRACT)

            print("  bumpers...")
            with BuildPart() as bumper_holder:
                raising = 1
                with BuildSketch(Plane.XY.offset(-self.dims.below_z+self.dims.bottom_plate_z-raising)) as bottom_holder_sketch:
                    with Locations(self.bumperholder_dims.bottom_holder_locations()):
                        Circle(self.bumperholder_dims.radius - 1.5*self.bumperholder_dims.deflect)
                extrude(amount=-self.dims.bottom_plate_z + self.bumper.dims.base_z + raising)
                chamfer(edges(Select.LAST).group_by(Axis.Z)[-1], length=0.5 - self.dims.clearance)
                extrude(to_extrude=offset(bottom_holder_sketch.sketch, amount=-0.5, mode=Mode.PRIVATE), amount=3, taper=45)

                with BuildSketch(Plane.XY.offset(-self.dims.below_z+self.bumper.dims.base_z+self.bumperholder_dims.height_z)):
                    with Locations(self.bumperholder_dims.bottom_holder_locations()):
                        Circle(self.bumperholder_dims.radius)
                        Circle(self.bumper.dims.radius, mode=Mode.SUBTRACT)
                extrude(amount=-self.bumper.dims.base_z-self.bumperholder_dims.height_z)
            
                chamfer(edges(Select.LAST).group_by(Edge.length)[-1], length=0.5)
                fillet(edges(Select.LAST).edges().filter_by(GeomType.CIRCLE).group_by(Edge.length)[-1],
                    radius=self.bumperholder_dims.deflect/2)

                with BuildSketch(Plane.XY.offset(-self.dims.below_z)):
                    with Locations(self.bumperholder_dims.bottom_holder_locations()):
                        Rectangle(10, 1)
                        Rectangle(1, 10)
                extrude(amount=self.dims.bottom_plate_z - raising/2, mode=Mode.SUBTRACT)

            self.debug_content.append({"small faces": faces().filter_by(lambda f: f.area < 1)}) if self.debug else None

        return keyplate.part
    
    def create_keywell(self):
        print("Creating keywell...")

        with BuildPart() as keywell:
            with BuildSketch(Plane.XY.offset(self.dims.above_z)) as body_sketch:
                add(self.outline.create_outline() )
            extrude(amount=-self.dims.below_z - self.dims.above_z)
            fillet(objects=keywell.edges(), radius=1)

            with BuildSketch(Plane.XY.offset(self.dims.above_z)) as wall_sketch:
                add(self.outline.create_keywell_outline() )
            extrude(amount=-self.dims.below_z - self.dims.above_z, mode=Mode.SUBTRACT)

            keywell_wall = self.outline.create_inner_outline(offset_by=-self.dims.wall_thickness)
            add(keywell_wall)
            extrude(amount=-self.dims.below_z  , mode=Mode.SUBTRACT)
            bottom_inner_edges = keywell.edges(Select.LAST).group_by(Axis.Z)[0]
            # chamfer(bottom_inner_edges, length=0.1)

            edges_to_add_clips = keywell_wall.edges().sort_by(Axis.Y, reverse=True)
            clip_offset = Vector(0, 
                                 0, 
                                 0)
            self.add_bottom_clips(edges_to_add_clips[1:], clips_on_outside=False, z_position=self.dims.clip_position_z, clip_offset=clip_offset)
            
            clip_offset = Vector(0, 
                                 self.dims.clip_protusion,
                                 -self.dims.clip_protusion)
            self.add_bottom_clips(edges_to_add_clips[0], clips_on_outside=False, z_position=self.dims.clip_position_z, clip_offset=clip_offset)
        return keywell.part

    def add_bottom_clips(self, edges: ShapeList[Edge] | Edge, clips_on_outside: bool = False, z_position: float = 0, clip_offset: Vector = Vector(0, 0, 0)) -> list[Sketch]:
        """Clips on the outside are always protruding.

            Offset adds 
                - X to the clip length along the edge, 
                - Y to the protrusion, 
                - Z to the height.
        """
        print("  bottom clips...")
        clips = []
        # Ensure edges is always a list
        if isinstance(edges, Edge):
            edges = ShapeList([edges])
        for e in edges.filter_by(GeomType.LINE).filter_by(lambda e: e.length > 5):
            edge_center = e.center()
            edge_direction = (e.end_point() - e.start_point()).normalized()
            plane_normal = Vector(edge_direction.Y, -edge_direction.X, 0)  # Perpendicular to edge in XY plane
            plane_origin = Vector(edge_center.X, edge_center.Y, z_position)
            plane = Plane(origin=plane_origin, z_dir=plane_normal, x_dir=edge_direction)

            clip_length = e.length * self.dims.clip_xy + clip_offset.X
            total_height = 2*self.dims.clip_protusion + clip_offset.Z
            total_protrusion = self.dims.clip_protusion + clip_offset.Y

            if clips_on_outside:
                plane = plane.offset(-total_protrusion)

            with BuildSketch(plane) as clip:
                Rectangle(clip_length, total_height)
            clip = clip.sketch

            dir = 1 if clips_on_outside else -1
            mode = Mode.ADD if clips_on_outside else Mode.SUBTRACT
            extrude(to_extrude=clip, amount=total_protrusion * dir, mode=mode)
            chamfer(clip.edges(), length=total_protrusion - self.dims.clearance/2)
            clips.append(clip)

        self.debug_content.append({f"clips {"bottom" if clips_on_outside else "keywell"}": clips}) if self.debug else None


    def create_bottom(self):
        print("Creating bottom...")

        with BuildPart() as bottom:
            outline = self.outline.create_inner_outline(offset_by=-self.dims.wall_thickness - self.dims.clearance)
            
            with BuildSketch(Plane.XY.offset(-self.dims.below_z)) as base:
                add(outline)
            extrude(amount=self.dims.bottom_plate_z)
            top_edges = faces().filter_by(Axis.Z)[-1].edges()
            bottom_edges = faces().filter_by(Axis.Z)[0].edges()
            chamfer(objects=top_edges, length=0.5)
            chamfer(objects=bottom_edges, length=0.1)

            edges_to_add_clips = base.edges().sort_by(Axis.Y, reverse=True)

            clip_offset = Vector(2*self.dims.clip_protusion - 2*self.dims.clearance,
                                 0, 
                                 2*self.dims.clip_protusion - 2*self.dims.clearance)
            self.add_bottom_clips(edges_to_add_clips[1:], clips_on_outside=True, z_position=self.dims.clip_position_z, clip_offset=clip_offset)

            clip_offset = Vector(4*self.dims.clip_protusion - 2*self.dims.clearance, 
                                 self.dims.clip_protusion, 
                                 3*self.dims.clip_protusion - 2*self.dims.clearance)
            self.add_bottom_clips(edges_to_add_clips[0], clips_on_outside=True, z_position=self.dims.clip_position_z, clip_offset=clip_offset)

            print("  xiao support...")
            with BuildSketch(Plane.XY.offset(self.dims.xiao_position.Z)) as xiao_support:
                with Locations((self.dims.xiao_position.X, self.dims.xiao_position.Y - Xiao.processor.forward_y)):
                    Rectangle(Xiao.processor.d.X + 2*self.dims.clearance, Xiao.processor.d.Y + 4*self.dims.clearance)
            extrude(amount=-(Xiao.dims.d.Z + Xiao.processor.d.Z + self.dims.clearance) , mode=Mode.SUBTRACT)
            self.debug_content.append({"xiao support": xiao_support}) if self.debug else None

            print("  bumper cutouts...")
            with BuildSketch(Plane.XY.offset(-self.dims.below_z)):
                with Locations(self.bumperholder_dims.bumper_locations()):
                    Circle(self.bumper.dims.radius)
            extrude(amount=self.bumper.dims.base_z, mode=Mode.SUBTRACT)

            with BuildSketch(Plane.XY.offset(-self.dims.below_z)): 
                with Locations(self.bumperholder_dims.bottom_holder_locations()):
                    Circle(self.bumper.dims.radius + 2*self.dims.clearance)
            extrude(amount=self.dims.bottom_plate_z, mode=Mode.SUBTRACT)

            with BuildSketch(Plane.XY.offset(-self.dims.below_z)): 
                with Locations(self.bumperholder_dims.bottom_holder_locations()):
                    Circle(self.bumper.dims.radius + 2)
            extrude(amount=self.dims.bottom_plate_z)

            with BuildSketch(Plane.XY.offset(-self.dims.below_z+self.bumper.dims.base_z)): 
                with Locations(self.bumperholder_dims.bottom_holder_locations()):
                    Circle(self.bumperholder_dims.radius - self.bumperholder_dims.deflect)
            bottom_holder_cut1 = extrude(amount=self.dims.bottom_plate_z - self.bumper.dims.base_z, mode=Mode.SUBTRACT)

            with BuildSketch(Plane.XY.offset(-self.dims.below_z)): 
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
        connector_width: float = 2
        with BuildSketch(Plane.XY.offset(-self.dims.keyplate_z )) as connector_sketch:
            top_y = self.keys.middle.locs[2].Y+Choc.cap.d.Y/2

            for row in range(3):
                with BuildLine() as row_line:
                    pts = [ keycol.locs[row] + (Choc.posts.p2.d.X, -Choc.posts.p2.d.Y) for keycol in self.keys.finger_cols]
                    Polyline(*pts)
                    offset(amount=connector_width/2, side=Side.BOTH)
                make_face()

            for col in [self.keys.inner, self.keys.pointer, self.keys.middle, self.keys.ring]:
                column_to_topline = Line(col.locs[0], col.locs[2])
                offset(column_to_topline, amount=connector_width/2, side=Side.BOTH)
                make_face()
            
            with BuildLine() as pinkie_to_topline:
                pts = [ self.keys.pinkie.locs[0], self.keys.pinkie.locs[2], (self.keys.pinkie.locs[2].X, top_y) ]
                Polyline(*pts)
                offset(amount=connector_width, side=Side.BOTH)
            make_face()

            l = Line(self.keys.thumb.locs[0]+ Choc.posts.p2.d, self.keys.thumb.locs[1]+ Choc.posts.p2.d)
            offset(l, amount=connector_width/2, side=Side.BOTH)
            make_face()
            for t in self.keys.thumb.locs:
                l = Line(t, self.keys.inner.locs[0])
                offset(l, amount=connector_width/2, side=Side.BOTH)
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
        
        self.bumper.model = self.bumper.model.rotate(Axis.X, 180).translate((0,0,-self.dims.below_z + self.bumper.dims.base_z))
        with BuildPart() as self.bumpers:
            with Locations(self.bumperholder_dims.bumper_locations() + self.bumperholder_dims.bottom_holder_locations()):
                add(copy.copy(self.bumper.model))
        self.bumpers = self.bumpers.part

        powerswitch = PowerSwitch()
        powerswitch = powerswitch.model.part\
            .rotate(Axis.Y, 180)\
            .rotate(Axis.Z, 90)\
            .translate((self.dims.xiao_position.X + Xiao.dims.d.X/2 + 3, self.dims.xiao_position.Y + 5, -(PowerSwitch.dims.thickness_z/2 + self.dims.bottom_plate_z - PowerSwitch.dims.lever_height_z)))
        push_object(powerswitch, name="power_switch") if self.debug else None


if __name__ == "__main__":
    set_port(3939)
    case = DualityWaveCase(debug=True, both_sides=False)
    show_clear()
    set_defaults(ortho=True, default_edgecolor="#121212", reset_camera=Camera.KEEP)
    set_colormap(ColorMap.seeded(colormap="rgb", alpha=1, seed_value="wave"))
    show_objects() 

    export_stl(case.keywell_left, "keywell_left.stl", tolerance=0.01) if hasattr(case, "keywell_left") else None
    export_stl(case.keyplate_left, "keyplate_left.stl", tolerance=0.01) if hasattr(case, "keyplate_left") else None
    export_stl(case.bottom_left, "bottom_left.stl", tolerance=0.01) if hasattr(case, "bottom_left") else None
