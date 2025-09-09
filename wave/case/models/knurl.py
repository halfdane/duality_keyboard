from build123d import *
import math
import copy
from dataclasses import dataclass


@dataclass
class KnurlDimensions:
    height_y = 4.62
    width_x = 8

class Knurl:
    dims = KnurlDimensions()
    knurl = None
    negative_knurl = None

    def __init__(self):
        with BuildPart() as knurl:
            with Locations((0,0, 0.1)):
                Box(self.dims.width_x, self.dims.height_y, 1.1)
            l1 = self \
                .create_snaking_lines(distance=2, rotation_angle=30) \
                .translate((0, 0, 1))

            sidelength = 2*math.sqrt(3) / 3
            with BuildSketch(l1 ^ 0) as profile1:
                Triangle(a=sidelength, b=sidelength, c=sidelength, rotation=60)

            t=profile1.sketch.translate((0, 0, -1/3))

            groove = sweep(path=l1, sections=t, mode=Mode.PRIVATE)
            mirrored = mirror(groove, Plane.YZ, mode=Mode.PRIVATE)
            add(groove, mode=Mode.SUBTRACT)
            add(mirrored, mode=Mode.SUBTRACT)

        with BuildPart() as negative_knurl:
            with Locations((0,0, 0.1)):
                Box(self.dims.width_x, self.dims.height_y, 1.1)
            add(knurl.part, mode=Mode.SUBTRACT)
        
        self.knurl = knurl
        self.negative_knurl = negative_knurl
        # show_all()

    def create_stamp(self, x, y):
        locs= GridLocations(self.dims.width_x, self.dims.height_y, math.ceil(x/self.dims.width_x), math.ceil(y/self.dims.height_y))
        return Compound([copy.copy(self.knurl.part).locate(loc) for loc in locs])

    def create_negative_stamp(self, x, y):
        locs= GridLocations(self.dims.width_x, self.dims.height_y, math.ceil(x/self.dims.width_x), math.ceil(y/self.dims.height_y))
        return Compound([copy.copy(self.negative_knurl.part).locate(loc) for loc in locs])

    def create_snaking_lines(self, distance=2, rotation_angle=0):    
        face_width=self.dims.width_x
        face_height=self.dims.height_y
        with BuildLine() as line:
            y_positions = [-face_height/2 + i * distance for i in range(-1, int(face_height // distance) + 2)]

            polyline_points = []
            for i, y in enumerate(y_positions):
                if i % 2 == 0:  # Even rows: left to right
                    start_point = (-face_width, y)
                    end_point = (face_width, y)
                else:  # Odd rows: right to left
                    start_point = (face_width, y)
                    end_point = (-face_width, y)

                polyline_points.extend([start_point, end_point])
            
            FilletPolyline(*polyline_points, radius=distance/3)

        return line.line.rotate(Axis.Z, rotation_angle)

    def read_knurl(self):
        # knurl.step is relative to this file
        this_dir = __file__.rsplit("/", 1)[0]
        part = import_step(this_dir + "/knurl.step")
        return part

# main method
if __name__ == "__main__":
    import time
    from ocp_vscode import *

    start_time = time.time()

    set_port(3939)
    show_clear()
    set_defaults(ortho=True, default_edgecolor="#121212", reset_camera=Camera.KEEP)
    set_colormap(ColorMap.seeded(colormap="rgb", alpha=1, seed_value="wave"))

    print(f"Setup time: {time.time() - start_time:.3f}s")

    symbol_start = time.time()
    triangle_side = 12
    with BuildSketch() as symbol:
        triangle=Triangle(a=triangle_side, b=triangle_side, c=triangle_side, mode=Mode.PRIVATE)
        larger_triangle=triangle.scale(1.1)
        with Locations(larger_triangle.vertices()):
            Circle(triangle_side/3)
        add(triangle, mode=Mode.SUBTRACT)
    print(f"Symbol creation time: {time.time() - symbol_start:.3f}s")

    knurl_start = time.time()
    knurl = Knurl()
    print("read knurl")
    print(f"Knurl creation time: {time.time() - knurl_start:.3f}s")

    k = knurl.knurl
    width_x = 44.1
    height_y = 57.9

    stamp_start = time.time()
    stamp = knurl.create_stamp(width_x, height_y)
    negative_stamp = knurl.create_negative_stamp(height_y, width_x)
    print(f"Stamp creation time: {time.time() - stamp_start:.3f}s")

    build_start = time.time()
    with BuildPart() as top_stamp:
        with BuildPart():
            add(symbol)
            extrude(amount=1.3)
            add(negative_stamp.rotate(axis=Axis.Z, angle=90), mode=Mode.SUBTRACT)
        with BuildPart():
            with BuildSketch(Plane.XY):
                Rectangle(width_x, height_y)
                add(symbol, mode=Mode.SUBTRACT)
            extrude(amount=1.3)
            add(stamp, mode=Mode.SUBTRACT)
    print(f"Build time: {time.time() - build_start:.3f}s")
    
    total_time = time.time() - start_time
    print(f"Total execution time: {total_time:.3f}s")
    show_all()