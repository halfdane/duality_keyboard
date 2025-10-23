if __name__ == "__main__":
    import sys, os
    # add parent directory to path
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dataclasses import dataclass
import math
from build123d import *
from models.switch import Switch
from models.keys import Keys
import copy

@dataclass
class Dimensions:
    base: Vector = Vector(107, 92)

class Outline:

    dims = Dimensions()

    def __init__(self, switch: Switch, keys: Keys, wall_thickness=1.8):
        self.switch = switch
        self.keys = keys
        
        d = self.get_direction2max_and_angle(keys.finger_cols)
        d["top"] = d["top"][0] + 10, d["top"][1]

        self.wall_thickness = wall_thickness

        self.cirque_recess_radius = 22
        self.cirque_recess_position = Vector(52, -5)
        
        d_x = switch.cap.d.X / 2 + 2*wall_thickness
        d_y = switch.cap.d.Y / 2 + 2*wall_thickness

        self.bottom_left = Vector(d["left"][0], d["bottom"][0]) \
            - Vector(d_x, 0) - Vector(0, d_y)
        self.top_left = Vector(d["left"][0], d["top"][0]) \
            - Vector(d_x, 0) + Vector(0, d_y)
        self.top_right = Vector(d["right"][0], d["top"][0]) \
            + Vector(d_x, 0) + Vector(0, d_y)
        self.bottom_right = Vector(d["right"][0], d["bottom"][0]) \
            + Vector(d_x, 0) - Vector(0, d_y)
        self.mid_right = (self.top_right + self.bottom_right) / 2

        self.thumb_cluster_horizontal = switch.cap.d.X / 2 + wall_thickness + 0.5
        self.thumb_cluster_vertical = switch.cap.d.Y / 2 + wall_thickness + 0.5

        all_thumbs = [self.keys.thumb]
        # among the thumbs that are on the right side, find the one that is the topmost
        rightmost_thumb = max(all_thumbs, key=lambda k: max(loc.X for loc in k.locs))
        # among the thumbs that are on the left side, find the one


        self.thumb_bottom_left = self.keys.thumb.locs[0] + Vector(-self.thumb_cluster_horizontal, -self.thumb_cluster_vertical).rotate(Axis.Z, self.keys.thumb.rotation)
        self.thumb_bottom_right = self.keys.thumb.locs[1] + Vector(self.thumb_cluster_horizontal, -self.thumb_cluster_vertical).rotate(Axis.Z, self.keys.thumb.rotation)
        self.thumb_top_right = self.keys.thumb.locs[1] + Vector(self.thumb_cluster_horizontal, self.thumb_cluster_vertical + wall_thickness).rotate(Axis.Z, self.keys.thumb.rotation)
        self.thumb_top_left = self.keys.thumb.locs[0] + Vector(-self.thumb_cluster_horizontal, self.thumb_cluster_vertical + wall_thickness).rotate(Axis.Z, self.keys.thumb.rotation)

        self.sketch = self.create_outline()
        self.inner_sketch = self.create_inner_outline(-self.wall_thickness)
        self.keywell_sketch = self.create_keywell_outline()

    def get_direction2max_and_angle(self, columns):
        direction2maxAndAngle: dict[str, tuple[int, int]] = {
            "bottom": (math.inf, 0),
            "top": (-math.inf, 0),
            "left": (math.inf, 0),
            "right": (-math.inf, 0),
        }
        for key_col in columns:
            for loc in key_col.locs:
                if loc.X < direction2maxAndAngle["left"][0]:
                    direction2maxAndAngle["left"] = (loc.X, key_col.rotation)
                if loc.X > direction2maxAndAngle["right"][0]:
                    direction2maxAndAngle["right"] = (loc.X, key_col.rotation)
                if loc.Y < direction2maxAndAngle["bottom"][0]:
                    direction2maxAndAngle["bottom"] = (loc.Y, key_col.rotation)
                if loc.Y > direction2maxAndAngle["top"][0]:
                    direction2maxAndAngle["top"] = (loc.Y, key_col.rotation)
        return direction2maxAndAngle


    def create_outline(self, offset_by=0):
        with BuildSketch() as outline:
            with BuildLine() as line:
                Line(self.bottom_left, self.top_left)
                Line(self.top_left, self.top_right)
                l2 = Line(self.top_right, self.mid_right)
                TangentArc([self.mid_right, self.thumb_top_right], tangent=l2 % 1)
                


                # Line(self.thumb_top_right, self.thumb_bottom_right)
                # Line(self.thumb_bottom_right, self.thumb_bottom_left)
                # Line(self.thumb_bottom_left, self.bottom_left)
            make_face()
            # with Locations(self.cirque_recess_position):
            #     Circle(self.cirque_recess_radius, mode=Mode.SUBTRACT)
            # fillet(vertices(), radius=1)
            # if offset_by != 0:
            #     offset(amount=offset_by)
            #     fillet(vertices(), radius=1)
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
            for keycol in self.keys.finger_cols:
                with BuildSketch():
                    with Locations(keycol.locs):
                        Rectangle(self.switch.above.d.X+4, self.switch.above.d.Y+3, rotation=keycol.rotation)
            most_right = vertices().sort_by(Axis.X)[-1]
            for keycol in [self.keys.thumb]:
                with BuildSketch():
                    for loc in keycol.locs:
                        # if location is further right than base.X, only draw half the rectangle
                        if loc.X > most_right.center().X:
                            with Locations(loc):
                                with Locations((0,0)):
                                    Rectangle(self.switch.above.d.X+4, self.switch.above.d.Y+3, rotation=keycol.rotation)
                        else:
                            with Locations(loc):
                                with Locations((0, 3)):
                                    Rectangle(self.switch.above.d.X+4, self.switch.above.d.Y+3+6, rotation=keycol.rotation)
            
            # remove small areas
            for wire in wires().filter_by(lambda w: w.area < 20):
                with BuildLine() as line:
                    add(wire)
                make_face()

            # iterate over pairs of edges and fillet acute angles
            t = edges()
            pairs = zip(t, t[1:] + t[:1])
            for e1, e2 in pairs:
                angle = e1.tangent_at(0).get_angle(e2.tangent_at(0))
                if angle < 30 or angle > 150:
                    v = vertices().filter_by(lambda v: v in e1.vertices() and v in e2.vertices())[0]
                    fillet(v, radius=0.5)
        return keywell_outline.sketch

# main method
if __name__ == "__main__":
    from ocp_vscode import *
    set_port(3939)
    show_clear()
    set_defaults(ortho=True, default_edgecolor="#121212", reset_camera=Camera.KEEP)
    set_colormap(ColorMap.accent())

    from models.choc import Choc
    from models.cherry import Cherry

    switch = Choc()
    keys = Keys(switch=switch)
    outline = Outline(switch=switch, keys=keys, wall_thickness=1.8)
    with BuildSketch() as choc_key_holes:
        for keycol in keys.keycols:
            with BuildSketch():
                with Locations(keycol.locs):
                    Rectangle(switch.below.d.X, switch.below.d.Y, rotation=keycol.rotation)
    choc_sketch = outline.sketch
    choc_inner_sketch = outline.inner_sketch
    choc_keywell = outline.keywell_sketch

    # switch = Cherry()
    # keys = Keys(switch=switch)
    # outline = Outline(switch=switch, keys=keys, wall_thickness=1.8)
    # with BuildSketch() as cherry_key_holes:
    #     for keycol in keys.keycols:
    #         with BuildSketch():
    #             with Locations(keycol.locs):
    #                 Rectangle(switch.below.d.X, switch.below.d.Y, rotation=keycol.rotation)
    # cherry_sketch = outline.sketch
    # cherry_inner_sketch = outline.inner_sketch
    # cherry_keywell = outline.keywell_sketch

    show_all()


