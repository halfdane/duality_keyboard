from build123d import *


class Symbol:
    def __init__(self):
        triangle_side = 12
        with BuildSketch() as symbol:
            triangle=Triangle(a=triangle_side, b=triangle_side, c=triangle_side, mode=Mode.PRIVATE)
            larger_triangle=triangle.scale(1.1)
            with Locations(larger_triangle.vertices()):
                Circle(triangle_side/3)
            add(triangle, mode=Mode.SUBTRACT)

        self.sketch = symbol.sketch
        
