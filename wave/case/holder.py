#!/usr/bin/env python3
import math
from build123d import *


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
    
    
    pattern_width=1.5
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
        

    show_all()