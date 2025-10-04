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
    d : RectDimensions = RectDimensions(15.6, 15.6, 1)

@dataclass
class BottomHousingDimensions:
    d : RectDimensions = RectDimensions(13.95, 13.95, 5)

@dataclass
class PostDimensions:
    center : PosAndDims = PosAndDims(p=Vector(0,0), d=RoundDimensions(3.85/2, 2.85))
    
    p1: PosAndDims = PosAndDims(p=Vector(3.8,-2.54), d=RoundDimensions(0.4, 3))
    p2: PosAndDims = PosAndDims(p=Vector(-2.54,-5.08), d=RoundDimensions(0.4, 3))

    posts: tuple[PosAndDims] = (center, p1, p2)


@dataclass
class ClampDimensions:
    p: PosAndDims = PosAndDims(p=Vector(13.95/2, 0, -1.9), 
                               d=RectDimensions((15.03-13.95)/2, 4.0, 0.8))

@dataclass
class UpperHousingDimensions:
    d: RectDimensions = RectDimensions(13.95, 13.95, 11-6)

@dataclass
class StemDimensions:
    d: RectDimensions = RectDimensions(4.0, 4.0, 4.1)

@dataclass
class CapDimensions:
    d: RectDimensions = RectDimensions(18.1, 18.1, 12.3)
    d_without_space: RectDimensions = RectDimensions(18, 18, d.Z)

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

class Cherry(Switch):
    base = BaseDimensions()
    bottom_housing = BottomHousingDimensions()
    posts = PostDimensions()
    clamps = ClampDimensions()
    upper_housing = UpperHousingDimensions()
    stem = StemDimensions()
    cap = CapDimensions()

    above = AboveDimensions()
    below = BelowDimensions()
    clamp_clearance_z: float = BottomHousingDimensions.d.Z - ClampDimensions.p.p.Z

    def __init__(self, show_model=False, show_step_file=False):
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

            with BuildPart() as snap_in_clamps:
                with Locations((self.clamps.p.p.X + self.clamps.p.d.X/2, self.clamps.p.p.Y, self.clamps.p.p.Z),
                               (-self.clamps.p.p.X - self.clamps.p.d.X/2, self.clamps.p.p.Y, self.clamps.p.p.Z)):
                    Box(self.clamps.p.d.X, self.clamps.p.d.Y, self.clamps.p.d.Z)

            with BuildPart(main_housing_base.faces().sort_by(Axis.Z)[-1]) as upper_housing:
                with Locations((0, 0, self.upper_housing.d.Z / 2)):
                    Box(self.upper_housing.d.X, self.upper_housing.d.Y, self.upper_housing.d.Z)

            with BuildPart(upper_housing.faces().sort_by(Axis.Z)[-1]) as stem:
                with Locations((0, 0, self.stem.d.Z / 2)):
                    Box(self.stem.d.X, self.stem.d.Y, self.stem.d.Z)

            with BuildPart() as key_cap:
                # Start with the plan of the key cap and extrude it
                with BuildSketch() as plan:
                    Rectangle(18 * MM, 18 * MM)
                extrude(amount=10 * MM, taper=15)
                # Create a dished top
                with Locations((0, -3 * MM, 47 * MM)):
                    Sphere(40 * MM, mode=Mode.SUBTRACT, rotation=(90, 0, 0))
                # Fillet all the edges except the bottom
                fillet(
                    key_cap.edges().filter_by_position(Axis.Z, 0, 30 * MM, inclusive=(False, True)),
                    radius=1 * MM,
                )
                # Hollow out the key by subtracting a scaled version
                scale(by=(0.925, 0.925, 0.85), mode=Mode.SUBTRACT)

                # Add supporting ribs while leaving room for switch activation
                with BuildSketch(Plane(origin=(0, 0, 4 * MM))):
                    Rectangle(15 * MM, 0.5 * MM)
                    Rectangle(0.5 * MM, 15 * MM)
                    Circle(radius=5.5 * MM / 2)
                # Extrude the mount and ribs to the key cap underside
                extrude(until=Until.NEXT)
                # Find the face on the bottom of the ribs to build onto
                rib_bottom = key_cap.faces().filter_by_position(Axis.Z, 4 * MM, 4 * MM)[0]
                # Add the switch socket
                with BuildSketch(rib_bottom) as cruciform:
                    Circle(radius=5.5 * MM / 2)
                    Rectangle(4.1 * MM, 1.17 * MM, mode=Mode.SUBTRACT)
                    Rectangle(1.17 * MM, 4.1 * MM, mode=Mode.SUBTRACT)
                extrude(amount=3.5 * MM, mode=Mode.ADD)
            key_cap = key_cap.part.translate((0, 0, self.upper_housing.d.Z))

        if show_model:
            from ocp_vscode import show_all
            show_all()



# main method
if __name__ == "__main__":
    from ocp_vscode import show_object, set_defaults, Camera
    set_defaults(ortho=True, default_edgecolor="#121212", reset_camera=Camera.KEEP)
    switch = Cherry(show_model=True)
    # show_object(switch.model, name="Cherry Switch")
