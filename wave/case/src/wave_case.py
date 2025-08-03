from build123d import *

def display_model(model, color=None):
    """
    Display a 3D model using available visualization methods
    Falls back through different methods if some aren't available
    
    Args:
        model: The build123d model to display
        color: Optional color specification
    """
    try:
        # First try build123d's standard display function
        show(model)
    except NameError:
        # If that's not available, try OCP viewer
        try:
            from build123d.jupyter_tools import display
            display(model)
        except ImportError:
            # Fallback to Jupyter's display function
            from IPython.display import display
            display(model)