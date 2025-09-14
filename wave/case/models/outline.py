from dataclasses import dataclass
from build123d import *
from models.switch import Choc

@dataclass
class Dimensions:
    base_width_x = 107
    base_length_y = 85
    thumb_container_height_y = 25
    circle_radius = 39.9

    switch_offset = (21.5, 12.9)

class Outline:

    dims = Dimensions()

    def __init__(self, thumbs):
        with BuildSketch() as outline:
            with Locations((self.dims.base_width_x/2, self.dims.base_length_y/2)):
                Rectangle(self.dims.base_width_x, self.dims.base_length_y)
            with Locations((thumbs.locs[1].position.X+11.5, thumbs.locs[1].position.Y + self.dims.thumb_container_height_y/2 + 14.4)):
                Rectangle(2*Choc.cap.width_x + 10, self.dims.thumb_container_height_y + 21.5, rotation=thumbs.rotation)
            with Locations((self.dims.base_width_x + self.dims.circle_radius, thumbs.locs[1].position.Y + 48.4)):
                Circle(self.dims.circle_radius, mode=Mode.SUBTRACT)

        self.sketch = outline.sketch

