import sys, os
if __name__ == "__main__":
    # add parent directory to path
    print(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dataclasses import dataclass
from build123d import *
from models.switch import Choc
from models.keys import ThumbDimensions, RingFingerDimensions

@dataclass
class Dimensions:
    base_width_x = 107
    base_length_y = 85
    thumb_container_height_y = 25
    circle_radius = 39.9

    switch_offset = (21.5, 12.9)

class Outline:

    dims = Dimensions()

    def __init__(self):
        thumbs = ThumbDimensions()
        ring = RingFingerDimensions()
        with BuildSketch() as outline:
            with Locations((self.dims.base_width_x/2, self.dims.base_length_y/2)):
                base=Rectangle(self.dims.base_width_x, self.dims.base_length_y)
            right_edge = base.edges().sort_by(Axis.X)[-1]
            with Locations((thumbs.locs[1].X+11.5, thumbs.locs[1].Y + self.dims.thumb_container_height_y/2 + 14.4)):
                Rectangle(2*Choc.cap.width_x + 10, self.dims.thumb_container_height_y + 21.5, rotation=thumbs.rotation)
            with Locations(right_edge @ 0.5+(self.dims.circle_radius, 0)):
                Circle(self.dims.circle_radius, mode=Mode.SUBTRACT)
            with Locations((self.dims.base_width_x/2+1, ring.y - 19)):
                Circle(44/2, mode=Mode.SUBTRACT)


        self.sketch = outline.sketch

# main method
if __name__ == "__main__":
    import time
    from ocp_vscode import *

    start_time = time.time()

    set_port(3939)
    show_clear()
    set_defaults(ortho=True, default_edgecolor="#121212", reset_camera=Camera.KEEP)
    set_colormap(ColorMap.seeded(colormap="rgb", alpha=1, seed_value="wave"))

    print(f"Setup time: {time.time() - start_time:.3f}s")
    outline = Outline()
    show_object(outline.sketch, name="outline")
