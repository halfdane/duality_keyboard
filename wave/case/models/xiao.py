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

@dataclass
class ResetButtonLeverDimensions:
    p: Vector = ComponentDimensions.reset_button_d.p
    d: RectDimensions = RectDimensions(2.0, 5)
    gap: float = 0.5

class Xiao:
    dims = BoardDimensions()
    processor = ProcessorDimensions()
    usb = UsbDimensions()
    solder_holes = SolderHoleDimensions()
    components = ComponentDimensions()
    reset_lever_dims = ResetButtonLeverDimensions()

    plane: Plane

    def __init__(self, plane=Plane.XY):
        self.plane = plane

        self.model = self._create_model()
        self.reset_button_lever_sketch = self._create_reset_button_lever_sketch()
        self.reset_button_bump = self._create_reset_button_bump()
        self.usb_cut_sketch = self._create_usb_cut_sketch()
        self.usb_cut_sketch_plane = self._create_usb_cut_sketch_plane(self.model)
        self.free_usb_space_sketch = self._create_free_usb_space_sketch()


    def _create_model(self):
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
            
            with BuildPart(Plane.XY.offset(self.dims.d.Z)) as usb:
                with Locations((0, self.usb.d.Y/2-self.dims.d.Y/2-self.usb.forward_y, self.usb.d.Z/2)):
                    Box(self.usb.d.X, self.usb.d.Y, self.usb.d.Z)
                fillet(edges().filter_by(Axis.Y), self.usb.radius)


            with BuildPart(Plane.XY.offset(self.dims.d.Z)) as parts:

                with Locations((0, self.processor.forward_y, self.processor.d.Z/2)) as processor:
                    Box(self.processor.d.X, self.processor.d.Y, self.processor.d.Z)

                with Locations(self.components.reset_button_d.p) as reset_button:
                    Box(self.components.reset_button_d.d.X, self.components.reset_button_d.d.Y, self.components.reset_button_d.d.Z)

                with Locations(self.components.led_d.p) as led:
                    Box(self.components.led_d.d.X, self.components.led_d.d.Y, self.components.led_d.d.Z)

                with Locations(self.components.loading_light_d.p) as loading_light:
                    Box(self.components.loading_light_d.d.X, self.components.loading_light_d.d.Y, self.components.loading_light_d.d.Z)
        return self.plane * model.part

    def _create_reset_button_lever_sketch(self):
        length = self.reset_lever_dims.d.Y
        lever_width = self.reset_lever_dims.d.X
        lever_gap = self.reset_lever_dims.gap
        p = self.reset_lever_dims.p
        with BuildSketch() as reset_sketch:
            l1 = Line(p+(-lever_width/2, 0), p+(-lever_width/2, length))
            offset(l1, amount=lever_gap, side=Side.LEFT)
            make_face()
            l2 = Line(p+(lever_width/2, 0), p+(lever_width/2, length))
            offset(l2, amount=lever_gap, side=Side.RIGHT)
            make_face()
            a = RadiusArc(l1@0, l2@0, radius=lever_width/2, short_sagitta=False)
            offset(a, amount=lever_gap, side=Side.RIGHT)
            make_face()

        return self.plane * reset_sketch.sketch

    def _create_reset_button_bump(self):
        lever_width = self.reset_lever_dims.d.X
        p = self.reset_lever_dims.p
        with BuildSketch() as reset_bump:
            with Locations(p):
                a = Circle(lever_width/2)

        return self.plane * reset_bump.sketch

    def _create_usb_cut_sketch(self, clearance=0.5):
        with BuildSketch() as usb_sketch:
            with Locations((0, Xiao.dims.d.Z/2)):
                with Locations((0, Xiao.usb.d.Z/2)):
                    RectangleRounded(Xiao.usb.d.X + 2*clearance, Xiao.usb.d.Z+2*clearance, radius=Xiao.usb.radius+clearance)
                with Locations((Xiao.components.led_d.p.X, Xiao.components.led_d.p.Z/2 + 0.5)):
                    Circle(0.5)
        return usb_sketch.sketch

    def _create_free_usb_space_sketch(self, clearance=0.5):
        with BuildSketch() as usb_sketch:
            with Locations((0, Xiao.dims.d.Z/2)):
                with Locations((-0.85, Xiao.usb.d.Z/2)):
                    RectangleRounded(Xiao.usb.d.X +2.7, Xiao.usb.d.Z+2*clearance, radius=Xiao.usb.radius+clearance)
        return usb_sketch.sketch
    
    def _create_usb_cut_sketch_plane(self, model):
        front_dir_axis = Axis(origin=self.plane.origin, direction=self.plane.y_dir)
        boardfront:Face = model.faces().sort_by(front_dir_axis).filter_by(Axis.Y)[1]
        return boardfront
    
    def free_usb_space(self, part: Part):
        with BuildPart() as p:
            add(part)
            with BuildSketch(self.usb_cut_sketch_plane) as cut_sketch:
                add(self.free_usb_space_sketch)
            extrude(to_extrude=cut_sketch.sketch, amount=7, mode=Mode.SUBTRACT)

        return p.part

    def add_bumps_and_cutouts(self, part: Part, bump_height=2, ):
        with BuildPart() as p:
            add(part)
            with BuildSketch(self.usb_cut_sketch_plane) as cut_sketch:
                add(self.usb_cut_sketch)
            extrude(to_extrude=cut_sketch.sketch, amount=7, mode=Mode.SUBTRACT)
            extrude(to_extrude=cut_sketch.sketch, amount=-6.5, mode=Mode.SUBTRACT)
            
            lever_sketch = self.reset_button_lever_sketch\
                    .translate((0,0,-Xiao.dims.d.Z-Xiao.usb.d.Z))
            add(lever_sketch)
            extrude(to_extrude=lever_sketch, amount=10, mode=Mode.SUBTRACT)

            reset_button_bump = self.reset_button_bump\
                    .translate((0,0,-Xiao.dims.d.Z-Xiao.usb.d.Z))
            extrude(to_extrude=reset_button_bump, amount=-bump_height)

        return p.part


# main method
if __name__ == "__main__":
    from ocp_vscode import *

    xiao_plane = Plane.XY
    xiao_plane = xiao_plane.rotated((180,0,0)).move(Location((18.9, 71.7, -0.74)))
    xiao = Xiao(xiao_plane)

    set_defaults(ortho=True, default_edgecolor="#121212", reset_camera=Camera.KEEP)
    show_object(xiao.model, name="Xiao Board", options={"color": "lightblue", "opacity": 0.5})
    show_object(xiao.reset_button_lever_sketch, name="Reset Button Cut", options={"color": "red", "opacity": 0.5})
    show_object(xiao.reset_button_bump, name="reset bump")

    with BuildPart(xiao_plane) as usb_cut:
        with BuildSketch(xiao.usb_cut_sketch_plane) as cut_sketch:
            cut = xiao.usb_cut_sketch
            add(cut)
        show_object(cut_sketch, name="USB Cut Sketch", options={"color": "orange", "opacity": 0.5})
        extrude(amount=7, mode=Mode.ADD)
    # usb_cut.part = xiao.plane * usb_cut.part
    show_object(usb_cut.part, name="USB Cut 3D", options={"color": "green", "opacity": 0.5})
    show_object(xiao.free_usb_space_sketch, name="Free USB Space Sketch", options={"color": "purple", "opacity": 0.5})
    
