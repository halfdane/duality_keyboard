from dataclasses import dataclass
import math
import copy
from build123d import *
from models.switch import Choc
from models.xiao import Xiao



@dataclass
class CaseDimensions:
    clearance: float = 0.02
    wall_thickness: float = 1.3
    pin_diameter: float = 1.0
    pin_clearance: float = 0.02

class SingleSwitchXiaoCase:
    dims = CaseDimensions()

    def __init__(self):
        self.rows = 2
        self.cols = 2
        self.width_y = Xiao.board.depth_y + 3 * self.dims.wall_thickness + self.rows*Choc.cap.length_y
        self.length_x = max(Xiao.board.width_x, self.cols*Choc.cap.width_x) + 2 * self.dims.wall_thickness + 4*self.dims.wall_thickness + self.dims.wall_thickness
        
        self.switchplate = self.create_switchplate()
        self.keywell = self.create_keywell()


    def create_switchplate(self):
        choc_hole_size = Choc.bottom_housing.width_x + 2 * self.dims.clearance
        key_y = self.width_y/2 - (self.rows*Choc.cap.length_y)/2 + 10 * self.dims.clearance
        wall_height = Choc.bottom_housing.height_z + Choc.posts.post_height_z

        with BuildPart() as case:
            with BuildSketch() as base:
                Rectangle(self.length_x, self.width_y)
                with Locations((-self.length_x/2+2*self.dims.wall_thickness+self.dims.clearance, 0),
                               (self.length_x/2-2*self.dims.wall_thickness-self.dims.clearance, 0)):
                    Rectangle(2*self.dims.wall_thickness+2*self.dims.clearance, 20+2*self.dims.clearance, mode=Mode.SUBTRACT)
            extrude(amount=self.dims.wall_thickness)

            with BuildSketch() as keyhole:
                with Locations((0, key_y)):
                    with GridLocations(Choc.cap.width_x, Choc.cap.length_y, self.cols, self.rows):
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

            keywell_top_right = (self.cols*(Choc.cap.width_x/2+self.dims.clearance), self.width_y/2)
            keywell_bottom_right = (self.cols*(Choc.cap.width_x/2+self.dims.clearance), self.width_y/2 - self.rows*(Choc.cap.length_y +self.dims.clearance))
            keywell_top_left = (-self.cols*(Choc.cap.width_x/2+self.dims.clearance), self.width_y/2)
            keywell_bottom_left = (-self.cols*(Choc.cap.width_x/2+self.dims.clearance), self.width_y/2 - self.rows*(Choc.cap.length_y +self.dims.clearance))

            top_left = (-self.length_x/2, self.width_y/2)
            
            with BuildSketch():
                Polygon(
                    bottom_left, bottom_right, top_right,
                    keywell_top_right, keywell_bottom_right, 
                    keywell_bottom_left, keywell_top_left,
                    top_left
                )

            extrude(amount=Choc.base.thickness_z + Choc.upper_housing.height_z + Choc.stem.height_z + Choc.cap.height_z)

            keywell_holder_width_y = 20
            with BuildSketch() as keywell_holder:
                with Locations((-self.length_x/2+2*self.dims.wall_thickness+self.dims.clearance, 0),
                               (self.length_x/2-2*self.dims.wall_thickness-self.dims.clearance, 0)):
                    Rectangle(2*self.dims.wall_thickness, keywell_holder_width_y)
            extrude(amount=-wall_height + self.dims.clearance)
        
        with BuildPart() as bottom:
            bottom_width_y = self.width_y - 2*self.dims.wall_thickness - 2*self.dims.clearance
            bottom_length_x = self.length_x - 2*self.dims.wall_thickness - 2*self.dims.clearance
            with BuildSketch():
                Rectangle(bottom_length_x, bottom_width_y)
            extrude(amount=self.dims.wall_thickness)
            
            with BuildSketch(bottom.faces().sort_by(Axis.Y)[0]) as usb_hole_bottom:
                with Locations((0, - Xiao.usb.height_z/2 - self.dims.wall_thickness/2 + wall_height - Xiao.board.thickness_z - self.dims.clearance)):
                    RectangleRounded(Xiao.usb.width_x + 2*self.dims.clearance, Xiao.usb.height_z+2*self.dims.clearance, radius=Xiao.usb.radius+self.dims.clearance)
            extrude(amount=-6+2*self.dims.clearance, mode=Mode.SUBTRACT)

            with BuildSketch() as bottom_holder:
                remaining = (self.width_y - 2*self.dims.wall_thickness - keywell_holder_width_y)/2
                with Locations((bottom_length_x/2 - self.dims.wall_thickness, (bottom_width_y - remaining)/2 + self.dims.clearance),
                               (-bottom_length_x/2 + self.dims.wall_thickness, (bottom_width_y - remaining)/2 + self.dims.clearance),
                               (bottom_length_x/2 - self.dims.wall_thickness, -(bottom_width_y - remaining)/2 - self.dims.clearance),
                               (-bottom_length_x/2 + self.dims.wall_thickness, -(bottom_width_y - remaining)/2 - self.dims.clearance),):
                    Rectangle(2*self.dims.wall_thickness, remaining-2*self.dims.clearance)
            extrude(amount=wall_height-self.dims.clearance)



        keywell.part = keywell.part.translate((0, 0, self.dims.wall_thickness))
        bottom.part = bottom.part.translate((0, 0, -wall_height))

        xiao = Xiao()
        xiao = xiao.model.part \
            .translate((0, -self.width_y/2 + xiao.board.depth_y/2 + self.dims.wall_thickness + self.dims.clearance, self.dims.clearance)) \
            .rotate(axis=Axis.Y, angle=180)
        

        choc = Choc()

        locs = GridLocations(Choc.cap.width_x+self.dims.clearance, Choc.cap.length_y+self.dims.clearance, self.cols, self.rows).local_locations
        chocs = [copy.copy(choc.model.part).locate(loc * Location((0, key_y, Choc.base.thickness_z + self.dims.wall_thickness))) for loc in locs]

    
        show_all()

        # return case
    

    def create_keywell(self):
        pass


# main method
if __name__ == "__main__":
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

    case = SingleSwitchXiaoCase().switchplate

    # show_all()