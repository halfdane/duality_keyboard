import sys, os
if __name__ == "__main__":
    # add parent directory to path
    print(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dataclasses import dataclass
from build123d import *
from models.switch import Choc
from models.keys import Keys, ThumbDimensions

@dataclass
class Dimensions:
    base_width_x = 107
    base_length_y = 85
    thumb_container_height_y = 25
    circle_radius = 39.9

    switch_offset = (21.5, 12.9)

class Outline:

    dims = Dimensions()

    def __init__(self, keys = Keys(Dimensions.switch_offset), debug=False):
        thumbs = keys.thumb
        ring = keys.ring
        with BuildSketch() as outline:
            with BuildLine() as line:
                l0 = Line((0,0), (0, self.dims.base_length_y))
                l1 = Line(l0@1, (self.dims.base_width_x, self.dims.base_length_y))
                l2 = Line(l1@1, (self.dims.base_width_x, self.dims.base_length_y/2))
                half_height = (Choc.cap.length_y + 5) /2
                half_width = (Choc.cap.width_x+5) / 2
                l3 = Line((thumbs.locs[1].X + half_width + half_height/8, thumbs.locs[1].Y + half_height - half_width/8), 
                          (thumbs.locs[1].X + half_width - half_height/8, thumbs.locs[1].Y - half_height - half_width/8))
                a0 = TangentArc([l2 @ 1, l3 @ 0], tangent=l2 % 1)
                
                l4 = Line(l3@1, (thumbs.locs[0].X - half_width + half_height/8-1, (l0@0).Y-1))
                a1 = RadiusArc((33.1, (l0@0).Y), l4 @ 1, radius=22.1, short_sagitta=True)
                l5 = Line(a1@0, l0@0)
            make_face()
            fillet(outline.vertices(), radius=1)
        self.sketch = outline.sketch

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
    outline = Outline()
    show_object(outline.sketch, name="outline")
