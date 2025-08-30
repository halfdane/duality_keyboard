from build123d import *

def create_snaking_lines(face, distance=2, rotation_angle=0):
    # Get the face's bounding box to determine actual dimensions
    bbox = face.bounding_box()
    face_width = bbox.size.X
    face_height = bbox.size.Y
    
    with BuildLine(face) as line:
        y_positions = [-face_height + i * distance for i in range(int(face_height*2 // distance) + 3)]

        polyline_points = []
        for i, y in enumerate(y_positions):
            if i % 2 == 0:  # Even rows: left to right
                start_point = (-face_width*2, y)
                end_point = (face_width*2, y)
            else:  # Odd rows: right to left
                start_point = (face_width*2, y)
                end_point = (-face_width*2, y)

            polyline_points.extend([start_point, end_point])
        
        FilletPolyline(*polyline_points, radius=distance/3)


    return line.line.rotate(Axis.Z, rotation_angle)

def knurl(face, cut_tool_side=1):
    l1 = create_snaking_lines(face, distance=cut_tool_side*2, rotation_angle=30)
    with BuildSketch(l1 ^ 0) as profile1:
        with Locations((0, -(3**0.5 / 8) * cut_tool_side)):
            Triangle(a=cut_tool_side, b=cut_tool_side, c=cut_tool_side, rotation=180)
    groove = sweep(path=l1, sections=profile1.sketch, mode=Mode.PRIVATE)
    mirrored = mirror(groove, Plane.YZ, mode=Mode.PRIVATE)
    add(groove, mode=Mode.SUBTRACT)
    add(mirrored, mode=Mode.SUBTRACT)


# main method
if __name__ == "__main__":
    from ocp_vscode import *

    set_port(3939)
    show_clear()
    set_defaults(ortho=True, default_edgecolor="#121212", reset_camera=Camera.KEEP)
    densa = 7800 / 1e6  # carbon steel density g/mm^3
    densb = 2700 / 1e6  # aluminum alloy
    densc = 1020 / 1e6  # ABS
    densd = 570 / 1e6   # red oak wood


    # print(f"\npart mass = {p.part.volume*densa} grams")
    # print(f"\npart mass = {p.part.scale(IN).volume/LB*densa} lbs")
    set_colormap(ColorMap.seeded(colormap="rgb", alpha=1, seed_value="wave"))


    totalheight = 100
    totalwidth = 100
    with BuildPart() as body:
        with BuildSketch(Plane.XY) as base:
            Rectangle(totalwidth, totalheight)
        extrude(amount=10)

        cutface = sorted(body.faces(), key=lambda f: f.area)[-1] 
        knurl(cutface)

    # body.part = body.part.rotate(Axis.X, 45).rotate(Axis.Y, 45).rotate(Axis.Z, 45)
    show_all()