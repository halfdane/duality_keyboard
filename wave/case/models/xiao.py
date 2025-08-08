from dataclasses import dataclass
from build123d import *

@dataclass
class BoardDimensions:
    width_x: float = 17.8
    depth_y: float = 21.0
    thickness_z: float = 1.250

@dataclass
class ProcessorDimensions:
    width_x: float = 12.5
    depth_y: float = 10.6
    height_z: float = 2.0
    forward_y: float = 1.8

@dataclass
class UsbDimensions:
    width_x: float = 8.940
    depth_y: float = 7.3
    height_z: float = 3.21
    radius: float = 1.25
    forward_y: float = -8.359

@dataclass
class SolderHoleDimensions:
    radius: float = 0.375
    spacing: float = 2.54
    holes_per_side: int = 7

@dataclass
class ComponentDimensions:
    reset_button_width_x: float = 1.6
    reset_button_depth_y: float = 2.6
    reset_button_height_z: float = 0.73
    reset_button_x: float = 5.749
    reset_button_y: float = -8.6
    
    led_width_x: float = 1.0
    led_depth_y: float = 1.0
    led_height_z: float = 0.3
    led_x: float = -5.7
    led_y: float = -7.7

class Xiao:
    board = BoardDimensions()
    processor = ProcessorDimensions()
    usb = UsbDimensions()
    solder_holes = SolderHoleDimensions()
    components = ComponentDimensions()

    def __init__(self):
        # Calculate solder hole positions
        with BuildPart() as self.model:
            with BuildPart() as board:
                with BuildSketch():
                    RectangleRounded(self.board.width_x, self.board.depth_y, 2)
                    solder_hole_offset_y = -self.board.depth_y / 2 + self.solder_holes.radius + self.solder_holes.spacing
                    for i in range(self.solder_holes.holes_per_side):
                        y = i * self.solder_holes.spacing + solder_hole_offset_y
                        with Locations((-self.board.width_x / 2 + 2*self.solder_holes.radius - 0.7, y), 
                                       (-self.board.width_x / 2 + 2*self.solder_holes.radius + 0.5, y), 
                                       (self.board.width_x / 2 - 2*self.solder_holes.radius - 0.5, y), 
                                       (self.board.width_x / 2 - 2*self.solder_holes.radius + 0.7, y)):
                            Circle(self.solder_holes.radius, mode=Mode.SUBTRACT)
                extrude(amount=self.board.thickness_z)

            with BuildPart(board.faces().sort_by(Axis.Z)[-1]):
                with Locations((0, self.usb.forward_y, self.usb.height_z/2)):
                    Box(self.usb.width_x, self.usb.depth_y, self.usb.height_z)
                fillet(edges().filter_by(Axis.Y), self.usb.radius)

                with Locations((0, self.processor.forward_y, self.processor.height_z/2)):
                    Box(self.processor.width_x, 
                        self.processor.depth_y, 
                        self.processor.height_z)

                with Locations((self.components.reset_button_x, self.components.reset_button_y, self.components.reset_button_height_z/2)):
                    Box(self.components.reset_button_width_x, self.components.reset_button_depth_y, self.components.reset_button_height_z)
            
                with Locations((self.components.led_x, self.components.led_y, self.components.led_height_z/2)):
                    Box(self.components.led_width_x, self.components.led_depth_y, self.components.led_height_z) 


# main method
if __name__ == "__main__":
    from ocp_vscode import show, show_object, show_all, reset_show, set_port, set_defaults, get_defaults, Camera
    xiao = Xiao()
    show_object(xiao.model.part, name="Builder Xiao", reset_camera=Camera.KEEP)