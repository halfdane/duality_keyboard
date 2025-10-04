from dataclasses import dataclass
from build123d import *
from models.model_types import RectDimensions, RoundDimensions, PosAndDims

@dataclass
class HasDimensions:
    d: RectDimensions

class Switch:
    cap: HasDimensions
    above: HasDimensions
    below: HasDimensions
    clamp_clearance_z: float