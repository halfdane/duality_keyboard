from build123d import *


class Symbol:
    def __init__(self, total_height=3):
        # The total height includes triangle height plus circle radius extending above and below
        # For equilateral triangle: height = side * sqrt(3)/2
        # Circle radius = side * radius_ratio
        circle_radius_ratio = 1/3

        # Total height = triangle_height + 2 * circle_radius
        # total_height = side * sqrt(3)/2 + 2 * side/6 = side * (sqrt(3)/2 + 1/3)
        triangle_side = total_height / (3**0.5 / 2 + 2*circle_radius_ratio)
        circle_radius = triangle_side * circle_radius_ratio  # diameter = side/3, so radius = side/6

        with BuildSketch() as symbol:
            triangle=Triangle(a=triangle_side, b=triangle_side, c=triangle_side, mode=Mode.PRIVATE)
            with Locations(triangle.vertices()):
                Circle(circle_radius)
            add(triangle.scale(0.97), mode=Mode.SUBTRACT)

        vertices = triangle.vertices()
        # Find the min/max Y coordinates including circle radius
        min_y = min(v.Y for v in vertices) - circle_radius
        max_y = max(v.Y for v in vertices) + circle_radius
        symbol_center_y = (min_y + max_y) / 2

        self.sketch = symbol.sketch.translate(Vector(0, -symbol_center_y))

# main method
if __name__ == "__main__":
    from ocp_vscode import show_object, set_defaults, Camera
    set_defaults(ortho=True, default_edgecolor="#121212", reset_camera=Camera.KEEP)
    total_height = 10
    symbol = Symbol(total_height=total_height)
    show_object(symbol.sketch, name="Symbol")
