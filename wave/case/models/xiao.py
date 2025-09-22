if __name__ == "__main__":
    import sys, os
    # add parent directory to path
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dataclasses import dataclass
from build123d import *
from models.model_types import RectDimensions, RoundDimensions, PosAndDims

@dataclass
class BoardDimensions:
    d: RectDimensions = RectDimensions(17.8, 21.0, 1.250)

@dataclass
class ProcessorDimensions:
    d: RectDimensions = RectDimensions(12.5, 10.6, 2.0)
    forward_y: float = 1.8

@dataclass
class UsbDimensions:
    d: RectDimensions = RectDimensions(8.940, 7.0, 3.21)
    radius: float = 1.25
    forward_y: float = 1

@dataclass
class SolderHoleDimensions:
    radius: float = 0.375
    spacing: float = 2.54
    holes_per_side: int = 7

@dataclass
class ComponentDimensions:
    reset_button_d: PosAndDims = PosAndDims(p=Vector(5.749, -8.6, 0.73/2), d=RectDimensions(1.6, 2.6, 0.73))
    led_d: PosAndDims = PosAndDims(p=Vector(-5.7, -7.7, 0.3/2), d=RectDimensions(1.0, 1.0, 0.3))
    loading_light_d: PosAndDims = PosAndDims(p=Vector(-5.65, -9.7, 0.1/2), d=RectDimensions(1.1, 0.5, 0.1))

class Xiao:
    dims = BoardDimensions()
    processor = ProcessorDimensions()
    usb = UsbDimensions()
    solder_holes = SolderHoleDimensions()
    components = ComponentDimensions()

    def __init__(self, show_model=False, show_step_file=False):
        # Calculate solder hole positions
        with BuildPart() as model:
            with BuildPart() as board:
                with BuildSketch():
                    RectangleRounded(self.dims.d.X, self.dims.d.Y, 2)
                    solder_hole_offset_y = -self.dims.d.Y / 2 + self.solder_holes.radius + self.solder_holes.spacing
                    for i in range(self.solder_holes.holes_per_side):
                        y = i * self.solder_holes.spacing + solder_hole_offset_y
                        with Locations((-self.dims.d.X / 2 + 2*self.solder_holes.radius - 0.7, y), 
                                       (-self.dims.d.X / 2 + 2*self.solder_holes.radius + 0.5, y), 
                                       (self.dims.d.X / 2 - 2*self.solder_holes.radius - 0.5, y), 
                                       (self.dims.d.X / 2 - 2*self.solder_holes.radius + 0.7, y)):
                            Circle(self.solder_holes.radius, mode=Mode.SUBTRACT)
                extrude(amount=self.dims.d.Z)

            with BuildPart(board.faces().sort_by(Axis.Z)[-1]) as parts:
                with Locations((0, self.usb.d.Y/2-self.dims.d.Y/2-self.usb.forward_y, self.usb.d.Z/2)) as usb:
                    Box(self.usb.d.X, self.usb.d.Y, self.usb.d.Z)
                fillet(edges().filter_by(Axis.Y), self.usb.radius)

                with Locations((0, self.processor.forward_y, self.processor.d.Z/2)) as processor:
                    Box(self.processor.d.X, self.processor.d.Y, self.processor.d.Z)

                with Locations(self.components.reset_button_d.p) as reset_button:
                    Box(self.components.reset_button_d.d.X, self.components.reset_button_d.d.Y, self.components.reset_button_d.d.Z)

                with Locations(self.components.led_d.p) as led:
                    Box(self.components.led_d.d.X, self.components.led_d.d.Y, self.components.led_d.d.Z)

                with Locations(self.components.loading_light_d.p) as loading_light:
                    Box(self.components.loading_light_d.d.X, self.components.loading_light_d.d.Y, self.components.loading_light_d.d.Z)
        self.model = model.part

        if show_model:
            from ocp_vscode import show, show_object, show_all, reset_show, set_port, set_defaults, get_defaults, Camera
            set_defaults(ortho=True, default_edgecolor="#121212", reset_camera=Camera.KEEP)
            show_object(self.model, name="Xiao Board", options={"color": "blue", "opacity": 0.5}) 


    def create_usb_cut(self, clearance=0.5):
        with BuildPart() as usb_cut:
            with BuildSketch(Plane.XZ.offset(-Xiao.dims.d.Y/2)) as usb_sketch:
                usb_z_position = -Xiao.dims.d.Z - Xiao.usb.d.Z/2
                with Locations((0, usb_z_position)):
                    RectangleRounded(Xiao.usb.d.X + 2*clearance, Xiao.usb.d.Z+2*clearance, radius=Xiao.usb.radius+clearance)
                with Locations((-Xiao.usb.d.X/2-1, usb_z_position+1)):
                    Circle(0.5)
            extrude(amount=-7, mode=Mode.ADD)
        
        return usb_cut.part+mirror(usb_cut.part, Plane.XZ.offset(-Xiao.dims.d.Y/2))




# main method
if __name__ == "__main__":
    xiao = Xiao(show_model=True, show_step_file=True).model