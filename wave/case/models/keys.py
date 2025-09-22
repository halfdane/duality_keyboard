if __name__ == "__main__":
    import sys, os
    # add parent directory to path
    print(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dataclasses import dataclass
from build123d import *
from models.switch import Choc


class KeyCol:
    pos: Vector = Vector(0,0)
    rotation: float = 0
    locs: list[Vector] = []

choc_x = Vector(Choc.cap.d.X, 0)
choc_y = Vector(0, Choc.cap.d.Y)

@dataclass
class PinkieDimensions(KeyCol):
    rotation: float = 8
    pos: Vector = Vector(21.5, 13.5)
    rot: Vector = choc_y - choc_x/rotation - choc_y/rotation/(2*rotation) - choc_x/rotation/(2*rotation)
    locs: list[Vector] = (
        Vector(pos),
        Vector(pos + rot),
        Vector(pos + 2*rot)
    )

@dataclass
class RingFingerDimensions(KeyCol):
    offset: Vector = Vector(-1.9, -2.8)
    pos = PinkieDimensions.pos + choc_x + choc_y + offset
    rotation: float = 0
    locs: list[Vector] = (
        Vector(pos), 
        Vector(pos + choc_y), 
        Vector(pos + 2*choc_y)
    )

@dataclass
class MiddleFingerDimensions(KeyCol):
    pos = RingFingerDimensions.pos + choc_x + choc_y/2
    rotation: float = 0
    locs: list[Vector] = (
        Vector(pos), 
        Vector(pos + choc_y), 
        Vector(pos + 2*choc_y)
    )

@dataclass
class PointerFingerDimensions(KeyCol):
    pos = MiddleFingerDimensions.pos + choc_x - choc_y/4
    rotation: float = 0
    locs: list[Vector] = (
        Vector(pos), 
        Vector(pos + choc_y), 
        Vector(pos + 2*choc_y)
    )

@dataclass
class InnerFingerDimensions(KeyCol):
    pos = PointerFingerDimensions.pos + choc_x - choc_y/4
    rotation: float = 0
    locs: list[Vector] = (
        Vector(pos), 
        Vector(pos + choc_y), 
        Vector(pos + 2*choc_y)
    )

@dataclass
class ThumbDimensions(KeyCol):
    rotation: float = -8
    pos: Vector = Vector(InnerFingerDimensions.locs[0].X,
                    InnerFingerDimensions.locs[0].Y)- choc_y \
                        - choc_x/rotation + choc_y/rotation

    rot: Vector = 0.5*choc_y/rotation

    locs: list[Vector] = (
        Vector(pos - choc_x/2 - rot + 0.5*choc_y/rotation/rotation + choc_x/rotation/rotation),
        Vector(pos + choc_x/2 + 2*rot + 2*choc_y/rotation/rotation - choc_x/rotation/2)
    )

class Keys:
    
    def __init__(self):
        self.pinkie = PinkieDimensions()
        self.ring = RingFingerDimensions()
        self.middle = MiddleFingerDimensions()
        self.pointer = PointerFingerDimensions()
        self.inner = InnerFingerDimensions()
        self.thumb = ThumbDimensions()        

        self.finger_cols = [self.pinkie, self.ring, self.middle, self.pointer, self.inner]
        self.keycols: list[KeyCol] = [*self.finger_cols, self.thumb]



# main method
if __name__ == "__main__":
    from ocp_vscode import *

    set_port(3939)
    show_clear()
    set_defaults(ortho=True, default_edgecolor="#121212", reset_camera=Camera.KEEP)
    set_colormap(ColorMap.seeded(colormap="rgb", alpha=1, seed_value="wave"))

    keys = Keys()
    with BuildPart() as key_holes:
        for keycol in keys.keycols:
            with BuildSketch():
                with Locations(keycol.locs) as l:
                    Rectangle(Choc.below.d.X, Choc.below.d.Y, rotation=keycol.rotation)
            extrude(amount=-5)
            with Locations(keycol.locs) as l:
                Sphere(1)
        with Locations((keys.thumb.locs[0] + keys.thumb.locs[1])/2) as l:
            Sphere(radius=1)

    show_all()