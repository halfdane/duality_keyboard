if __name__ == "__main__":
    import sys, os
    # add parent directory to path
    print(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from ocp_vscode import *

from dataclasses import dataclass
from build123d import *
from models.switch import Choc
from models.keys import Keys

choc_x = Vector(Choc.cap.d.X, 0)
choc_y = Vector(0, Choc.cap.d.Y)

@dataclass
class Dimensions:
    base: Vector = Vector(107, 85)

class Outline:

    dims = Dimensions()

    def __init__(self, keys = Keys(), debug=False):
        thumbs = keys.thumb
        ring = keys.ring
        with BuildSketch() as outline:
            with BuildLine() as line:
                l0 = Line((0,0), (0, self.dims.base.Y))
                l1 = Line(l0@1, (self.dims.base.X, self.dims.base.Y))
                l2 = Line(l1@1, (self.dims.base.X, self.dims.base.Y/2))

                l30 = thumbs.locs[1] + choc_x/2 + choc_y/2 + (3.9,1.2)
                l31 = thumbs.locs[1] + choc_x/2 - choc_y/2 + (0.7,-3.7)
                l3 = Line(l30, l31)
                a0 = TangentArc([l2 @ 1, l3 @ 0], tangent=l2 % 1)

                l4 = Line(l3@1, Vector(thumbs.locs[0].X-1.5, (l0@0).Y-1) - choc_x/2)
                a1 = RadiusArc((31.5, (l0@0).Y), l4 @ 1, radius=22.1, short_sagitta=True)
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

    keys = Keys()
    with BuildSketch() as key_holes:
        for keycol in keys.keycols:
            with BuildSketch() as keycol_sketch:
                with Locations(keycol.locs) as l:
                    Rectangle(Choc.below.d.X, Choc.below.d.Y, rotation=keycol.rotation)
            add(keycol_sketch)

    show_object(outline.sketch, name="outline")
    show_object(key_holes.sketch, name="key_holes")
