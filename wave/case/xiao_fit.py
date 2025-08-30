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
        self.width_y = Xiao.board.depth_y + 3 * self.dims.wall_thickness + Choc.bottom_housing.width_x
        self.length_x = Xiao.board.width_x + 2 * self.dims.wall_thickness
        
        self.switchplate = self.create_switchplate()
        self.keywell = self.create_keywell()


    def create_switchplate(self):
        choc_hole_size = Choc.bottom_housing.width_x + 2 * self.dims.clearance
        key_x = self.width_y/2 - choc_hole_size/2 - self.dims.wall_thickness
        wall_height = Choc.bottom_housing.height_z + Choc.posts.post_height_z

        with BuildPart() as case:
            with BuildSketch() as base:
                Rectangle(self.length_x, self.width_y)
            extrude(amount=self.dims.wall_thickness)

            with BuildSketch() as keyhole:
                with Locations((0, key_x)):
                    Rectangle(choc_hole_size, choc_hole_size)
            extrude(amount=self.dims.wall_thickness, mode=Mode.SUBTRACT)

            with BuildSketch() as walls:
                outer=Rectangle(self.length_x, self.width_y)
                offset(
                    outer,
                    -self.dims.wall_thickness,
                    mode=Mode.SUBTRACT,
                    kind=Kind.INTERSECTION,
                )
            extrude(amount=-wall_height)

            usb_face = case.faces().sort_by(Axis.Y)[0]
            with BuildSketch(usb_face) as usb_hole:
                usb_z_position = wall_height/2 - Xiao.usb.height_z/2 - self.dims.wall_thickness - Xiao.board.thickness_z/2
                with Locations((0, usb_z_position)):
                    RectangleRounded(Xiao.usb.width_x + 2*self.dims.clearance, Xiao.usb.height_z+2*self.dims.clearance, radius=Xiao.usb.radius+self.dims.clearance)
                with Locations((Xiao.usb.width_x/2+1, usb_z_position+1)):
                    Circle(0.5)
            extrude(amount=-7, mode=Mode.SUBTRACT)

        with BuildPart() as keywell:
            bottom_left = (-self.length_x/2, -self.width_y/2 )
            bottom_right = (self.length_x/2, -self.width_y/2)  

            top_right = (self.length_x/2, self.width_y/2)

            keywell_top_right = (Choc.cap.width_x/2-self.dims.clearance, self.width_y/2)
            keywell_bottom_right = (Choc.cap.width_x/2-self.dims.clearance, self.width_y/2 - Choc.cap.length_y)
            keywell_top_left = (-Choc.cap.width_x/2+self.dims.clearance, self.width_y/2)
            keywell_bottom_left = (-Choc.cap.width_x/2+self.dims.clearance, self.width_y/2 - Choc.cap.length_y)

            top_left = (-self.length_x/2, self.width_y/2)
                
            
            with Locations(): 
                with BuildSketch():
                    Polygon(
                        bottom_left, bottom_right, top_right,
                        keywell_top_right, keywell_bottom_right, 
                        keywell_bottom_left, keywell_top_left,
                        top_left
                    )

            extrude(amount=Choc.base.thickness_z + Choc.upper_housing.height_z + Choc.stem.height_z + Choc.cap.height_z)
        
        with BuildPart() as bottom:
            with BuildSketch():
                Rectangle(self.length_x-2*self.dims.wall_thickness - 2*self.dims.clearance, self.width_y - 2*self.dims.wall_thickness - 2*self.dims.clearance)
            extrude(amount=self.dims.wall_thickness)
            usb_face_bottom = bottom.faces().sort_by(Axis.Y)[0]
            with BuildSketch(usb_face_bottom) as usb_hole_bottom:
                with Locations((0, - Xiao.usb.height_z/2 - self.dims.wall_thickness/2 + wall_height - Xiao.board.thickness_z - self.dims.clearance)):
                    RectangleRounded(Xiao.usb.width_x + 2*self.dims.clearance, Xiao.usb.height_z+2*self.dims.clearance, radius=Xiao.usb.radius+self.dims.clearance)
            extrude(amount=-6+2*self.dims.clearance, mode=Mode.SUBTRACT)




        keywell.part = keywell.part.translate((0, 0, self.dims.wall_thickness))
        bottom.part = bottom.part.translate((0, 0, -wall_height))

        xiao = Xiao()
        xiao = xiao.model.part \
            .translate((0, -self.width_y/2 + xiao.board.depth_y/2 + self.dims.wall_thickness + self.dims.clearance, self.dims.clearance)) \
            .rotate(axis=Axis.Y, angle=180) \
        
        choc = Choc()
        choc = choc.model.part\
            .translate((0, key_x, Choc.base.thickness_z + self.dims.wall_thickness))
        show_all()

        return case
    

    def create_keywell(self):
        pass


# main method
if __name__ == "__main__":
    from ocp_vscode import show, show_object, show_all, reset_show, set_port, set_defaults, get_defaults, Camera
    case = SingleSwitchXiaoCase().switchplate

    # show_all()