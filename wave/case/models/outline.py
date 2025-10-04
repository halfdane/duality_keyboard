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
    base: Vector = Vector(107, 92)

class Outline:

    dims = Dimensions()

    def __init__(self, wall_thickness=1.8):
        self.wall_thickness = wall_thickness

        self.cirque_recess_radius = 22
        self.cirque_recess_position = Vector(52, -5)

        self.bottom_left = Vector(0, 0)
        self.top_left = Vector(0, self.dims.base.Y)
        self.top_right = Vector(self.dims.base.X, self.dims.base.Y)
        self.mid_right = Vector(self.dims.base.X, self.dims.base.Y/2)

        self.thumb_cluster_horizontal = Choc.cap.d.X/2 + wall_thickness + 1
        self.thumb_cluster_vertical = Choc.cap.d.Y/2 + wall_thickness + 1

        self.thumb_bottom_left = Keys.thumb.locs[0] + Vector(-self.thumb_cluster_horizontal, -self.thumb_cluster_vertical).rotate(Axis.Z, Keys.thumb.rotation)
        self.thumb_bottom_right = Keys.thumb.locs[1] + Vector(self.thumb_cluster_horizontal, -self.thumb_cluster_vertical).rotate(Axis.Z, Keys.thumb.rotation)
        self.thumb_top_right = Keys.thumb.locs[1] + Vector(self.thumb_cluster_horizontal, self.thumb_cluster_vertical + wall_thickness).rotate(Axis.Z, Keys.thumb.rotation)
        self.thumb_top_left = Keys.thumb.locs[0] + Vector(-self.thumb_cluster_horizontal, self.thumb_cluster_vertical + wall_thickness).rotate(Axis.Z, Keys.thumb.rotation)

        self.sketch = self.create_outline()
        self.inner_sketch = self.create_inner_outline(-self.wall_thickness)
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
                rect_y = 15
                with Locations(self.cirque_recess_position):
                    Circle(self.cirque_recess_radius)
                with Locations(self.cirque_recess_position + (0, self.cirque_recess_radius - rect_y/2)):
                    RectangleRounded(25, rect_y, radius=rect_y/2 - 0.01, rotation=180)
            fillet(vertices(), radius=1)
            if offset_by != 0:
                offset(amount=offset_by)
                fillet(vertices(), radius=1)

        return inner_outline.sketch
        
    def create_keywell_outline(self):
        with BuildSketch() as keywell_outline:
            x = Choc.cap.d.X +1
            y = Choc.cap.d.Y + 1
            for keycol in Keys.finger_cols:
                with Locations(keycol.locs):
                    Rectangle(x, y, rotation=keycol.rotation)
            

            offset_y = 4
            with Locations(Keys.thumb.locs[0] + Vector(0, offset_y/2).rotate(Axis.Z, Keys.thumb.rotation)):
                Rectangle(x, y + offset_y, rotation=Keys.thumb.rotation)
            offset_y = 2
            with Locations(Keys.thumb.locs[1] + Vector(0, offset_y/2).rotate(Axis.Z, Keys.thumb.rotation)):
                Rectangle(x, y + offset_y, rotation=Keys.thumb.rotation)

            with Locations(self.cirque_recess_position):
                Circle(self.cirque_recess_radius +self.wall_thickness,  mode=Mode.SUBTRACT)


            # manual fillet between pinkie and ring finger
            pinkie_line = Line(Keys.pinkie.locs[2] + Vector(x/2, y/2).rotate(Axis.Z, Keys.pinkie.rotation),
                                Keys.pinkie.locs[2] + Vector(x/2, -y/2).rotate(Axis.Z, Keys.pinkie.rotation), mode=Mode.PRIVATE)
            ring_line = Line(Keys.ring.locs[2] + Vector(-x/2, y).rotate(Axis.Z, Keys.ring.rotation),
                                Keys.ring.locs[2] + Vector(-x/2, -y).rotate(Axis.Z, Keys.ring.rotation), mode=Mode.PRIVATE)
            pinkie_pos = pinkie_line@0.7
            perpendicular_line_to_pinkie = Line(pinkie_pos, pinkie_pos + Vector(100,0).rotate(Axis.Z, Keys.pinkie.rotation), mode=Mode.PRIVATE)
            cross = perpendicular_line_to_pinkie.intersect(ring_line)
            final_line = Line(pinkie_pos, cross, mode=Mode.PRIVATE)
            a = SagittaArc(start_point=final_line@1, end_point=final_line@0, sagitta=final_line.length/2)
            with BuildLine() as line:
                add(a)
                l1 = Line(a@1, a@1 + Vector(0, -20))
                l2 = Line(l1@1, l1@1 + Vector(10, 0))
                l3 = Line(l2@1, a@0)
            make_face()
        return keywell_outline.sketch
    
    def create_keywell_thumb_addition(self):
        w_x = Vector(self.wall_thickness/2, 0).rotate(Axis.Z, Keys.thumb.rotation)
        w_y = Vector(0, self.wall_thickness/2).rotate(Axis.Z, Keys.thumb.rotation)

        with BuildSketch() as thumb_addition:
            with Locations(Keys.thumb.locs):
                with Locations(Vector(2, -self.wall_thickness).rotate(Axis.Z, Keys.thumb.rotation)):
                    Rectangle(Choc.cap.d.X +1, Choc.cap.d.Y +1 + 2*self.wall_thickness, rotation=Keys.thumb.rotation)

        return thumb_addition.sketch


# main method
if __name__ == "__main__":
    import time
    from ocp_vscode import *

    start_time = time.time()

    set_port(3939)
    show_clear()
    set_defaults(ortho=True, default_edgecolor="#121212", reset_camera=Camera.KEEP)
    set_colormap(ColorMap.accent())

    print(f"Setup time: {time.time() - start_time:.3f}s")
    outline = Outline()

    keys = Keys()
    with BuildSketch() as key_holes:
        for keycol in keys.keycols:
            with BuildSketch():
                with Locations(keycol.locs):
                    Rectangle(Choc.below.d.X, Choc.below.d.Y, rotation=keycol.rotation)

    sketch = outline.sketch
    inner_sketch = outline.inner_sketch
    keywell = outline.keywell_sketch
    thumb_addition = outline.create_keywell_thumb_addition()

    show_all()


