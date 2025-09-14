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
class BottomDimensions:
    size_z: float = 1.3
    keyplate_offset: float = 1.3

@dataclass
class KeyplateDimensions:
    size_z: float = Choc.bottom_housing.height_z + Choc.posts.post_height_z + BottomDimensions.size_z
    switch_clamp_clearance: float = size_z - Choc.clamps.clearance_z

    xiao_position: Location = (1.5 + Xiao.board.width_x/2, Outline.dims.base_length_y - Xiao.board.depth_y/2-1.5, -1.3)

@dataclass
class CaseDimensions:
    clearance: float = 0.02
    pin_radius: float = 0.5
    pattern_depth: float = 0.2

    keywell_height_z: float = Choc.base.thickness_z + Choc.upper_housing.height_z + Choc.stem.height_z + Choc.cap.height_z


class DualityWaveCase:
    dims = CaseDimensions()
    bottom_dims = BottomDimensions()
    keyplate_dims = KeyplateDimensions()
    keys = Keys()
    outline = Outline(keys.thumb)

    def __init__(self, with_knurl=False, debug=False):
        self.with_knurl = with_knurl
        self.debug = debug

        self.create_keyplate()

        self.create_accessories()

    def create_keyplate(self):
        print("Creating keyplate...")

        with BuildSketch() as key_holes:
            with Locations(self.outline.dims.switch_offset):
                for keycol in self.keys.keycols:
                    with Locations(keycol.locs):
                        Rectangle(Choc.bottom_housing.width_x, Choc.bottom_housing.depth_y, rotation=keycol.rotation)
        push_object(key_holes, name="key_holes") if self.debug else None

        with BuildPart() as self.keyplate:
            self.keyplate.name = "Keyplate"

            with BuildSketch() as walls:
                add(self.outline.sketch)
            extrude(amount=-self.keyplate_dims.size_z)

            if self.with_knurl: 
                print("Adding knurl...")
                tops = self.keyplate.faces().filter_by(Axis.Z)
                walls = self.keyplate.faces().filter_by(lambda f: f not in tops).sort_by(Axis.X, reverse=True)
                self.create_knurl(distance=10 if self.debug else 1.5, width_x=200, height_y=50)
                for i, wall in enumerate(walls):
                    print(f"  Projecting pattern to wall {i+1} of {len(walls)}")
                    push_object(wall, name=f"wall_{i}") if self.debug else None
                    faces, pattern = self.project_to_face(self.knurl.rotate(Axis.X, 90), wall)
                    push_object(pattern, name=f"pattern_{i}") if self.debug else None
                    for i, face in enumerate(faces):
                        thicken(to_thicken=face, amount=-self.dims.pattern_depth, mode=Mode.SUBTRACT)

            with BuildSketch(Plane.XY.offset(-self.keyplate_dims.size_z)) as bottom_walls:
                    offset(
                            self.outline.sketch,
                            -self.bottom_dims.keyplate_offset,
                            kind=Kind.INTERSECTION,
                        )
            extrude(amount=self.bottom_dims.size_z, mode=Mode.SUBTRACT)
            push_object(bottom_walls, name="bottom_walls") if self.debug else None

            with BuildSketch() as keyholes:
                add(key_holes)
            extrude(amount=-Choc.clamps.clearance_z, mode=Mode.SUBTRACT)
            with BuildSketch(Plane.XY.offset(-Choc.clamps.clearance_z)) as keyholes_with_space:
                offset(
                        key_holes.sketch,
                        1, 
                        kind=Kind.INTERSECTION
                )
            extrude(amount=-self.keyplate_dims.size_z, mode=Mode.SUBTRACT)



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

            with Locations(self.outline.dims.switch_offset):
                for keycol in self.keys.keycols:
                    with Locations(keycol.locs):
                        add(copy.copy(choc.model.part).rotate(Axis.Z, keycol.rotation))
        push_object(self.chocs, name="chocs")

        xiao = Xiao()
        xiao.model = xiao.model.part\
            .rotate(Axis.X, 180)\
            .translate(self.keyplate_dims.xiao_position)
        push_object(xiao.model, name="xiao")

            

if __name__ == "__main__":
    set_port(3939)
    show_clear()
    set_defaults(ortho=True, default_edgecolor="#121212", reset_camera=Camera.KEEP)
    set_colormap(ColorMap.seeded(colormap="rgb", alpha=1, seed_value="wave"))

    knurl = False
    case = DualityWaveCase(with_knurl=knurl, debug=True)

    push_object(case.keyplate) if hasattr(case, "keyplate") else None
    show_objects() 