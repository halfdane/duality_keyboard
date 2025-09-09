#!/usr/bin/env python3
from build123d import *

def create_snaking_lines(distance=2, rotation_angle=0, width_x=0, height_y=0):    
    face_width=width_x
    face_height=height_y

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
    snake_face = offset(line.line, 0.2*distance)
    with BuildSketch() as sketch:
        add(snake_face.rotate(Axis.Z, rotation_angle))
        make_face()

        add(snake_face.rotate(Axis.Z, -rotation_angle))
        make_face()

    return sketch.sketch

def the_line_test():
    with BuildLine() as heyy:
        r = Line((0,0,0), (0,0,20))
        s = Line((0,12,0), (0,0,-20))
        add(r)
        add(s)
        add(Line(r@0, s@0))
    lol = offset(heyy.line, 7)
    return lol

if __name__ == "__main__":
    import time
    from ocp_vscode import *
    

    start_time = time.time()

    set_port(3939)
    show_clear()
    set_defaults(ortho=True, default_edgecolor="#121212", reset_camera=Camera.KEEP)
    set_colormap(ColorMap.seeded(colormap="rgb", alpha=1, seed_value="wave"))

    width_x=44.1
    height_y=57.9
    depth_z=20
    snake = create_snaking_lines(distance=2, rotation_angle=30, width_x=width_x, height_y=height_y)

    lol = the_line_test()

    x_offset = -4
    y_offset = 10
    z_offset = 7

    def chamfer_this(edge: Edge):
        start = edge@0
        end = edge@1
        return \
            start.X == end.X == (x_offset - width_x/2) and \
            start.Y != end.Y and \
            start.Z != end.Z

    thing_cutter = snake\
        .rotate(Axis.Y, 90)\
        .translate((x_offset - width_x/2, y_offset, z_offset))
    with BuildPart() as thing:
        with Locations((x_offset, y_offset, z_offset)):
            Box(width_x, height_y, depth_z)
        cutface = thing.faces().sort_by(Axis.X)[0]
        extrude(thing_cutter, amount=1, mode=Mode.SUBTRACT)



    total_time = time.time() - start_time
    print(f"Total execution time: {total_time:.3f}s")

    show_all()