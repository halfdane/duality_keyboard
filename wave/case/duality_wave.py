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
from models.pin import Pin

from ocp_vscode import *


@dataclass(frozen=True)
class CaseDimensions:
    clearance: float = 0.02
    
    wall_thickness: float = 1.8

    above_z: float = Choc.above.d.Z
    add_below_choc_posts: float = 0.7
    below_z: float = Choc.below.d.Z + add_below_choc_posts
    bottom_plate_z: float = 2.4
    keyplate_z: float = below_z - bottom_plate_z

    clip_protusion: float = 0.4
    clip_lower_z: float = -below_z + bottom_plate_z/2
    clip_upper_z: float = -keyplate_z/2

    xiao_to_power_switch: float = PowerSwitch.dims.d.Y/2 + PowerSwitch.dims.pin_length/2
    xiao_pos_x: float = 2*wall_thickness + Xiao.dims.d.X/2 + xiao_to_power_switch + PowerSwitch.dims.d.Y/2
    xiao_pos_y: float = Outline.dims.base.Y - Xiao.dims.d.Y/2 - Xiao.usb.forward_y - wall_thickness - 2*clearance
    xiao_pos_z: float = -1.45
    xiao_position: Vector = Vector(xiao_pos_x, xiao_pos_y, xiao_pos_z)
    xiao_mirror_position: Vector = Vector(-xiao_pos_x, xiao_pos_y, xiao_pos_z)

    powerswitch_position: Vector = Vector(
                xiao_position.X - Xiao.dims.d.X/2 - xiao_to_power_switch, 
                xiao_position.Y - 2, 
                -(below_z - 0.75*PowerSwitch.lever.d.Z))
    powerswitch_rotation: Vector = Vector(0, 180, 90)
     
    pin_radius: float = Pin.dims.radius + clearance
    pin_plane: Plane = field(default_factory=lambda: Plane(((Outline.dims.base.X)/2, Outline.dims.base.Y, CaseDimensions.clip_lower_z), z_dir=-Axis.Y.direction, x_dir=Axis.X.direction))
    pin_locations: list[Vector] = (
        Vector(0, 0),
        Vector(0.47 * Outline.dims.base.X, 0),
        Vector(-0.47 * Outline.dims.base.X, 0)
    )


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
            self.keys.thumb.locs[1] + Vector(Choc.cap.d.X/2 - radius/2 - 0.5, -Choc.cap.d.Y/2+radius/2 + 0.5).rotate(Axis.Z, Keys.thumb.rotation),
            Vector(o_dims.base.X, o_dims.base.Y) + Vector(-radius, -radius),
            Vector(0, 0) + Vector(radius, radius),
            Vector(0, o_dims.base.Y) + Vector(radius, -radius),

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

        push_object(self.debug_content, name="debug") if self.debug else None

        self.create_accessories()
        
        xiao_plane = Plane.XY
        xiao_plane = xiao_plane.rotated((180,0,0)).move(Location(self.dims.xiao_position))
        xiao_mirrored_plane = xiao_plane.rotated((180,0,0)).move(Location(self.dims.xiao_mirror_position))
        self.xiao = Xiao(xiao_plane, clearance=self.dims.clearance)

        accessories = []
        accessories.append({"chocs": self.chocs})
        accessories.append({"xiao": self.xiao.model})
        accessories.append({"bumpers": self.bumpers})
        accessories.append({"power_switch": self.powerswitch})
        push_object(accessories, name="accessories")

        self.keywell_left = self.create_keywell()
        self.keywell_left = self.xiao.add_usb_cutouts(self.keywell_left)
        push_object(self.keywell_left, name="keywell_left") if self.debug else None

        self.keyplate_left = self.create_keyplate()
        self.keyplate_left = self.xiao.add_large_usb_cutouts(self.keyplate_left)
        push_object(self.keyplate_left, name="keyplate_left") if self.debug else None

        self.bottom_left = self.create_bottom()
        self.bottom_left = self.xiao.add_usb_cutouts(self.bottom_left)
        self.bottom_left = self.xiao.add_reset_lever(self.bottom_left, xiao_plane.offset(self.dims.keyplate_z + self.dims.xiao_position.Z)) 
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
            self.bottom_right = self.xiao.add_reset_lever(self.bottom_right, xiao_mirrored_plane.offset(self.dims.keyplate_z + self.dims.xiao_position.Z))
            push_object(self.bottom_right, name="bottom_right") if self.debug else None

            accessories.append({"chocs_right": mirror(self.chocs, about=Plane.YZ)})
            accessories.append({"xiao_right": Xiao(xiao_mirrored_plane).model})
            accessories.append({"bumpers_right": mirror(self.bumpers, about=Plane.YZ)})
        print("Done creating case.")

    def create_keyplate(self):
        print("Creating keyplate...")
        debug_content = []
        self.debug_content.append({"keyplate": debug_content}) if self.debug else None
        with BuildPart() as keyplate:
            base=add(self.outline.create_inner_outline(offset_by=-self.dims.wall_thickness - self.dims.clearance))
            extrude(amount=-self.dims.keyplate_z)
            debug_content.append({"base": base}) if self.debug else None

            chamfer(objects=faces().filter_by(Axis.Z).edges(), length=0.1)

            edges_to_add_clips = self.filter_clip_edges(base.edges())
            c = self.add_bottom_clips(edges_to_add_clips, clips_on_outside=True, z_position=-self.dims.keyplate_z/2)
            debug_content.append({"clips": c}) if self.debug else None

            print("  key holes...")
            with BuildSketch() as key_holes:
                for keycol in self.keys.keycols:
                    with Locations(keycol.locs):
                        Rectangle(Choc.below.d.X, Choc.below.d.Y, rotation=keycol.rotation)
            debug_content.append({"key_holes": key_holes}) if self.debug else None
            extrude(amount=-Choc.clamps.clearance_z, mode=Mode.SUBTRACT)

            with BuildSketch(Plane.XY.offset(-Choc.clamps.clearance_z)) as keyholes_with_space:
                offset(key_holes.sketch, 0.5)
            extrude(amount=-self.dims.below_z, mode=Mode.SUBTRACT)

            print("  xiao hole...")
            with BuildSketch(Plane((self.dims.xiao_position.X, self.dims.xiao_position.Y, 0))) as xiao_hole:
                Rectangle(Xiao.dims.d.X - 1.5, Xiao.dims.d.Y - 1.5)
            extrude(amount=self.dims.xiao_position.Z, mode=Mode.SUBTRACT)
            with BuildSketch(Plane(self.dims.xiao_position)) as xiao_cut:
                Rectangle(Xiao.dims.d.X + 2*self.dims.clearance, Xiao.dims.d.Y + 2*self.dims.clearance)
            extrude(amount=-self.dims.below_z, mode=Mode.SUBTRACT)

            print("  connector cut...")
            connector_width: float = 1.5
            with BuildSketch(Plane.XY.offset(-self.dims.keyplate_z )) as connector_sketch:
                for row in range(3):
                    with BuildLine() as row_line:
                        pts = [ keycol.locs[row] + (Choc.posts.p2.d.X, -Choc.posts.p2.d.Y) for keycol in self.keys.finger_cols]
                        Polyline(*pts)
                        offset(amount=connector_width, side=Side.BOTH)
                    make_face()

                for col in [self.keys.inner, self.keys.pointer, self.keys.middle, self.keys.ring]:
                    column_to_topline = Line(col.locs[0], col.locs[2])
                    offset(column_to_topline, amount=connector_width, side=Side.BOTH)
                    make_face()
                
                with BuildLine() as pinkie_to_topline:
                    pts = [ self.keys.pinkie.locs[0], self.keys.pinkie.locs[2] ]
                    Polyline(*pts)
                    offset(amount=connector_width, side=Side.BOTH)
                make_face()

                l = Line(self.keys.thumb.locs[0]+ Choc.posts.p2.d, self.keys.thumb.locs[1]+ Choc.posts.p2.d)
                offset(l, amount=connector_width, side=Side.BOTH)
                make_face()
                for t in self.keys.thumb.locs:
                    l = Line(t, self.keys.inner.locs[0])
                    offset(l, amount=connector_width, side=Side.BOTH)
                    make_face()

            extrude(amount=self.dims.keyplate_z - Choc.bottom_housing.d.Z, mode=Mode.SUBTRACT)
            debug_content.append({"connector_sketch": connector_sketch}) if self.debug else None

            connect_to_xiao_plane = Plane.XY.rotated((20,0,0))
            connect_to_xiao_plane.origin = (self.keys.pinkie.locs[2] + (self.dims.xiao_position.X, self.dims.xiao_position.Y))/2
            connect_to_xiao_plane.origin += Vector(0, 0, self.dims.xiao_position.Z)
            with BuildSketch(connect_to_xiao_plane) as connect_to_xiao:
                v = Vector(0, self.keys.pinkie.locs[2].Y - self.dims.xiao_position.Y)
                l=Line(v/2, -v/2)
                offset(l, amount=2*connector_width, side=Side.BOTH)
                make_face()
            debug_content.append({"connect_to_xiao": connect_to_xiao}) if self.debug else None

            connect_to_xiao_cut = extrude(amount=-7, mode=Mode.SUBTRACT)
            debug_content.append({"connect_to_xiao_cut": connect_to_xiao_cut}) if self.debug else None

            print("  powerswitch...")
            with BuildSketch(Plane(self.dims.powerswitch_position).rotated(self.dims.powerswitch_rotation)) as powerswitch_cut:
                Rectangle(PowerSwitch.dims.d.X + self.dims.clearance, PowerSwitch.dims.d.Y)
                pin_clearance_y = (PowerSwitch.dims.d.Y + PowerSwitch.dims.pin_length + 10)
                with Locations((0, pin_clearance_y/2)):
                    Rectangle(PowerSwitch.dims.d.X - 4, pin_clearance_y)
            extrude(amount=-PowerSwitch.dims.d.Z, mode=Mode.SUBTRACT)
            debug_content.append({"powerswitch_cut": powerswitch_cut}) if self.debug else None

        return keyplate.part
    
    def create_keywell(self):
        print("Creating keywell...")
        debug_content = []
        self.debug_content.append({"keywell": debug_content}) if self.debug else None
        with BuildPart() as keywell:
            with BuildSketch(Plane.XY.offset(self.dims.above_z)) as body_sketch:
                add(self.outline.create_outline() )
            body = extrude(amount=-self.dims.below_z - self.dims.above_z)

            def intersect_faces(faces: ShapeList[Face]) -> ShapeList[Face]:
                return lambda aFace: len([aFace for f in faces if f.intersect(aFace) is not None]) > 0

            print("  skulpting thumb cut...")
            debug_thumb_content = []
            debug_content.append({"thumb_cut": debug_thumb_content}) if self.debug else None

            thumb_x_from_top = Choc.cap.d.Z + Choc.stem.d.Z
            taper = 35
            length_of_tapered_section = thumb_x_from_top / math.cos(math.radians(taper))
            with BuildSketch(Plane.XY.offset(self.dims.above_z)) as thumb_cut_sketch:
                with Locations(sum(self.keys.thumb.locs)/len(self.keys.thumb.locs)+Vector(Choc.cap.d.X/2+length_of_tapered_section/2-1, -Choc.cap.d.Y/2).rotate(Axis.Z, self.keys.thumb.rotation)):
                    Rectangle(Choc.cap.d.X * 3, Choc.cap.d.Y, rotation=self.keys.thumb.rotation)
            debug_thumb_content.append({"sketch": thumb_cut_sketch}) if self.debug else None
            thumb_cut=extrude(amount=-thumb_x_from_top, mode=Mode.SUBTRACT, taper=taper)
            thumb_cut_faces = keywell.faces().filter_by(intersect_faces(thumb_cut.faces()))

            debug_thumb_content.append({"faces": thumb_cut_faces}) if self.debug else None
            upper_edges = thumb_cut_faces.edges().group_by(Axis.Z)[-1]
            lower_edges = thumb_cut_faces.edges().group_by(Axis.Z)[0]
            debug_thumb_content.append({"lower_edges": lower_edges}) if self.debug else None
            back_and_top_edges = lower_edges.sort_by(Axis.Y, reverse=True)[0:3]
            debug_thumb_content.append({"back_and_top_edges": back_and_top_edges}) if self.debug else None
            thumb_to_fillet = ShapeList(upper_edges + back_and_top_edges)
            debug_thumb_content.append({"to_fillet": thumb_to_fillet}) if self.debug else None
            fillet(thumb_to_fillet, radius=length_of_tapered_section*0.8)

            # every face thats not top or bottom
            outside = [f for f in body.faces() if f not in body.faces().filter_by(Axis.Z)]
            outside_faces = keywell.faces().filter_by(intersect_faces(outside))
            debug_content.append({"outside_faces": outside_faces}) if self.debug else None
            fillet(outside_faces.edges(), radius=1)
            
            print("  keywell cut...")
            with BuildSketch(Plane.XY.offset(self.dims.above_z)) as key_cut_sketch:
                add(self.outline.create_keywell_outline() )
            extrude(amount=-self.dims.below_z - self.dims.above_z, mode=Mode.SUBTRACT)

            keywell_wall = self.outline.create_inner_outline(offset_by=-self.dims.wall_thickness)
            add(keywell_wall)
            keywell_cut = extrude(amount=-self.dims.below_z, mode=Mode.SUBTRACT)

            bottom_inner_edges = keywell.faces()\
                .filter_by(intersect_faces(keywell_cut.faces())) \
                .edges().group_by(Axis.Z)[0]
            debug_content.append({"bottom_inner_edges": bottom_inner_edges}) if self.debug else None
            chamfer(bottom_inner_edges, length=0.1)

            edges_to_add_clips = self.filter_clip_edges(keywell_wall.edges())
            long_clips, short_clips = self.split_off_clips_that_should_be_longer(edges_to_add_clips)

            print("  clips...")
            c = self.add_bottom_clips(long_clips, clips_on_outside=False, z_position=self.dims.clip_lower_z, extralong=True)
            debug_content.append({"bottom long clips": c}) if self.debug else None
            c = self.add_bottom_clips(short_clips, clips_on_outside=False, z_position=self.dims.clip_lower_z)
            debug_content.append({"bottom short clips": c}) if self.debug else None
            c = self.add_bottom_clips(edges_to_add_clips, clips_on_outside=False, z_position=self.dims.clip_upper_z)
            debug_content.append({"keyplate clips": c}) if self.debug else None

            print("  pin holes...")
            with BuildSketch(self.dims.pin_plane) as pin_holes:
                with Locations(self.dims.pin_locations):
                    Circle(self.dims.pin_radius)
            debug_content.append({"pin_holes": pin_holes}) if self.debug else None
            extrude(amount=2* self.dims.wall_thickness, mode=Mode.SUBTRACT)

            handle = 3
            with BuildSketch(self.dims.pin_plane.rotated((30, 0, 0))) as pin_holders:
                with Locations(self.dims.pin_locations[0:2]):
                    with Locations((-handle/2+ self.dims.pin_radius/2, -4 - self.dims.pin_radius + 2*self.dims.clearance)):
                        RectangleRounded(handle, 10, radius=self.dims.pin_radius)
                with Locations(self.dims.pin_locations[2]):
                    with Locations((handle/2 - self.dims.pin_radius/2, -4 - self.dims.pin_radius + 2*self.dims.clearance)):
                        RectangleRounded(handle, 10, radius=self.dims.pin_radius)
            extrude(amount=1, to_extrude=pin_holders.sketch, mode=Mode.SUBTRACT)
            extrude(amount=-self.dims.wall_thickness, to_extrude=pin_holders.sketch, mode=Mode.SUBTRACT)

        return keywell.part
    
    def split_off_clips_that_should_be_longer(self, edges: ShapeList[Edge] | Edge) -> tuple[ShapeList[Edge], ShapeList[Edge]]:
        """Split edges into two lists: those that should have long clips and those that should have short clips
            @return: (long_clip_edges, short_clip_edges)
        ."""
        if isinstance(edges, Edge):
            edges = ShapeList([edges])
        long_clip_edges = edges.sort_by(Axis.Y)[0:4].sort_by(Axis.X)[0:3]
        short_clip_edges = ShapeList([e for e in edges if e not in long_clip_edges])
        return long_clip_edges, short_clip_edges

    def filter_clip_edges(self, edges: ShapeList[Edge] | Edge) -> ShapeList[Edge]:
        """Filter edges to only include straight edges longer than 5mm."""
        if isinstance(edges, Edge):
            edges = ShapeList([edges])
        filtered_edges = edges\
            .sort_by(Axis.Y, reverse=True)\
            .filter_by(GeomType.LINE)\
            .filter_by(lambda e: e.length > 5)
        return filtered_edges

    def add_bottom_clips(self, edges: ShapeList[Edge] | Edge, clips_on_outside: bool = False, z_position: float = 0, extralong=False) -> list[Sketch]:
        if isinstance(edges, Edge):
            edges = ShapeList([edges])
        clips = []
        for e in edges:
            edge_center = e.center()
            edge_direction = (e.end_point() - e.start_point()).normalized()
            plane_normal = Vector(edge_direction.Y, -edge_direction.X, 0)  # Perpendicular to edge in XY plane
            plane_origin = Vector(edge_center.X, edge_center.Y, z_position)
            plane = Plane(origin=plane_origin, z_dir=plane_normal, x_dir=edge_direction)

            clip_xy_ratio: float = 0.6
            clip_length = e.length * clip_xy_ratio
            total_height = 4*self.dims.clip_protusion
            total_protrusion = self.dims.clip_protusion * (2 if extralong else 1)

            if clips_on_outside: 
                total_height -= self.dims.clearance * (8 if extralong else 2)
                clip_length -= 1
                plane = plane.offset(-total_protrusion)

            with BuildSketch(plane) as clip:
                Rectangle(clip_length, total_height)
            clip = clip.sketch

            dir = 1 if clips_on_outside else -1
            mode = Mode.ADD if clips_on_outside else Mode.SUBTRACT
            taper = 5 if extralong else 0
            extrude(to_extrude=clip, amount=dir*total_protrusion, mode=mode, taper=-dir*taper)
            if clips_on_outside:
                fillet(clip.edges(), radius=self.dims.clip_protusion - 0.2)
            clips.append(clip)
        return clips


    def create_bottom(self):
        print("Creating bottom...")
        debug_content = []
        self.debug_content.append({"bottom": debug_content}) if self.debug else None
        with BuildPart() as bottom:
            outline = self.outline.create_inner_outline(offset_by=-self.dims.wall_thickness - self.dims.clearance)
            
            with BuildSketch(Plane.XY.offset(-self.dims.below_z)) as base:
                add(outline)
            extrude(amount=self.dims.bottom_plate_z)
            chamfer(objects=faces().filter_by(Axis.Z).edges(), length=0.1)

            edges_to_add_clips = self.filter_clip_edges(base.edges())
            long_clips, short_clips = self.split_off_clips_that_should_be_longer(edges_to_add_clips)
            c = self.add_bottom_clips(long_clips, clips_on_outside=True, z_position=self.dims.clip_lower_z, extralong=True)
            debug_content.append({"long clips": c}) if self.debug else None
            c = self.add_bottom_clips(short_clips, clips_on_outside=True, z_position=self.dims.clip_lower_z)
            debug_content.append({"short clips": c}) if self.debug else None

            print("  xiao support...")
            with BuildSketch(Plane.XY.offset(self.dims.xiao_position.Z)) as xiao_support:
                with Locations((self.dims.xiao_position.X, self.dims.xiao_position.Y - Xiao.processor.forward_y)):
                    Rectangle(Xiao.processor.d.X + 0.5, Xiao.processor.d.Y + 0.5)
            extrude(amount=-(Xiao.dims.d.Z + Xiao.processor.d.Z + self.dims.clearance) , mode=Mode.SUBTRACT)
            debug_content.append({"xiao support": xiao_support}) if self.debug else None

            print("  bumper cutouts...")
            with BuildSketch(Plane.XY.offset(-self.dims.below_z)):
                with Locations(self.bumperholder_dims.bumper_locations()):
                    Circle(self.bumper.dims.radius)
            extrude(amount=self.bumper.dims.base_z, mode=Mode.SUBTRACT)

            with BuildSketch(Plane.XY.offset(-Choc.below.d.Z)) as choc_posts:
                for keycol in self.keys.keycols:
                    with Locations(keycol.locs):
                        for post in Choc.posts.posts:
                            with BuildSketch(mode=Mode.PRIVATE) as choc_post_sketch:
                                with Locations(post.p):
                                    Circle(post.d.radius + 0.25)
                            add(choc_post_sketch.sketch.mirror(Plane.XZ).rotate(Axis.Z, keycol.rotation))
            extrude(amount=5, mode=Mode.SUBTRACT)
            debug_content.append({"chocs posts": choc_posts}) if self.debug else None

            with BuildSketch(Plane(self.dims.powerswitch_position).rotated(self.dims.powerswitch_rotation)) as powerswitch_cut:
                with Locations((0, PowerSwitch.dims.pin_length/2)):
                    Rectangle(PowerSwitch.dims.d.X + 1, PowerSwitch.dims.d.Y + 1 + PowerSwitch.dims.pin_length)
            extrude(amount=-10, mode=Mode.SUBTRACT)

            with BuildSketch(Plane(self.dims.powerswitch_position).rotated(self.dims.powerswitch_rotation)) as powerswitch_lever_cut_sketch:
                with Locations(-PowerSwitch.lever.p):
                    RectangleRounded(PowerSwitch.lever.clearance + 0.5, PowerSwitch.lever.d.Y +0.5, radius=0.5)
            powerswitch_lever_cut = extrude(amount=self.dims.powerswitch_position.Z + self.dims.below_z, mode=Mode.SUBTRACT)
            debug_content.append({"powerswitch_lever_cut": powerswitch_lever_cut}) if self.debug else None  
            chamfer(powerswitch_lever_cut.edges().group_by(Axis.Z)[0], length=1.5, length2=0.5)

            print("  pin holes...")
            with BuildSketch(self.dims.pin_plane) as pin_holes:
                with Locations(self.dims.pin_locations):
                    Circle(self.dims.pin_radius)
            debug_content.append({"pin_holes": pin_holes}) if self.debug else None
            extrude(amount=2* self.dims.wall_thickness, mode=Mode.SUBTRACT)

        return bottom.part

    def create_accessories(self):
        if not self.debug:
            return
        
        choc = Choc()        
        with BuildPart() as self.chocs:
            self.chocs.name = "Choc Switches"

            for keycol in self.keys.keycols:
                with Locations(keycol.locs):
                    add(choc.model.part.rotate(Axis.Z, keycol.rotation))
        self.chocs = self.chocs.part
        
        self.bumper.model = self.bumper.model.rotate(Axis.X, 180).translate((0,0,-self.dims.below_z + self.bumper.dims.base_z))
        with BuildPart() as self.bumpers:
            with Locations(self.bumperholder_dims.bumper_locations()):
                add(copy.copy(self.bumper.model))
        self.bumpers = self.bumpers.part

        self.powerswitch = PowerSwitch()
        self.powerswitch = self.powerswitch.model\
            .rotate(Axis.Y, self.dims.powerswitch_rotation.Y )\
            .rotate(Axis.Z, self.dims.powerswitch_rotation.Z )\
            .translate(self.dims.powerswitch_position)


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
