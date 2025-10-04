from build123d import *


class SpaceInvader:
    def __init__(self, total_height=16):
        pattern = [
            [0,0,1,0,0,0,0,0,1,0,0],
            [0,0,0,1,0,0,0,1,0,0,0],
            [0,0,1,1,1,1,1,1,1,0,0],
            [0,1,1,0,1,1,1,0,1,1,0],
            [1,1,1,1,1,1,1,1,1,1,1],
            [1,0,1,1,1,1,1,1,1,0,1],
            [1,0,1,0,0,0,0,0,1,0,1],
            [0,0,0,1,1,0,1,1,0,0,0]
        ]
        pixel_size = total_height / len(pattern)
        half_cols = len(pattern[0]) / 2 - 0.5
        half_rows = len(pattern) / 2 - 0.5

        border = 0
        
        with BuildSketch() as space_invader:
            locs = [((col - half_cols) * pixel_size, (half_rows - row) * pixel_size)
                    for row in range(8)
                    for col in range(11)
                    if pattern[row][col]]
            with Locations(locs):
                Rectangle(pixel_size-border, pixel_size-border)
        
        self.sketch = space_invader.sketch

# main method
if __name__ == "__main__":
    from ocp_vscode import show_object, set_defaults, Camera
    set_defaults(ortho=True, default_edgecolor="#121212", reset_camera=Camera.KEEP)
    total_height = 10
    space_invader = SpaceInvader(total_height=total_height)
    show_object(space_invader.sketch, name="Space Invader")
