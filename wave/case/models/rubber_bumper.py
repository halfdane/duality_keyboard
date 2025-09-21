from build123d import *
from ocp_vscode import *
from dataclasses import dataclass

@dataclass
class BumperDimensions:
    base_z: float = 1
    dome_z: float = 1
    radius: float = 4


class RubberBumper:
    dims = BumperDimensions()

    def __init__(self):
        with BuildPart() as bumper:
            with BuildSketch(Plane.XZ):
                with BuildLine() as profile:
                    l1 = Line((0, 0), (self.dims.radius, 0))
                    l2 = Line(l1 @ 1, (self.dims.radius, self.dims.base_z))

                    a1 = SagittaArc(l2 @ 1, (-self.dims.radius, self.dims.base_z), -self.dims.dome_z, mode=Mode.PRIVATE)
                    d = ThreePointArc([a1@0, a1@0.25, a1@0.5])
                    l3 = Line(d@1, l1@0)
                make_face()
            revolve(axis=Axis.Z)

        self.model = bumper.part

# main method
if __name__ == "__main__":
    import time
    from ocp_vscode import *

    set_port(3939)
    show_clear()
    set_defaults(ortho=True, default_edgecolor="#121212", reset_camera=Camera.KEEP)
    set_colormap(ColorMap.seeded(colormap="rgb", alpha=1, seed_value="wave"))

    bumper = RubberBumper()
    show_object(bumper.model, name="bumper")