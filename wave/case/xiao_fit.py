from dataclasses import dataclass
from build123d import *
from models.switch import Choc
from models.xiao import Xiao
from ocp_vscode import *

set_port(3939)
show_clear()
set_defaults(ortho=True, default_edgecolor="#121212", reset_camera=Camera.KEEP)
densa = 7800 / 1e6  # carbon steel density g/mm^3
densb = 2700 / 1e6  # aluminum alloy
densc = 1020 / 1e6  # ABS
densd = 570 / 1e6   # red oak wood


# print(f"\npart mass = {p.part.volume*densa} grams")
# print(f"\npart mass = {p.part.scale(IN).volume/LB*densa} lbs")
set_colormap(ColorMap.seeded(colormap="rgb", alpha=1, seed_value="wave"))


@dataclass
class CaseDimensions:
    clearance: float = 0.02
    wall_thickness: float = 1.3
    pin_diameter: float = 1.0
    pin_clearance: float = 0.02

class SingleSwitchXiaoCase:
    dims = CaseDimensions()

    def __init__(self):
        self.width = Xiao.board.depth_y + 3 * self.dims.wall_thickness + Choc.bottom_housing.width_x
        self.length = Xiao.board.width_x + 2 * self.dims.wall_thickness
        
        self.switchplate = self.create_switchplate()
        self.keywell = self.create_keywell()


    def create_switchplate(self):
        choc_hole_size = Choc.bottom_housing.width_x + 2 * self.dims.clearance
        key_x = self.width/2 - choc_hole_size/2 - self.dims.wall_thickness
        wall_height = Choc.bottom_housing.height_z + Choc.posts.post_height_z + self.dims.wall_thickness

        with BuildPart() as switchplate:
            with BuildSketch() as base:
                Rectangle(self.length, self.width)
            extrude(amount=self.dims.wall_thickness)

            with BuildSketch() as keyhole:
                with Locations((0, key_x)):
                    Rectangle(choc_hole_size, choc_hole_size)
            extrude(amount=self.dims.wall_thickness, mode=Mode.SUBTRACT)

            with BuildSketch() as walls:
                outer=Rectangle(self.length, self.width)
                offset(
                    outer,
                    -self.dims.wall_thickness,
                    mode=Mode.SUBTRACT,
                    kind=Kind.INTERSECTION,
                )
            extrude(amount=wall_height)

        with BuildPart(Plane(base.faces().sort_by(Axis.Z)[0])) as keywell:
            top_left = (-self.length/2, -self.width/2)
            top_right = (self.length/2, -self.width/2)
            bottom_right = (self.length/2, self.width/2)

            keywell_bottom_right = (Choc.cap.width_x/2, self.width/2)
            keywell_top_right = (Choc.cap.width_x/2, self.width/2 - Choc.cap.length_y)
            keywell_top_left = (-Choc.cap.width_x/2, self.width/2 - Choc.cap.length_y)
            keywell_bottom_left = (-Choc.cap.width_x/2, self.width/2)

            bottom_left = (-self.length/2, self.width/2)
            with BuildSketch():
                Polygon(
                    top_left, top_right, bottom_right, 
                    keywell_bottom_right, keywell_top_right,
                    keywell_top_left, keywell_bottom_left,
                    bottom_left
                )

            extrude(amount=-5)





        innerFrontSide = Plane(switchplate.faces().sort_by(Axis.Y)[1])
        xiao = Xiao()
        xiao = innerFrontSide*xiao.model.part \
            .translate((0, xiao.board.depth_y/2, -wall_height/2+self.dims.wall_thickness/2)) \
            .rotate(axis=Axis.X, angle=90)
        choc = Choc()
        choc = choc.model.part.translate((0, key_x, Choc.base.thickness_z)).rotate(axis=Axis.Y, angle=180)
        show_all()

        return switchplate
    

    def create_keywell(self):
        pass


# main method
if __name__ == "__main__":
    from ocp_vscode import show, show_object, show_all, reset_show, set_port, set_defaults, get_defaults, Camera
    case = SingleSwitchXiaoCase().switchplate
