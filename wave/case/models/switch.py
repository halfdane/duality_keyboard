import os
from build123d import *

class KailhChoc:
    """
    Kailh Choc low profile switch model
    Dimensions from: https://www.kailh.com/products/kailh-choc-1350-scissor-switch
    """
    
    # Main dimensions
    WIDTH = 15.0
    LENGTH = 15.0
    TOTAL_HEIGHT = 11.0
    
    # Plate cutout dimensions
    CUTOUT_WIDTH = 13.8
    CUTOUT_LENGTH = 13.8
    
    # Pin dimensions
    PIN_DIAMETER = 3.0
    PIN_SPACING = 5.08  # Standard Choc pin spacing (mm)
    
    def __init__(self, position=(0, 0, 0), rotation=0):
        self.position = position
        self.rotation = rotation
        
    def build(self):
        cwd = os.getcwd()

        print("Current Working Directory:", cwd)

        filename = 'wave/case/assets/Kailh_PG1353.STEP'
        if not os.path.exists(filename):
            raise FileNotFoundError(f"Switch STEP file not found: {filename}")
        
        switch = Pos(0, 0, 2.6) * Rot(90, -90, 0) * \
            import_step(filename)

        return switch

    def get_cutout(self, plate_thickness=1.5):
        """Generate a switch cutout for a plate"""
        with BuildPart() as cutout:
            with Locations(self.position):
                # Plate cutout
                Box(self.CUTOUT_WIDTH, self.CUTOUT_LENGTH, plate_thickness)
                
                # Pin holes
                with Locations((0, -self.PIN_SPACING/2, 0), (0, self.PIN_SPACING/2, 0)):
                    Cylinder(self.PIN_DIAMETER/2, plate_thickness)
        
        # If rotation is needed, apply it to the entire cutout
        if self.rotation != 0:
            cutout.part = cutout.part.rotated(Vector(0, 0, 1), self.rotation)
            
        return cutout.part



if __name__ == "__main__":
    # Example usage
    switch = KailhChoc(position=(0, 0, 0), rotation=0)
    switch_model = switch.build()
    
    # Display the switch model
    try:
        # Try to import from parent module
        import sys
        sys.path.append("/home/tvollert/halfdane/duality_keyboard/wave/case")
        from prototype import display_model
        display_model(switch_model)
    except ImportError:
        # Fallback to basic display method
        try:
            show(switch_model)
        except NameError:
            try:
                from build123d.jupyter_tools import display
                display(switch_model)
            except ImportError:
                from IPython.display import display
                display(switch_model)

