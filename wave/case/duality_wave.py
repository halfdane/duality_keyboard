from dataclasses import dataclass, field, InitVar
import math
import copy
from build123d import *
from models.choc import Choc
from models.cherry import Cherry
from models.switch import Switch
from models.xiao import Xiao
from models.power_switch import PowerSwitch
from models.symbol import Symbol
from models.space_invader import SpaceInvader
from models.keys import ErgoKeys, Point
from models.outline import Outline
from models.rubber_bumper import RubberBumper, BumperDimensions
from models.pin import Pin
from models.model_types import RoundDimensions, PosAndDims, RectDimensions

from ocp_vscode import *


@dataclass
class CaseDimensions:
    switch: InitVar[Switch]
    outline: InitVar[Outline]
    keys: InitVar[ErgoKeys]

    clearance: float = 0.02
    wall_thickness: float = 1.8

    above_z: float = field(init=False)
    add_below_choc_posts: float = field(init=False)
    below_z: float = field(init=False)
    bottom_plate_z: float = field(init=False)
    keyplate_z: float = field(init=False)

    clip_protusion: float = 0.4
    clip_lower_z: float = field(init=False)
    clip_upper_z: float = field(init=False)

    xiao_position: Vector = field(init=False)
    xiao_mirror_position: Vector = field(init=False)

    powerswitch_position: Vector = field(init=False)
    powerswitch_rotation: Vector = field(init=False)

    pin_radius: float = field(init=False)
    pin_plane: Plane = field(init=False)
    pin_locations: list[Vector] = field(init=False)

    battery_pd: PosAndDims = field(init=False)

    magnet_d: RoundDimensions = field(init=False)
    magnet_positions: list[Vector] = field(init=False)

    weight_d: Vector = field(init=False)
    weight_positions: list[Vector] = field(init=False)

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
        self.pin_plane: Plane = Plane(
            (outline.top_right.X/2, outline.top_right.Y, -self.keyplate_z), 
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


@dataclass
class BumperHolderDimensions:
    keys: InitVar[ErgoKeys]
    outline: InitVar[Outline]
    switch: InitVar[Switch]

    radius: float = BumperDimensions.radius+1
    height_z: float = 0.5
    deflect: float = 0.4

    bumper_locations: list[Vector] = field(init=False)

    def __post_init__(self, keys: ErgoKeys, outline: Outline, switch: Switch):
        base_offset = 2.5
        radius = BumperDimensions.radius + base_offset
        self.bumper_locations = [
            keys.thumb_clusters[0][1][0].p + Vector(switch.cap.d.X/2 - radius/2 - 0.5, -switch.cap.d.Y/2+radius/2 + 0.5).rotate(Axis.Z, keys.thumb_clusters[0][1][0].r),
            outline.top_right + Vector(-radius, -radius),
            outline.bottom_left + Vector(radius, radius),
            outline.top_left + Vector(radius, -radius),
            (keys.finger_clusters[0][2][0].p + keys.finger_clusters[0][2][1].p) / 2 + (8, 0),
        ]

class DualityWaveCase:

    def __init__(self, switch: Switch, debug=False, both_sides=False):
        self.switch = switch
        self.keys = ErgoKeys()
        self.outline = Outline(switch=self.switch, keys=self.keys, wall_thickness=CaseDimensions.wall_thickness)

        self.dims = CaseDimensions(switch=self.switch, outline=self.outline, keys=self.keys)
        self.bumperholder_dims = BumperHolderDimensions(switch=self.switch, outline=self.outline, keys=self.keys)
        self.bumper = RubberBumper()

        self.debug_content: list = []

        print("Creating case...")

        self.debug = debug

        push_object(self.debug_content, name="debug") if self.debug else None

        self.create_accessories()
        
        xiao_plane = Plane.XY
        xiao_plane = xiao_plane.rotated((180,0,0)).move(Location(self.dims.xiao_position))
        xiao_mirrored_plane = xiao_plane.rotated((180,0,0)).move(Location(self.dims.xiao_mirror_position))
        self.xiao = Xiao(xiao_plane, clearance=self.dims.clearance)

        accessories = []
        accessories.append({"chocs": self.switches})
        accessories.append({"xiao": self.xiao.model})
        accessories.append({"bumpers": self.bumpers})
        accessories.append({"power_switch": self.powerswitch})
        accessories.append({"pins": self.pins})

        battery = Box(self.dims.battery_pd.d.X, self.dims.battery_pd.d.Y, self.dims.battery_pd.d.Z)
        battery = battery.translate(self.dims.battery_pd.p)
        accessories.append({"battery": battery})

        with BuildPart() as magnets: 
            with BuildSketch(Plane.XY.offset(self.dims.magnet_positions[0].Z)) as magnet_sketch:
                with Locations(self.dims.magnet_positions):
                    Circle(self.dims.magnet_d.radius)
            extrude(amount=-self.dims.magnet_d.Z)
        accessories.append({"magnets": magnets})

        with BuildPart() as weights:
            with BuildSketch(Plane.XY.offset(self.dims.weight_positions[0].Z)) as weight_sketch:
                with Locations(self.dims.weight_positions):
                    Rectangle(self.dims.weight_d.X, self.dims.weight_d.Y)
            extrude(amount=-self.dims.weight_d.Z)
        accessories.append({"weights": weights})

        push_object(accessories, name="accessories")

        self.keywell_left = self.create_keywell()
        self.keywell_left = self.xiao.add_usb_cutouts(self.keywell_left)
        push_object(self.keywell_left, name="keywell_left") if self.debug else None

        # self.keyplate_left = self.create_keyplate()
        # self.keyplate_left = self.xiao.add_large_usb_cutouts(self.keyplate_left)
        # push_object(self.keyplate_left, name="keyplate_left") if self.debug else None

        # self.bottom_left = self.create_bottom()
        # self.bottom_left = self.xiao.add_large_usb_cutouts(self.bottom_left)
        # self.bottom_left = self.xiao.add_reset_lever(self.bottom_left, xiao_plane.offset(self.dims.keyplate_z + self.dims.xiao_position.Z)) 
        # push_object(self.bottom_left, name="bottom_left") if self.debug else None

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

            accessories.append({"chocs_right": mirror(self.switches, about=Plane.YZ)})
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
                for key in self.keys.keys:
                    with Locations(key.p):
                        Rectangle(self.switch.below.d.X, self.switch.below.d.Y, rotation=key.r)
            debug_content.append({"key_holes": key_holes}) if self.debug else None
            extrude(amount=-self.switch.clamp_clearance_z, mode=Mode.SUBTRACT)

            with BuildSketch(Plane.XY.offset(-self.switch.clamp_clearance_z)) as keyholes_with_space:
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
                for cluster in self.keys.clusters:
                    for keycol in cluster:
                        with BuildLine() as col_line:
                            pts = [ key.p + (self.switch.posts.p2.d.X, -self.switch.posts.p2.d.Y) for key in keycol]
                            if len(pts) < 2:
                                continue
                            Polyline(*pts)
                            offset(amount=connector_width, side=Side.BOTH)
                        make_face()

                    max_rows = max(len(col) for col in cluster)
                    for row_idx in range(max_rows):
                        with BuildLine() as row_line:
                            # For this row, collect the appropriate position from each column
                            pts = []
                            for col in cluster:
                                if len(col) > row_idx:
                                    pts.append(col[row_idx])
                                elif len(col) > 0:  # fall back to the "lower" row if not enough points
                                    pts.append(col[-1])
                                # else: skip empty column (no point to connect)
                            pts = [key.p + (self.switch.posts.p2.d.X, -self.switch.posts.p2.d.Y) for key in pts]
                            if len(pts) < 2:
                                continue
                            Polyline(*pts)
                            offset(amount=connector_width, side=Side.BOTH)
                        make_face()

                def find_closest_pair(keys_a: list[Point|Vector], keys_b: list[Point|Vector]) -> tuple[Vector, Vector]:
                    min_distance = math.inf
                    closest_a = None
                    closest_b = None
                    for a in keys_a:
                        for b in keys_b:
                            a_pos = a.p if isinstance(a, Point) else a
                            b_pos = b.p if isinstance(b, Point) else b
                            dist = (a_pos - b_pos).length
                            if dist < min_distance:
                                min_distance = dist
                                closest_a = a_pos
                                closest_b = b_pos
                    return closest_a, closest_b
                
                # find closest points between clusters and connect them
                for i in range(len(self.keys.clusters)-1):
                    cluster_a = [key for col in self.keys.clusters[i] for key in col]
                    cluster_b = [key for col in self.keys.clusters[i+1] for key in col]
                    closest_pair = find_closest_pair(cluster_a, cluster_b)
                    l = Line(closest_pair)
                    offset(objects=l, amount=connector_width, side=Side.BOTH)
                    make_face()

            extrude(amount=self.dims.keyplate_z - self.switch.bottom_housing.d.Z, mode=Mode.SUBTRACT)
            debug_content.append({"connector_sketch": connector_sketch}) if self.debug else None

            connect_to_xiao_plane = Plane.XY
            top_pinkie = self.keys.finger_clusters[0][0][len(self.keys.finger_clusters[0][0])-1].p
            connect_to_xiao_plane.origin = (top_pinkie + (self.dims.xiao_position.X, self.dims.xiao_position.Y))/2
            connect_to_xiao_plane.origin += Vector(0, 0, self.dims.xiao_position.Z+0.3)
            with BuildSketch(connect_to_xiao_plane) as connect_to_xiao:
                v = Vector(0, top_pinkie.Y - self.dims.xiao_position.Y)
                l=Line(v/2, -v/2)
                offset(l, amount=2*connector_width, side=Side.BOTH)
                make_face()
            debug_content.append({"connect_to_xiao": connect_to_xiao}) if self.debug else None

            connect_to_xiao_cut = extrude(amount=-7, mode=Mode.SUBTRACT)
            debug_content.append({"connect_to_xiao_cut": connect_to_xiao_cut}) if self.debug else None

            print("  powerswitch...")
            with BuildSketch(Plane(self.dims.powerswitch_position).rotated(self.dims.powerswitch_rotation)) as powerswitch_cut:
                Rectangle(PowerSwitch.dims.d.X + 2*self.dims.clearance, PowerSwitch.dims.d.Y + 2*self.dims.clearance)
                pin_clearance_y = (PowerSwitch.dims.d.Y + PowerSwitch.dims.pin_length + 10)
                with Locations((0, pin_clearance_y/2)):
                    Rectangle(PowerSwitch.dims.d.X - 3, pin_clearance_y)
            extrude(amount=-PowerSwitch.dims.d.Z, mode=Mode.SUBTRACT)
            debug_content.append({"powerswitch_cut": powerswitch_cut}) if self.debug else None

            print("  pin extrusion...")
            with BuildSketch(Plane.XY.offset(self.dims.pin_plane.origin.Z)) as pin_space_sketch:
                with Locations((self.dims.pin_plane.origin.X, 
                                self.outline.top_left.Y - 1.5*self.dims.wall_thickness - 0.5)):
                    Rectangle(self.dims.wall_thickness*2 + 0.5, self.dims.wall_thickness*3 + 0.5)
            pin_space =extrude(amount=self.dims.keyplate_z, mode=Mode.SUBTRACT)
            debug_content.append({"pin_space": pin_space}) if self.debug else None

            print("  pin holes...")
            with BuildSketch(self.dims.pin_plane) as pin_holes:
                Circle(self.dims.pin_radius)
            debug_content.append({"pin_holes": pin_holes}) if self.debug else None
            extrude(amount=self.pin.dims.length, mode=Mode.SUBTRACT)


        return keyplate.part
    
    def create_keywell(self):
        print("Creating keywell...")
        debug_content = []
        self.debug_content.append({"keywell": debug_content}) if self.debug else None
        with BuildPart() as keywell:
            with BuildSketch(Plane.XY.offset(self.dims.above_z)) as body_sketch:
                add(self.outline.create_outline())
            body = extrude(amount=-self.dims.below_z - self.dims.above_z)

            def intersect_faces(faces: ShapeList[Face]) -> ShapeList[Face]:
                return lambda aFace: len([aFace for f in faces if f.intersect(aFace) is not None]) > 0

            print("  skulpting thumb cut...")
            debug_thumb_content = []
            debug_content.append({"thumb_cut": debug_thumb_content}) if self.debug else None

            thumb_x_from_top = self.switch.cap.d.Z + self.switch.stem.d.Z
            taper = 35
            with BuildSketch(Plane.XY.offset(self.dims.above_z - thumb_x_from_top)) as thumb_cut_sketch:
                for thumb_cluster in self.keys.thumb_clusters:
                    for column_index, column in enumerate(thumb_cluster):
                        for key_index, key in enumerate(column):
                            x = self.switch.above.d.X * 1.5
                            y = self.switch.above.d.Y * 0.75
                            loc = Location(key.p + (0, -y), key.r)
                            if key_index == 0 and column_index == 0:
                                # this is the innermost key - start the cut further to the right
                                loc.position += Vector(self.switch.above.d.X/3, 0, 0).rotate(Axis.Z, key.r)
                            
                            if key_index == 0:
                                # this is the first key in the column - make the cut taller
                                loc.position += Vector(0, -5, 0).rotate(Axis.Z, key.r)
                                y += 10
                            with Locations(loc):
                                Rectangle(x, y)

            debug_thumb_content.append({"sketch": thumb_cut_sketch}) if self.debug else None
            thumb_cut=extrude(amount=thumb_x_from_top, mode=Mode.SUBTRACT, taper=-taper)

            # every face thats not top or bottom
            outside = [f for f in body.faces() if f not in body.faces().filter_by(Axis.Z)]
            outside_faces = keywell.faces().filter_by(intersect_faces(outside))
            debug_content.append({"outside_faces": outside_faces}) if self.debug else None
            fillet(outside_faces.edges(), radius=1)

            
            keywell_wall = self.outline.create_inner_outline(offset_by=-self.dims.wall_thickness)
            add(keywell_wall)
            keywell_cut = extrude(amount=-self.dims.below_z, mode=Mode.SUBTRACT)

            inner_faces = keywell.faces()\
                .filter_by(intersect_faces(keywell_cut.faces())) \
                .group_by(Axis.Z)[0]
            debug_content.append({"inner_faces": inner_faces}) if self.debug else None
            bottom_inner_edges = inner_faces \
                .edges().group_by(Axis.Z)[0]
            debug_content.append({"bottom_inner_edges": bottom_inner_edges}) if self.debug else None

            chamfer(set(bottom_inner_edges), length=0.1)
            
            print("  keywell cut...")
            with BuildSketch(Plane.XY.offset(self.dims.above_z)) as key_cut_sketch:
                add(self.outline.create_keywell_outline() )
            extrude(to_extrude=key_cut_sketch.sketch, amount=-self.dims.below_z - self.dims.above_z, mode=Mode.SUBTRACT)



            edges_to_add_clips = self.filter_clip_edges(keywell_wall.edges())
            long_clips, short_clips = self.split_off_clips_that_should_be_longer(edges_to_add_clips)

            print("  clips...")
            # c = self.add_bottom_clips(long_clips, clips_on_outside=False, z_position=self.dims.clip_lower_z, extralong=True)
            # debug_content.append({"bottom long clips": c}) if self.debug else None
            # c = self.add_bottom_clips(short_clips, clips_on_outside=False, z_position=self.dims.clip_lower_z)
            # debug_content.append({"bottom short clips": c}) if self.debug else None
            c = self.add_bottom_clips(edges_to_add_clips, clips_on_outside=False, z_position=self.dims.clip_upper_z)
            debug_content.append({"keyplate clips": c}) if self.debug else None
            return keywell.part

            print("  pin holes...")
            with BuildSketch(self.dims.pin_plane) as pin_holes:
                Circle(self.dims.pin_radius)
            debug_content.append({"pin_holes": pin_holes}) if self.debug else None
            extrude(amount=self.pin.dims.length, mode=Mode.SUBTRACT)

            print("  battery recess...")
            battery_pd = self.dims.battery_pd
            with BuildSketch(Plane.XY.offset(battery_pd.p.Z)) as battery_sketch:
                with Locations((battery_pd.p.X, battery_pd.p.Y)):
                    Rectangle(battery_pd.d.X + 2*self.dims.clearance, battery_pd.d.Y + 2*self.dims.clearance)
            extrude(amount=-battery_pd.d.Z - self.dims.wall_thickness, mode=Mode.SUBTRACT)
            debug_content.append({"battery_sketch": battery_sketch}) if self.debug else None

            print("  magnet recesses...")
            with BuildSketch(Plane.XY.offset(self.dims.magnet_positions[0].Z)) as magnet_sketch:
                with Locations(self.dims.magnet_positions):
                    Circle(self.dims.magnet_d.radius + self.dims.clearance)
            extrude(amount=-self.dims.above_z - self.dims.magnet_d.Z - 0.5, mode=Mode.SUBTRACT)
            debug_content.append({"magnet_sketch": magnet_sketch}) if self.debug else None

            print("  weight recesses...")
            with BuildSketch(Plane.XY.offset(self.dims.weight_positions[0].Z)) as weight_sketch:
                with Locations(self.dims.weight_positions):
                    Rectangle(self.dims.weight_d.X + 2*self.dims.clearance, self.dims.weight_d.Y + 2*self.dims.clearance)
            extrude(amount=-self.dims.above_z - self.dims.weight_d.Z, mode=Mode.SUBTRACT)
            debug_content.append({"weight_sketch": weight_sketch}) if self.debug else None

            print("  symbol...")
            with BuildSketch(Plane.XY.offset(self.dims.above_z)) as symbol_sketch:
                symbol_height = 20
                with Locations(self.outline.top_left + Vector(0.7*symbol_height, -0.7*symbol_height)):
                    add(Symbol(total_height=symbol_height).sketch)
            extrude(amount=-0.5, mode=Mode.SUBTRACT)
            debug_content.append({"symbol_sketch": symbol_sketch}) if self.debug else None

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
            extrude(to_extrude=clip, amount=-dir*total_protrusion, mode=mode, taper=-dir*taper)
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
            with BuildSketch(Plane.XY.offset(self.dims.xiao_position.Z)) as xiao_cutout:
                with Locations((self.dims.xiao_position.X, self.dims.xiao_position.Y - Xiao.processor.forward_y)):
                    Rectangle(Xiao.dims.d.X - 0.5, Xiao.dims.d.Y - Xiao.processor.forward_y*2 +4)
            extrude(amount=-(Xiao.dims.d.Z + Xiao.processor.d.Z/2) , mode=Mode.SUBTRACT)
            debug_content.append({"xiao xiao_cutout": xiao_cutout}) if self.debug else None

            print("  bumper cutouts...")
            with BuildSketch(Plane.XY.offset(-self.dims.below_z)):
                with Locations(self.bumperholder_dims.bumper_locations):
                    Circle(self.bumper.dims.radius)
            extrude(amount=self.bumper.dims.base_z, mode=Mode.SUBTRACT)

            print("  switch post cutouts")
            with BuildSketch(Plane.XY.offset(-self.switch.below.d.Z)) as choc_posts:
                for key in self.keys.keys:
                    with Locations(key.p):
                        for post in self.switch.posts.posts:
                            with BuildSketch(mode=Mode.PRIVATE) as choc_post_sketch:
                                with Locations(post.p):
                                    Circle(post.d.radius + 0.25)
                            add(choc_post_sketch.sketch.mirror(Plane.XZ).rotate(Axis.Z, key.r))
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

            print("  pin extrusion...")
            with BuildSketch(Plane.XY.offset(-self.dims.below_z + self.dims.bottom_plate_z)) as pin_space_sketch:
                with Locations(((self.outline.top_right.X - self.outline.top_left.X)/2, 
                                self.outline.top_left.Y - self.dims.wall_thickness*2 - 0.5)):
                    Rectangle(self.dims.wall_thickness*2, self.dims.wall_thickness*2)
            pin_space =extrude(amount=self.dims.keyplate_z, taper=2)
            fillet(pin_space.edges(), radius=0.3 - self.dims.clearance)
            debug_content.append({"pin_space": pin_space}) if self.debug else None

            print("  pin holes...")
            with BuildSketch(self.dims.pin_plane) as pin_holes:
                Circle(self.dims.pin_radius)
            debug_content.append({"pin_holes": pin_holes}) if self.debug else None
            extrude(amount=self.pin.dims.length, mode=Mode.SUBTRACT)

            print("  space invader...")
            with BuildSketch(Plane.XY.offset(-self.dims.below_z)) as invader_sketch:
                invader_height = 10
                with Locations(self.outline.cirque_recess_position \
                               + (self.outline.cirque_recess_radius-2, self.outline.cirque_recess_radius)):
                    add(SpaceInvader(total_height=invader_height).sketch.rotate(Axis.Z, -40))
            extrude(amount=0.5, mode=Mode.SUBTRACT)
            debug_content.append({"invader_sketch": invader_sketch}) if self.debug else None



        return bottom.part

    def create_accessories(self):
        if not self.debug:
            return
        
        with BuildPart() as self.switches:
            for key in self.keys.keys:
                with Locations(key.p):
                    add(self.switch.model.part.rotate(Axis.Z, key.r))
        self.switches = self.switches.part
        
        self.bumper.model = self.bumper.model.rotate(Axis.X, 180).translate((0,0,-self.dims.below_z + self.bumper.dims.base_z))
        with BuildPart() as self.bumpers:
            with Locations(self.bumperholder_dims.bumper_locations):
                add(self.bumper.model)
        self.bumpers = self.bumpers.part

        self.powerswitch = PowerSwitch()
        self.powerswitch = self.powerswitch.model\
            .rotate(Axis.Y, self.dims.powerswitch_rotation.Y )\
            .rotate(Axis.Z, self.dims.powerswitch_rotation.Z )\
            .translate(self.dims.powerswitch_position)

        self.pin = Pin()
        with BuildPart(self.dims.pin_plane) as self.pins:
            add(self.pin.model)
        self.pins = self.pins.part


if __name__ == "__main__":
    set_port(3939)
    case = DualityWaveCase(switch=Choc(), debug=True, both_sides=False)
    show_clear()
    set_defaults(ortho=True, default_edgecolor="#121212", reset_camera=Camera.KEEP)
    set_colormap(ColorMap.seeded(colormap="rgb", alpha=1, seed_value="wave"))
    show_objects() 

    export_stl(case.keywell_left, "keywell_left.stl", tolerance=0.01) if hasattr(case, "keywell_left") else None
    export_stl(case.keyplate_left, "keyplate_left.stl", tolerance=0.01) if hasattr(case, "keyplate_left") else None
    export_stl(case.bottom_left, "bottom_left.stl", tolerance=0.01) if hasattr(case, "bottom_left") else None
