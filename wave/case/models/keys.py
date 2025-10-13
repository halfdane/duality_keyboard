if __name__ == "__main__":
    import sys, os
    # add parent directory to path
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dataclasses import dataclass, InitVar, field
import math
from build123d import *
from models.switch import Switch


@dataclass
class KeyCol:
    switch: InitVar[Switch]
    previous: InitVar[Vector]
    rotation: float = field(init=False, default=0)
    locs: list[Vector] = field(init=False, default_factory=list)

@dataclass
class PinkieDimensions(KeyCol):
    def __post_init__(self, switch: Switch, previous: Vector):
        self.rotation = 8
        cap = Vector(switch.cap.d.X, switch.cap.d.Y)
        pos = previous
        rot = Vector(0, cap.Y).rotate(Axis.Z, self.rotation)
        self.locs = (Vector(pos), Vector(pos + rot), Vector(pos + 2*rot))

@dataclass
class RingFingerDimensions(KeyCol):
    def __post_init__(self, switch: Switch, previous: Vector):
        offset: Vector = Vector(-1.9, -2.8)
        cap = Vector(switch.cap.d.X, switch.cap.d.Y)
        pos = previous + (cap.X, cap.Y) + offset
        self.locs = (Vector(pos), Vector(pos + (0, cap.Y)), Vector(pos + (0, 2*cap.Y)))

@dataclass
class MiddleFingerDimensions(KeyCol):
    def __post_init__(self, switch: Switch, previous: Vector):
        cap = Vector(switch.cap.d.X, switch.cap.d.Y)
        pos = previous + (cap.X, cap.Y/2)
        self.locs = ( Vector(pos), Vector(pos + (0, cap.Y)), Vector(pos + (0, 2*cap.Y)) )

@dataclass
class PointerFingerDimensions(KeyCol):
    def __post_init__(self, switch: Switch, previous: Vector):
        cap = Vector(switch.cap.d.X, switch.cap.d.Y)
        pos = previous + (cap.X, -cap.Y/4)
        self.locs = ( Vector(pos), Vector(pos + (0, cap.Y)), Vector(pos + (0, 2*cap.Y)) )

@dataclass
class InnerFingerDimensions(KeyCol):
    def __post_init__(self, switch: Switch, previous: Vector):
        cap = Vector(switch.cap.d.X, switch.cap.d.Y)
        pos = previous + (cap.X, -cap.Y/4)
        self.locs = ( Vector(pos), Vector(pos + (0, cap.Y)), Vector(pos + (0, 2*cap.Y)) )

@dataclass
class ThumbDimensions(KeyCol):
    def __post_init__(self, switch: Switch, previous: Vector):
        self.rotation = -8
        cap = Vector(switch.cap.d.X, switch.cap.d.Y)
        pos = previous + (-6.3, -17.8)
        rot = Vector(cap.X, 0).rotate(Axis.Z, self.rotation)
        self.locs = (Vector(pos), Vector(pos + rot))

@dataclass
class Keys:
    switch: InitVar[Switch]

    pinkie: KeyCol = field(init=False)
    ring: KeyCol = field(init=False)
    middle: KeyCol = field(init=False)
    pointer: KeyCol = field(init=False)
    inner: KeyCol = field(init=False)
    thumb: KeyCol = field(init=False)

    finger_cols: list[KeyCol] = field(init=False)
    keycols: list[KeyCol] = field(init=False)

    def __post_init__(self, switch: Switch):
        self.pinkie = PinkieDimensions(switch=switch, previous=Vector(21, 15))
        self.ring = RingFingerDimensions(switch=switch, previous=self.pinkie.locs[0])
        self.middle = MiddleFingerDimensions(switch=switch, previous=self.ring.locs[0])
        self.pointer = PointerFingerDimensions(switch=switch, previous=self.middle.locs[0])
        self.inner = InnerFingerDimensions(switch=switch, previous=self.pointer.locs[0])
        self.thumb = ThumbDimensions(switch=switch, previous=self.inner.locs[0])

        self.finger_cols = (self.pinkie, self.ring, self.middle, self.pointer, self.inner)
        self.keycols: list[KeyCol] = [*self.finger_cols, self.thumb]



# main method
if __name__ == "__main__":
    from ocp_vscode import *

    set_port(3939)
    show_clear()
    set_defaults(ortho=True, default_edgecolor="#121212", reset_camera=Camera.KEEP)
    set_colormap(ColorMap.seeded(colormap="rgb", alpha=1, seed_value="wave"))

    from models.choc import Choc
    from models.cherry import Cherry

    def create_sizing(switch: Switch):
        keys = Keys(switch=switch)
        with BuildSketch() as sizing:
            for keycol in keys.keycols:
                with Locations(keycol.locs) as l:
                    Rectangle(switch.above.d.X*2, switch.above.d.Y*2, rotation=keycol.rotation)
                with Locations(keycol.locs) as l:
                    Circle(1, mode=Mode.SUBTRACT)
            with Locations(keys.thumb.locs[0], keys.thumb.locs[1]) as l:
                Circle(radius=1, mode=Mode.SUBTRACT)
            with Locations(keys.thumb.locs[0]) as l:
                Circle(radius=1, mode=Mode.SUBTRACT) 
            with Locations(keys.thumb.locs[1]) as l:
                Circle(radius=1 , mode=Mode.SUBTRACT) 
        return sizing.sketch

    choc_sizing = create_sizing(switch=Choc())
    # cherry_sizing = create_sizing(switch=Cherry())


    show_all()
