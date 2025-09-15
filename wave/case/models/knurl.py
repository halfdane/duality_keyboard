from build123d import *
import math
from ocp_vscode import *

class Knurl:

    def __init__(self, debug=False):
        self.debug = debug

    def patternize(self, walls, pattern_depth=0.5, distance=1.5):
        for i, wall in enumerate(walls):
            print(f"  Projecting pattern to wall {i} of {len(walls)}")
            push_object(wall, name=f"wall_{i}") if self.debug else None
            width, height = max(wall.oriented_bounding_box().size.X, wall.oriented_bounding_box().size.Z), wall.oriented_bounding_box().size.Y
            if height > width:
                width, height = height, width
            if width < 0.1 or height < 0.1:
                print(f"  Skipping small wall {i}")
                continue

            if wall.is_planar:
                with BuildSketch(wall) as pattern_sketch:
                    add(self.create_knurl(distance=distance, width_x=width, height_y=height))
                push_object(pattern_sketch, name=f"planar_pattern_{i}") if self.debug else None
                extrude(to_extrude=pattern_sketch.sketch, amount=-pattern_depth, mode=Mode.SUBTRACT)
            else:
                faces, pattern = self.project_to_face(
                    self.create_knurl(distance=distance, width_x=200, height_y=200)\
                        .rotate(Axis.X, 90), 
                        wall)
                push_object(pattern, name=f"curved_pattern_{i}") if self.debug else None
                for i, face in enumerate(faces):
                    thicken(to_thicken=face, amount=-pattern_depth, mode=Mode.SUBTRACT)

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


    def create_knurl(self, width_x=0, height_y=0, distance=2, offset:Vector=Vector(0,0,0)):
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

        return pattern.sketch

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


    show_all()