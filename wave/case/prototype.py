from build123d import *
from models.switch import KailhChoc
from models.xiao import SeeedXiaoBLE
from src.wave_case import display_model


def create_prototype_case(switch_cutout, xiao_mounting):
    """Create a simple prototype case with one Kailh Choc switch and a XIAO BLE board"""
    
    # Build the case
    with BuildPart() as case:
        # Base plate
        Box(case_length, case_width, wall_thickness)
        
        # Walls
        with BuildSketch() as wall_sketch:
            Rectangle(case_length, case_width)
            Rectangle(case_length - 2*wall_thickness, case_width - 2*wall_thickness)
        
        extrude(wall_sketch.sketch, amount=case_height)
        
        # Top plate with switch cutout
        with Locations((0, 0, case_height - plate_thickness)):
            Box(case_length, case_width, plate_thickness)
        
        # Cut switch hole and mounting holes using subtract operation
        case.part = case.part.cut(switch_cutout)
        case.part = case.part.cut(xiao_mounting)
        
        # Add a cable exit
        with Locations((case_length/2, 0, wall_thickness + 5)):
            Cylinder(5, wall_thickness)
    
    return case.part


# Case dimensions
case_width = 40.0
case_length = 60.0
case_height = 15.0
wall_thickness = 2.0
plate_thickness = 1.5

# Component positions
switch_position = (0, 15, case_height)
xiao_position = (0, -10, wall_thickness)


def main():
    """Main function to build and display the prototype"""
    print("Building Wave keyboard prototype case...")


    print("we're currently in directory:", __file__)

    exit(0)
    
    # Create components
    switch = KailhChoc(position=switch_position)
    xiao = SeeedXiaoBLE(position=xiao_position)
    
    # Build models
    switch_model = switch.build()
    xiao_model = xiao.build()
    
    # Get cutouts
    switch_cutout = switch.get_cutout(plate_thickness)
    xiao_mounting = xiao.get_mounting_holes(wall_thickness)
    
    # Create the case
    case = create_prototype_case(switch_cutout, xiao_mounting)
    
    # Display the complete assembly
    print("Displaying case with components...")
    assembly = Compound.makeCompound([case, switch_model, xiao_model])
    display_model(assembly)
    
    # Export the model
    stl_path = "wave_prototype_case.stl"
    export_stl(case, stl_path)
    print(f"Case exported to {stl_path}")
    
    return case, switch_model, xiao_model


if __name__ == "__main__":
    main()

