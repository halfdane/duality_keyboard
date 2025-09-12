from dataclasses import dataclass, field
import math
import copy
from build123d import *
from models.switch import Choc
from models.xiao import Xiao
from models.power_switch import PowerSwitch
from models.knurl import Knurl
from models.symbol import Symbol

from ocp_vscode import *

class KeyCol:
    rotation: float = 0
    locs: list[Location] = []

@dataclass
class PinkieDimensions(KeyCol):
    x: float = 0
    y: float = 0
    offset_x: float = -1
    rotation: float = 8
    locs: list[Location] = (
        Location((0, 0)), 
        Location((-Choc.cap.width_x/rotation, Choc.cap.length_y)), 
        Location((-2*Choc.cap.width_x/rotation, 2*Choc.cap.length_y))
    )

@dataclass
class RingFingerDimensions(KeyCol):
    x: float = Choc.cap.width_x + PinkieDimensions.offset_x
    y: float = 14
    rotation: float = 0
    locs: list[Location] = (
        Location((x, y)), 
        Location((x, Choc.cap.length_y + y)), 
        Location((x, 2*Choc.cap.length_y + y))
    )

@dataclass
class MiddleFingerDimensions(KeyCol):
    x: float = 2*Choc.cap.width_x + PinkieDimensions.offset_x
    y: float = 22.4
    rotation: float = 0
    locs: list[Location] = (
        Location((x, y)), 
        Location((x, Choc.cap.length_y + y)), 
        Location((x, 2*Choc.cap.length_y + y))
    )

@dataclass
class PointerFingerDimensions(KeyCol):
    x: float = 3*Choc.cap.width_x + PinkieDimensions.offset_x
    y: float = 18
    rotation: float = 0
    locs: list[Location] = (
        Location((x, y)), 
        Location((x, Choc.cap.length_y + y)), 
        Location((x, 2*Choc.cap.length_y + y))
    )

@dataclass
class InnerFingerDimensions(KeyCol):
    x: float = 4*Choc.cap.width_x + PinkieDimensions.offset_x
    y: float = 14
    rotation: float = 0
    locs: list[Location] = (
        Location((x, y)), 
        Location((x, Choc.cap.length_y + y)), 
        Location((x, 2*Choc.cap.length_y + y))
    )

@dataclass
class ThumbDimensions(KeyCol):
    x: float = InnerFingerDimensions.locs[0].position.X - 6.5
    y: float = InnerFingerDimensions.locs[0].position.Y - 18
    rotation: float = -8
    locs: list[Location] = (
        Location((x, y)), 
        Location((Choc.cap.width_x + x, y + Choc.cap.length_y/rotation)), 
    )

@dataclass
class CaseDimensions:
    clearance: float = 0.02
    wall_thickness: float = 1.3
    pin_radius: float = 0.5

    pattern_depth: float = 0.2

    case_height_z: float = Choc.bottom_housing.height_z + Choc.posts.post_height_z
    keywell_height_z: float = Choc.base.thickness_z + Choc.upper_housing.height_z + Choc.stem.height_z + Choc.cap.height_z


class DualityWaveCase:
    dims = CaseDimensions()
    pinkie = PinkieDimensions()
    ring = RingFingerDimensions()
    middle = MiddleFingerDimensions()
    pointer = PointerFingerDimensions()
    inner = InnerFingerDimensions()
    thumb = ThumbDimensions()
    keycols = [pinkie, ring, middle, pointer, inner, thumb]

    def __init__(self, with_knurl=False, debug=False):
        self.with_knurl = with_knurl
        self.debug = debug

        self.wall_height = Choc.bottom_housing.height_z + Choc.posts.post_height_z

        self.create_case()

        self.create_accessories()

    def create_case(self):
        print("Creating case...")

        with BuildSketch() as key_holes:
            for keycol in self.keycols:
                with Locations(*keycol.locs):
                    Rectangle(Choc.bottom_housing.width_x, Choc.bottom_housing.depth_y, rotation=keycol.rotation)
            push_object(key_holes, name="key_holes") if self.debug else None
            
        with BuildSketch() as outline:
            base_width_x = 107
            base_length_y = 85
            thumb_container_height_y = 25
            circle_radius = 39.9

            with Locations((base_width_x/2 - 21.5, base_length_y/2 - 12.9)):
                Rectangle(base_width_x, base_length_y)
            with Locations((self.thumb.locs[1].position.X-10, self.thumb.locs[1].position.Y + thumb_container_height_y/2 + 1.5)):
                Rectangle(2*Choc.cap.width_x + 10, thumb_container_height_y + 21.5, rotation=self.thumb.rotation)
            with Locations((base_width_x + circle_radius - 21.5, self.thumb.locs[1].position.Y + 35.5)):
                Circle(circle_radius, mode=Mode.SUBTRACT)

            outline = outline.sketch

            push_object(outline, name="outline") if self.debug else None

        with BuildPart() as self.case:
            self.case.name = "Case"

            with BuildSketch() as walls:
                add(outline)
            extrude(amount=-self.wall_height-self.dims.wall_thickness)

            if self.with_knurl: 
                print("Adding knurl...")
                tops = self.case.faces().filter_by(Axis.Z)
                walls = self.case.faces().filter_by(lambda f: f not in tops).sort_by(Axis.X, reverse=True)
                self.create_knurl(distance=10 if self.debug else 1.5, width_x=200, height_y=50)
                for i, wall in enumerate(walls):
                    print(f"  Projecting pattern to wall {i+1} of {len(walls)}")
                    push_object(wall, name=f"wall_{i}") if self.debug else None
                    faces, pattern = self.project_to_face(self.knurl.rotate(Axis.X, 90), wall)
                    push_object(pattern, name=f"pattern_{i}") if self.debug else None
                    for i, face in enumerate(faces):
                        thicken(to_thicken=face, amount=-self.dims.pattern_depth, mode=Mode.SUBTRACT)

            with BuildSketch(Plane.XY.offset(-self.dims.wall_thickness-self.wall_height)) as keep_walls:
                    offset(
                            outline,
                            -self.dims.wall_thickness,
                            kind=Kind.INTERSECTION,
                        )
            extrude(amount=self.dims.wall_thickness, mode=Mode.SUBTRACT)
            push_object(keep_walls, name="keep_walls") if self.debug else None

            with BuildSketch() as keyholes:
                add(key_holes)
            extrude(amount=-self.dims.wall_thickness, mode=Mode.SUBTRACT)
            with BuildSketch(Plane.XY.offset(-self.dims.wall_thickness)) as keyholes:
                offset(
                        key_holes.sketch,
                        1, 
                        kind=Kind.INTERSECTION
                )
            extrude(amount=-self.wall_height, mode=Mode.SUBTRACT)
            push_object(key_holes, name="keyholes") if self.debug else None



    def project_to_face(self, pattern, face: Face) -> Vector:
        vector = face.normal_at((0,0,0))

        abs_vector = Vector(abs(vector.X), abs(vector.Y), abs(vector.Z))
        if abs_vector.X >= abs_vector.Y and abs_vector.X >= abs_vector.Z:
            direction, pattern = (Vector(-1, 0, 0), pattern.rotate(Axis.Z, 90).translate((200, 0, 0))) if vector.X >= 0 else (Vector(1, 0, 0), pattern.rotate(Axis.Z, 90).translate((-200, 0, 0)))
        elif abs_vector.Y >= abs_vector.X and abs_vector.Y >= abs_vector.Z:
            direction, pattern = (Vector(0, -1, 0), pattern.translate((0, 200, 0))) if vector.Y >= 0 else (Vector(0, 1, 0), pattern.translate((0, -200, 0)))
        else:
            direction, pattern = (Vector(0, 0, -1), pattern.translate((0, 0, 200))) if vector.Z >= 0 else (Vector(0, 0, 1), pattern.translate((0, 0, -200)))
        
        return pattern.face().project_to_shape(face, direction).faces(), pattern


    def create_knurl(self, width_x=0, height_y=0, distance=2):
        pattern_width=distance
        scale=2/3
        half_height = pattern_width / math.atan(math.radians(90))
        points = [
            (scale*-pattern_width/2, 0),
            (0, -scale*half_height),
            (scale*pattern_width/2, 0),
            (0, scale*half_height),
        ]
        with BuildSketch() as rhombus:
            Polygon(*points)

        with BuildSketch() as pattern:
            Rectangle(width_x, height_y)
            with Locations((0,0), (-pattern_width/2, half_height)):
                with GridLocations(
                    x_count=math.ceil(width_x/pattern_width)+1,
                    y_count=math.ceil(height_y/(2*half_height))+1,
                    x_spacing=pattern_width,
                    y_spacing=2*half_height,
                ):
                    add(rhombus, mode=Mode.SUBTRACT)

        self.knurl = pattern.sketch
        self.knurl.name = "Surface Pattern"
        self.knurl.distance = distance


    def create_accessories(self):
        choc = Choc()
        with BuildPart() as self.chocs:
            self.chocs.name = "Choc Switches"

            for keycol in self.keycols:
                with Locations([loc*Location((0,0,Choc.base.thickness_z)) for loc in keycol.locs]):
                    add(copy.copy(choc.model.part).rotate(Axis.Z, keycol.rotation))
        push_object(self.chocs, name="chocs")

        xiao = Xiao()
        xiao.model = xiao.model.part\
            .rotate(Axis.X, 180)\
            .translate((-5, 62, -self.dims.wall_thickness))
        push_object(xiao.model, name="xiao")

            

if __name__ == "__main__":
    set_port(3939)
    show_clear()
    set_defaults(ortho=True, default_edgecolor="#121212", reset_camera=Camera.KEEP)
    set_colormap(ColorMap.seeded(colormap="rgb", alpha=1, seed_value="wave"))

    knurl = True
    case = DualityWaveCase(with_knurl=knurl, debug=True)

    push_object(case.case) if hasattr(case, "case") else None
    show_objects() 