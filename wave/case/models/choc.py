if __name__ == "__main__":
    import sys, os
    # add parent directory to path
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dataclasses import dataclass
from build123d import *
from models.model_types import RectDimensions, RoundDimensions, PosAndDims
from models.switch import Switch

@dataclass
class BaseDimensions:
    d : RectDimensions = RectDimensions(15, 15, 0.8)

@dataclass
class BottomHousingDimensions:
    d : RectDimensions = RectDimensions(13.8, 13.8, 2.2)

@dataclass
class PostDimensions:
    center : PosAndDims = PosAndDims(p=Vector(0,0), d=RoundDimensions(1.6, 2.65))
    
    a1: PosAndDims = PosAndDims(p=Vector(5.5,0), d=RoundDimensions(0.9, 2.65))
    a2: PosAndDims = PosAndDims(p=Vector(-5.5,0), d=RoundDimensions(0.9, 2.65))

    p1: PosAndDims = PosAndDims(p=Vector(0,5.9), d=RoundDimensions(0.2, 3))
    p2: PosAndDims = PosAndDims(p=Vector(-5,3.8), d=RoundDimensions(0.2, 3))

    posts: tuple[PosAndDims] = (center, a1, a2, p1, p2)


@dataclass
class ClampDimensions:
    d: RectDimensions = RectDimensions(0.35, 3.154, 0.9)
    offset_between: float = 3.5

@dataclass
class UpperHousingDimensions:
    d: RectDimensions = RectDimensions(13.6, 13.8, 2.5)

@dataclass
class StemDimensions:
    d: RectDimensions = RectDimensions(10, 4.5, 2.5)    
    ext_d: RectDimensions = RectDimensions(3, 1.2, 0)

@dataclass
class CapDimensions:
    d: RectDimensions = RectDimensions(18, 17, 2.5)
    d_without_space: RectDimensions = RectDimensions(17.45, 16.571, 2.25)

@dataclass
class AboveDimensions:
    d: RectDimensions = RectDimensions(
        BaseDimensions.d.X,
        BaseDimensions.d.Y,
        BaseDimensions.d.Z + UpperHousingDimensions.d.Z + StemDimensions.d.Z + CapDimensions.d.Z
    )


@dataclass
class BelowDimensions:
    d: RectDimensions = RectDimensions(
        BottomHousingDimensions.d.X,
        BottomHousingDimensions.d.Y,
        BottomHousingDimensions.d.Z + max([post.d.Z for post in PostDimensions.posts])
    )

class Choc(Switch):
    base = BaseDimensions()
    bottom_housing = BottomHousingDimensions()
    posts = PostDimensions()
    clamps = ClampDimensions()
    upper_housing = UpperHousingDimensions()
    stem = StemDimensions()
    cap = CapDimensions()

    above = AboveDimensions()
    below = BelowDimensions()

    clamp_clearance_z: float = BottomHousingDimensions.d.Z - ClampDimensions.d.Z

    def __init__(self, show_model=False):
        with BuildPart() as self.model:
            with BuildPart() as main_housing_base:
                with Locations((0, 0, +self.base.d.Z / 2)):
                    Box(self.base.d.X, self.base.d.Y, self.base.d.Z)

            with BuildPart(main_housing_base.faces().sort_by(Axis.Z)[0]) as bottom_housing:
                with Locations((0, 0, self.bottom_housing.d.Z / 2)):
                    Box(self.bottom_housing.d.X, self.bottom_housing.d.Y, self.bottom_housing.d.Z)

            with BuildPart(bottom_housing.faces().sort_by(Axis.Z)[0]) as posts:
                for post in self.posts.posts:
                    with Locations(post.p + (0, 0, -post.d.Z / 2)):
                        Cylinder(post.d.radius, post.d.Z)

            with BuildPart(bottom_housing.faces().filter_by(Axis.X)) as snap_in_clamps:
                with Locations(((self.bottom_housing.d.Z-self.clamps.d.Z)/2, self.clamps.offset_between, self.clamps.d.X/2), 
                            ((self.bottom_housing.d.Z-self.clamps.d.Z)/2, -self.clamps.offset_between, self.clamps.d.X/2)):
                    Box(self.clamps.d.Z, self.clamps.d.Y, self.clamps.d.X)

            with BuildPart(main_housing_base.faces().sort_by(Axis.Z)[-1]) as upper_housing:
                with Locations((0, 0, self.upper_housing.d.Z / 2)):
                    Box(self.upper_housing.d.X, self.upper_housing.d.Y, self.upper_housing.d.Z)

            with BuildPart(upper_housing.faces().sort_by(Axis.Z)[-1]) as stem:
                with Locations((0, 0, self.stem.d.Z / 2)):
                    Box(self.stem.d.X, self.stem.d.Y, self.stem.d.Z)
                with Locations((0, -(self.stem.d.Y+self.stem.ext_d.Y)/2, self.stem.d.Z / 2)):
                    Box(self.stem.ext_d.X, self.stem.ext_d.Y, self.stem.d.Z)

            with BuildPart() as cap:
                with BuildSketch(stem.faces().sort_by(Axis.Z)[-1]):
                    with Locations((0, 0.05)):
                        RectangleRounded(self.cap.d_without_space.X, self.cap.d_without_space.Y, 2)
                extrude(amount=self.cap.d.Z)
                fillet(cap.faces().sort_by(Axis.Z)[-1].edges(), 1.5)
                s = 40
                with Locations((0, 0, s+6.7)):
                    Sphere(s, mode=Mode.SUBTRACT, rotation=(90, 0, 0))

        if show_model:
            from ocp_vscode import show_all
            show_all()



# main method
if __name__ == "__main__":
    from ocp_vscode import show_object, set_defaults, Camera
    set_defaults(ortho=True, default_edgecolor="#121212", reset_camera=Camera.KEEP)
    switch = Choc(show_model=True)
    # show_object(switch.model, name="Kailh Choc Switch")
