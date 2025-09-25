if __name__ == "__main__":
    import sys, os
    # add parent directory to path
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
choc_xy = choc_x + choc_y

@dataclass
class PinkieDimensions(KeyCol):
    rotation: float = 8
    pos: Vector = Vector(21.5, 12.8 )
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
    pos: Vector = InnerFingerDimensions.locs[0] + (-6.3, -17.8)
    rot = Vector(-2*rotation, rotation)

    locs: list[Vector] = (
        Vector(pos),
        Vector(pos + choc_x + choc_x/rot.X + choc_y/rot.Y + (-0.4, -0.5)),
    )

class Keys:
    
    pinkie = PinkieDimensions()
    ring = RingFingerDimensions()
    middle = MiddleFingerDimensions()
    pointer = PointerFingerDimensions()
    inner = InnerFingerDimensions()
    thumb = ThumbDimensions()

    finger_cols = [pinkie, ring, middle, pointer, inner]
    keycols: list[KeyCol] = [*finger_cols, thumb]



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
            # with Locations(keycol.locs) as l:
            #     Sphere(1)
        # with Locations(keys.thumb.locs[0], keys.thumb.locs[1]) as l:
        #     Sphere(radius=1)
        with Locations(keys.thumb.locs[1]) as l:
            Sphere(radius=1) 


    show_all()