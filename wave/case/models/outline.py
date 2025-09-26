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

    def __init__(self, wall_thickness=1.8):
        self.wall_thickness = wall_thickness

        self.cirque_recess_radius = 22
        self.cirque_recess_position = Vector(54, -5)

        self.bottom_left = Vector(0, 0)
        self.top_left = Vector(0, self.dims.base.Y)
        self.top_right = Vector(self.dims.base.X, self.dims.base.Y)
        self.mid_right = Vector(self.dims.base.X, self.dims.base.Y/2)

        thumb_cluster_horizontal = Choc.cap.d.X/2 + wall_thickness
        thumb_cluster_vertical = Choc.cap.d.Y/2 + wall_thickness
        
        self.thumb_bottom_left = Keys.thumb.locs[0] + Vector(-thumb_cluster_horizontal, -thumb_cluster_vertical).rotate(Axis.Z, Keys.thumb.rotation)
        self.thumb_bottom_right = Keys.thumb.locs[1] + Vector(thumb_cluster_horizontal, -thumb_cluster_vertical).rotate(Axis.Z, Keys.thumb.rotation)
        self.thumb_top_right = Keys.thumb.locs[1] + Vector(thumb_cluster_horizontal, thumb_cluster_vertical + wall_thickness).rotate(Axis.Z, Keys.thumb.rotation)
        self.thumb_top_left = Keys.thumb.locs[0] + Vector(-thumb_cluster_horizontal, thumb_cluster_vertical + wall_thickness).rotate(Axis.Z, Keys.thumb.rotation)

        self.sketch = self.create_outline()
        self.inner_sketch = self.create_inner_outline()
        self.keywell_sketch = self.create_keywell_outline()


    def create_outline(self, offset_by=0):
        with BuildSketch() as outline:
            with BuildLine() as line:
                Line(self.bottom_left, self.top_left)
                Line(self.top_left, self.top_right)
                l2 = Line(self.top_right, self.mid_right)
                TangentArc([self.mid_right, self.thumb_top_right], tangent=l2 % 1)
                Line(self.thumb_top_right, self.thumb_bottom_right)
                Line(self.thumb_bottom_right, self.thumb_bottom_left)
                Line(self.thumb_bottom_left, self.bottom_left)
            make_face()
            with Locations(self.cirque_recess_position):
                Circle(self.cirque_recess_radius, mode=Mode.SUBTRACT)
            fillet(vertices(), radius=1)
            if offset_by != 0:
                offset(amount=offset_by)
                fillet(vertices(), radius=1)
        return outline.sketch
    
    def create_inner_outline(self, offset_by=-1.8):
        with BuildSketch() as inner_outline:
            with BuildLine() as line:
                Line(self.bottom_left, self.top_left)
                Line(self.top_left, self.top_right)
                l2 = Line(self.top_right, self.mid_right)
                TangentArc([self.mid_right, self.thumb_top_right], tangent=l2 % 1)
                Line(self.thumb_top_right, self.thumb_bottom_right)
                Line(self.thumb_bottom_right, self.thumb_bottom_left)
                Line(self.thumb_bottom_left, self.bottom_left)
            make_face()
            with BuildSketch(mode=Mode.SUBTRACT): 
                with Locations(self.cirque_recess_position):
                    Circle(self.cirque_recess_radius)
                with Locations(self.cirque_recess_position + (0, self.cirque_recess_radius - self.wall_thickness/4)):
                    Rectangle(100, self.wall_thickness/2, mode=Mode.SUBTRACT, rotation=180)
            fillet(vertices(), radius=1)
            if offset_by != 0:
                offset(amount=offset_by)
                fillet(vertices(), radius=1)
        
        return inner_outline.sketch
        
    def create_keywell_outline(self):
        thumb_bottom_left = Keys.thumb.locs[0] + Vector(-Choc.cap.d.X/2, -Choc.cap.d.Y).rotate(Axis.Z, Keys.thumb.rotation)
        thumb_top_left = self.thumb_top_left + Vector(self.wall_thickness, 0).rotate(Axis.Z, Keys.thumb.rotation)

        outline = self.create_outline()
        with BuildSketch() as keywell_outline:
            add(outline)

            for keycol in Keys.finger_cols:
                with Locations(keycol.locs):
                    Rectangle(Choc.cap.d.X +1, Choc.cap.d.Y + 1, rotation=keycol.rotation, mode=Mode.SUBTRACT)
            keycol = Keys.thumb
            with Locations(keycol.locs):
                Rectangle(Choc.cap.d.X +4, Choc.cap.d.Y + 8, rotation=keycol.rotation, mode=Mode.SUBTRACT)


        return keywell_outline.sketch


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
    show_object(outline.keywell_sketch, name="keywell_outline")
