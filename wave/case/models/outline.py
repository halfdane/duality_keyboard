if __name__ == "__main__":
    import sys, os
    # add parent directory to path
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import math
from build123d import *
from models.switch import Switch
from models.keys import ErgoKeys
from ergogen import Point

class Outline:
    def __init__(self, switch: Switch, keys: ErgoKeys, wall_thickness=1.8):
        self.switch = switch
        self.keys = keys
        
        self.wall_thickness = wall_thickness

        self.cirque_recess_radius = 22
        self.cirque_recess_position = Vector(30, -24)
        
        self.d_x = switch.cap.d.X / 2 + 2*wall_thickness
        self.d_y = switch.cap.d.Y / 2 + 2*wall_thickness

        self.keywell_sketch, fingers_sketch = self.create_keywell_outline()
        # find left, right, top, bottom points
        finger_outer_points = ShapeList({e.start_point() for e in fingers_sketch.edges()} | {e.end_point() for e in fingers_sketch.edges()})
        self.left = finger_outer_points.sort_by(Axis.X)[0].X - self.wall_thickness
        self.right = finger_outer_points.sort_by(Axis.X)[-1].X + self.wall_thickness
        self.bottom = finger_outer_points.sort_by(Axis.Y)[0].Y - self.wall_thickness
        self.top = finger_outer_points.sort_by(Axis.Y)[-1].Y + self.wall_thickness + 10

        self.bottom_left = Vector(self.left, self.bottom)
        self.top_left = Vector(self.left, self.top) 
        self.top_right = Vector(self.right, self.top) 
        self.bottom_right = Vector(self.right, self.bottom) 
        self.mid_right = (self.top_right + self.bottom_right) / 2

        self.sketch = self.create_outline()
        self.inner_sketch = self.create_inner_outline(-self.wall_thickness)

    def reorient_edges(self, sketch):
        """Create new sketch with consistently oriented edges."""
        edges = list(sketch.wires()[0].edges())
        ordered, remaining = [edges[0]], edges[1:]
        
        while remaining:
            end = ordered[-1].end_point()
            i = next(i for i, e in enumerate(remaining) 
                    if e.start_point() == end or e.end_point() == end)
            edge = remaining.pop(i)
            ordered.append(edge if edge.start_point() == end else edge.reversed())

        face = Face(Wire(ordered))
        
        # Counter-clockwise creates upward normal (+Z), clockwise creates downward normal (-Z)
        if face.normal_at().Z > 0:  # Clockwise - need to reverse
            ordered = [e.reversed() for e in reversed(ordered)]
        
        with BuildSketch(Plane.XY) as sk:
            make_face(Wire(ordered))
        return sk.sketch


    def create_outline(self):
        bottom_left_thumb_key = self.keys.thumb_clusters[0][0][0]
        bottom_right_thumb_key = self.keys.thumb_clusters[0][len(self.keys.thumb_clusters[0])-1][0]

        self.thumb_bottom_left = bottom_left_thumb_key.p + Vector(-self.d_x+self.wall_thickness, -self.d_y+1).rotate(Axis.Z, bottom_left_thumb_key.r)
        self.thumb_bottom_right = bottom_right_thumb_key.p + Vector(self.d_x, -self.d_y).rotate(Axis.Z, bottom_right_thumb_key.r)

        def is_crossing_keywell(t: TangentArc):
            for edge in self.keywell_sketch.edges():
                inter = t.intersect(edge)
                if inter:
                    return True
            return False
        
        with BuildSketch() as outline:
            with BuildLine() as line:
                l1 = Line(self.bottom_left, self.top_left)
                l2 = Line(self.top_left, self.top_right)
                l3 = Line(self.top_right, self.mid_right)

                # just try every top thumb key until there's one that doesn't intersect the keywell
                for thumb_col_index in range(len(self.keys.thumb_clusters[0])):
                    top_right_thumb_key = self.keys.thumb_clusters[0][thumb_col_index][len(self.keys.thumb_clusters[0][thumb_col_index])-1]
                    self.thumb_top = top_right_thumb_key.p + Vector(self.d_x, self.d_y).rotate(Axis.Z, top_right_thumb_key.r)
                    t = TangentArc([self.mid_right, self.thumb_top], tangent=l3 % 1, mode=Mode.PRIVATE)
                    if not is_crossing_keywell(t):
                        add(t)
                        break

                l4 = Line(self.thumb_top, self.thumb_bottom_left)
                l5 = Line(self.thumb_bottom_left, self.bottom_left)
            make_face()

            # add rectangles for all thumb keys to add them to the outline
            for thumb_key in self.keys.thumb_keys:
                with Locations(thumb_key.p):
                    Rectangle(2*self.d_x, 2*self.d_y, rotation=thumb_key.r)

            # position the circle in a way that it touches self.thumb_bottom_left
            # iterate over lowest keys to find a good place
            found_position = False
            for cluster in self.keys.clusters:
                if found_position:
                    break
                for col in cluster:
                    if found_position:
                        break
                    for key in col:
                        if found_position:
                            break

                        key_bottom_right = key.p + Vector(self.d_x, -self.d_y).rotate(Axis.Z, key.r)
                        midpoint = (key_bottom_right + self.thumb_bottom_left) / 2
                        chord_vec = self.thumb_bottom_left - key_bottom_right

                        loc = Vector(midpoint.X, self.cirque_recess_position.Y)
                        with Locations(loc):
                            c = Circle(self.cirque_recess_radius, mode=Mode.PRIVATE)
                        if self.cirque_recess_radius < chord_vec.length / 2 and not is_crossing_keywell(c):
                            # there's definitelly enough space for the circle here - just position it next to the thumb cluster
                            add(c, mode=Mode.SUBTRACT)
                            self.cirque_recess_position = loc
                            found_position = True
            fillet(vertices(), radius=1)
        return self.reorient_edges(outline.sketch)
    
    def create_inner_outline(self, offset_by=-1.8):
        with BuildSketch() as inner_outline:
            add(self.sketch)
            if offset_by != 0:
                offset(amount=offset_by)
                for vertex in vertices():
                    try:
                        fillet(vertex, radius=1)
                    except Exception as e:
                        #ignore fillet errors
                        pass
            with BuildSketch(mode=Mode.SUBTRACT) as help:
                rect_y = 15
                with Locations(self.cirque_recess_position + (0, self.cirque_recess_radius - rect_y/3)):
                    RectangleRounded(25, rect_y, radius=rect_y/2 - 0.01, rotation=180)

        return self.reorient_edges(inner_outline.sketch)

    def create_keywell_outline(self):
        with BuildSketch() as fingers_outline:
            for key in self.keys.finger_keys:
                with BuildSketch():
                    with Locations(key.p):
                        Rectangle(self.d_x*1.6, self.d_y*1.6, rotation=key.r)
        with BuildSketch() as thumbs_outline:
            for key in self.keys.thumb_keys:
                with BuildSketch():
                    with Locations(key.p):
                        Rectangle(self.d_x*1.6, self.d_y*1.6, rotation=key.r)

        with BuildSketch() as keywell_outline:
            add(fingers_outline)
            add(thumbs_outline)

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
                    v = vertices().filter_by(lambda v: v in e1.vertices() and v in e2.vertices())
                    if v:
                        try:
                            fillet(v[0], radius=0.7)
                        except Exception as e:
                            pass
                        # fillet(v, radius=0.7)

        return self.reorient_edges(keywell_outline.sketch), self.reorient_edges(fingers_outline.sketch)

def add_arrows(edges):
    with BuildSketch() as arrows:
        for edge in edges:
            with Locations(edge.center()):
                # get rotation angle in degrees
                angle = math.degrees(math.atan2(edge.end_point().Y - edge.start_point().Y, edge.end_point().X - edge.start_point().X))
                ArrowHead(size=5, rotation=angle)
    return arrows.sketch

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
    keys = ErgoKeys()
    outline = Outline(switch=switch, keys=keys, wall_thickness=1.8)
    with BuildSketch() as choc_key_holes:
        for key in keys.keys:
            with BuildSketch():
                with Locations(key.p):
                    Rectangle(switch.below.d.X, switch.below.d.Y, rotation=key.r)
    choc_sketch = outline.sketch
    choc_sketch_arrows = add_arrows(choc_sketch.edges())
    choc_inner_sketch = outline.inner_sketch
    choc_inner_sketch_arrows = add_arrows(choc_inner_sketch.edges())
    choc_keywell = outline.keywell_sketch
    choc_keywell_arrows = add_arrows(choc_keywell.edges())

    # # switch = Cherry()
    # # keys = Keys(switch=switch)
    # # outline = Outline(switch=switch, keys=keys, wall_thickness=1.8)
    # # with BuildSketch() as cherry_key_holes:
    # #     for keycol in keys.keycols:
    # #         with BuildSketch():
    # #             with Locations(keycol.locs):
    # #                 Rectangle(switch.below.d.X, switch.below.d.Y, rotation=keycol.rotation)
    # # cherry_sketch = outline.sketch
    # # cherry_inner_sketch = outline.inner_sketch
    # # cherry_keywell = outline.keywell_sketch

    show_all()


