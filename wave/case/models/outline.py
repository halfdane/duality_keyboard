if __name__ == "__main__":
    import sys, os
    # add parent directory to path
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dataclasses import dataclass
import math
from build123d import *
from models.switch import Choc
from models.keys import Keys

choc_x = Vector(Choc.cap.d.X, 0)
choc_y = Vector(0, Choc.cap.d.Y)
choc_xy = choc_x + choc_y

@dataclass
class Dimensions:
    base: Vector = Vector(107, 85)

class Outline:

    dims = Dimensions()

    def __init__(self):
        thumbs = Keys.thumb

        x = Choc.cap.d.X * 2.13
        y = Choc.above.d.Y * 1.45
        rotation_rad = math.radians(Keys.thumb.rotation)
        rotation_cos = math.cos(rotation_rad)
        rotation_sin = math.sin(rotation_rad)

        cirque_recess_radius = 22
        with BuildSketch():
            with Locations((54.5, -5)):
                cirque_meets_X = Circle(cirque_recess_radius).intersect(Line((0, 0), (100, -0.2)))

        bottom_left = Vector(0, 0)
        top_left = Vector(0, self.dims.base.Y)
        top_right = Vector(self.dims.base.X, self.dims.base.Y)
        mid_right = Vector(self.dims.base.X, self.dims.base.Y/2)

        cirque_recess_left = cirque_meets_X.vertices().sort_by(Axis.X)[0]
        thumb_bottom_left = cirque_meets_X.vertices().sort_by(Axis.X)[1]
        thumb_bottom_right = thumb_bottom_left + (x * rotation_cos, x * rotation_sin)
        thumb_top_right = thumbs.locs[1] + choc_x/2 + choc_y/2 + (3.9, 1)        
        thumb_top_right = thumb_bottom_right + (-y * rotation_sin, y * rotation_cos)

        with BuildSketch() as outline:
            with BuildLine() as line:
                l0 = Line(bottom_left, top_left)
                l1 = Line(top_left, top_right)
                l2 = Line(top_right, mid_right)

                a0 = TangentArc([mid_right, thumb_top_right], tangent=l2 % 1)
                l3 = Line(thumb_top_right, thumb_bottom_right)
                l4 = Line(thumb_bottom_right, thumb_bottom_left)
                a1 = RadiusArc(cirque_recess_left, thumb_bottom_left, radius=cirque_recess_radius, short_sagitta=True)
                l5 = Line(cirque_recess_left, l0@0)
            make_face()
            fillet(outline.vertices(), radius=1)

        with BuildSketch() as inner_outline:
            with BuildLine() as line:
                add(l0)
                add(l1)
                add(l2)

                add(l3)
                add(a0)
                add(l4)

                p = 0.49


                r1=RadiusArc(a1@0, a1@(p-0.1), radius=22.1, short_sagitta=True)
                r2=RadiusArc(a1@(p+0.1), a1@1, radius=22.1, short_sagitta=True)
                add(Line(r2@0, r1@1))
                add(l5)
            make_face()
            fillet(outline.vertices(), radius=1)
        
        self.sketch = outline.sketch
        self.inner_sketch = inner_outline.sketch

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
    show_object(outline.inner_sketch, name="inner_outline")




