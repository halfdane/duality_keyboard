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

    def __init__(self, plane=Plane.XY, clearance=0.01):
        self.plane = plane
        self.clearance = clearance

        self.model = self._create_model()
        self.reset_button_bump = self._create_reset_button_bump()
        self.usb_cut_sketch_plane = self._create_usb_cut_sketch_plane(self.model)


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

                with Locations(self.components.reset_button_d.p):
                    self.reset_button = Box(self.components.reset_button_d.d.X, self.components.reset_button_d.d.Y, self.components.reset_button_d.d.Z)

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
            with BuildLine() as line:
                l1 = Line(p+Vector(-lever_width/2, 0), p+Vector(-lever_width/2, length))
                l3 = Line(l1@0 + Vector(-lever_gap, 0), l1@1 + Vector(-lever_gap, 0))
                rl = RadiusArc(l3@1, l1@1, radius=lever_gap/2, short_sagitta=True)

                r1 = Line(p+Vector(lever_width/2, 0), p+Vector(lever_width/2, length))
                r3 = Line(r1@0 + Vector(lever_gap, 0), r1@1 + Vector(lever_gap, 0))
                rr = RadiusArc(r1@1, r3@1, radius=lever_gap/2, short_sagitta=True)

                a1 = EllipticalCenterArc((l3@0 + r3@0)/2, lever_width/2, lever_width, start_angle=180, end_angle=360)
                a2 = EllipticalCenterArc((l3@0 + r3@0)/2, lever_width/2 + lever_gap, lever_width + lever_width/4, start_angle=180, end_angle=360)

            make_face()
        return reset_sketch.sketch

    def _create_reset_button_bump(self):
        lever_width = self.reset_lever_dims.d.X
        p = self.reset_lever_dims.p
        with BuildSketch() as reset_bump:
            with Locations(p):
                Ellipse(lever_width/2, lever_width)

        return reset_bump.sketch

    def _create_usb_cut_sketch(self):
        with BuildSketch() as usb_sketch:
            with Locations((0, Xiao.dims.d.Z/2)):
                with Locations((0, Xiao.usb.d.Z/2)):
                    RectangleRounded(Xiao.usb.d.X + 2*self.clearance, Xiao.usb.d.Z+2*self.clearance, radius=Xiao.usb.radius+self.clearance)
                with Locations((Xiao.components.led_d.p.X, Xiao.components.led_d.p.Z/2 + 1)):
                    Circle(1)
        return usb_sketch.sketch

    def _create_free_usb_space_sketch(self):
        with BuildSketch() as usb_sketch:
            with Locations((0, Xiao.dims.d.Z/2)):
                with Locations((0, Xiao.usb.d.Z/2)):
                    RectangleRounded(Xiao.usb.d.X + 2*self.clearance, Xiao.usb.d.Z+2*self.clearance, radius=Xiao.usb.radius+self.clearance)
                with Locations((0, 0.25*Xiao.usb.d.Z)):
                    Rectangle(Xiao.usb.d.X + 2*self.clearance, Xiao.usb.d.Z/2+2*self.clearance)
                with Locations((Xiao.components.led_d.p.X, Xiao.components.led_d.p.Z/2 + 1)):
                    Circle(1)
                with Locations((Xiao.components.led_d.p.X+1, Xiao.components.led_d.p.Z/2 + 0.5)):
                    Rectangle(4, 1)
        return usb_sketch.sketch
    
    def _create_usb_cut_sketch_plane(self, model):
        front_dir_axis = Axis(origin=self.plane.origin, direction=self.plane.y_dir)
        boardfront:Face = model.faces().sort_by(front_dir_axis).filter_by(Axis.Y)[1]
        return boardfront
    
    def add_large_usb_cutouts(self, part: Part):
        with BuildPart() as p:
            add(part)
            with BuildSketch(self.usb_cut_sketch_plane) as cut_sketch:
                add(self._create_free_usb_space_sketch())
            extrude(to_extrude=cut_sketch.sketch, amount=7, mode=Mode.SUBTRACT)
            extrude(to_extrude=cut_sketch.sketch, amount=-(self.usb.d.Y - self.usb.forward_y + self.clearance), mode=Mode.SUBTRACT)

        return p.part

    def add_usb_cutouts(self, part: Part):
        with BuildPart() as p:
            add(part)
            with BuildSketch(self.usb_cut_sketch_plane) as cut_sketch:
                add(self._create_usb_cut_sketch())
            extrude(to_extrude=cut_sketch.sketch, amount=7, mode=Mode.SUBTRACT)
            extrude(to_extrude=cut_sketch.sketch, amount=-(self.usb.d.Y - self.usb.forward_y + self.clearance), mode=Mode.SUBTRACT)

        return p.part
    
    def add_reset_lever(self, part: Part, plane: Plane):
        with BuildPart() as p:
            add(part)
            dist = plane.origin.Z - self.plane.origin.Z + self.dims.d.Z + self.components.reset_button_d.d.Z
            with BuildSketch(plane) as lever_sketch:
                add(self._create_reset_button_lever_sketch())
            extrude(dir=plane.z_dir, amount=10, mode=Mode.SUBTRACT)

            thin_to = 1.8
            with BuildSketch(plane) as lever_thinning_sketch:
                Rectangle(self.dims.d.X-4, self.dims.d.Y-4)
                add(offset(self.reset_button_bump, amount=0.5))
                with Locations(self.reset_lever_dims.p + Vector(-0.5, self.reset_lever_dims.d.Y/2)):
                    Rectangle(self.reset_lever_dims.d.X+1, self.reset_lever_dims.d.Y+2)
            extrude(dir=plane.z_dir, amount=thin_to, mode=Mode.SUBTRACT)

            with BuildSketch(plane.offset(thin_to)) as reset_button_bump:
                add(self.reset_button_bump)
            extrude(amount=dist-thin_to, mode=Mode.ADD)


        return p.part


# main method
if __name__ == "__main__":
    from ocp_vscode import *

    xiao_plane = Plane.XY
    xiao_plane = xiao_plane.rotated((180,0,0)).move(Location((18.9, 71.7, -0.74)))
    xiao = Xiao(xiao_plane)

    set_defaults(ortho=True, default_edgecolor="#121212", reset_camera=Camera.KEEP)
    set_colormap(ColorMap.accent())

    model = xiao.model
    reset_button_lever_sketch = xiao._create_reset_button_lever_sketch()
    reset_button_bump = xiao.reset_button_bump
    free_usb_space_sketch = xiao._create_free_usb_space_sketch()

    with BuildPart(xiao_plane) as usb_cut_3d:
        with BuildSketch(xiao.usb_cut_sketch_plane) as cut_sketch:
            cut = xiao._create_usb_cut_sketch()
            add(cut)
        extrude(amount=7, mode=Mode.ADD)
    # usb_cut.part = xiao.plane * usb_cut.part

    bumper_plane = xiao_plane.offset(Xiao.dims.d.Z + Xiao.usb.d.Z)
    reset_lever = xiao.add_reset_lever(model, bumper_plane)

    with BuildSketch(xiao_plane, bumper_plane) as plane_sketch:
        Circle(10)

    show_all()
