from dataclasses import dataclass
from build123d import *
from models.switch import Choc

class KeyCol:
    rotation: float = 0
    locs: list[Location] = []

@dataclass
class PinkieDimensions(KeyCol):
    x: float = 0
    y: float = 0
    offset_x: float = -1
    rotation: float = 8
    locs: list[Location] = (
        Location((0, 0)), 
        Location((-Choc.cap.width_x/rotation, Choc.cap.length_y)), 
        Location((-2*Choc.cap.width_x/rotation, 2*Choc.cap.length_y))
    )

@dataclass
class RingFingerDimensions(KeyCol):
    x: float = Choc.cap.width_x + PinkieDimensions.offset_x
    y: float = 14
    rotation: float = 0
    locs: list[Location] = (
        Location((x, y)), 
        Location((x, Choc.cap.length_y + y)), 
        Location((x, 2*Choc.cap.length_y + y))
    )

@dataclass
class MiddleFingerDimensions(KeyCol):
    x: float = 2*Choc.cap.width_x + PinkieDimensions.offset_x
    y: float = 22.4
    rotation: float = 0
    locs: list[Location] = (
        Location((x, y)), 
        Location((x, Choc.cap.length_y + y)), 
        Location((x, 2*Choc.cap.length_y + y))
    )

@dataclass
class PointerFingerDimensions(KeyCol):
    x: float = 3*Choc.cap.width_x + PinkieDimensions.offset_x
    y: float = 18
    rotation: float = 0
    locs: list[Location] = (
        Location((x, y)), 
        Location((x, Choc.cap.length_y + y)), 
        Location((x, 2*Choc.cap.length_y + y))
    )

@dataclass
class InnerFingerDimensions(KeyCol):
    x: float = 4*Choc.cap.width_x + PinkieDimensions.offset_x
    y: float = 14
    rotation: float = 0
    locs: list[Location] = (
        Location((x, y)), 
        Location((x, Choc.cap.length_y + y)), 
        Location((x, 2*Choc.cap.length_y + y))
    )

@dataclass
class ThumbDimensions(KeyCol):
    x: float = InnerFingerDimensions.locs[0].position.X - 6.5
    y: float = InnerFingerDimensions.locs[0].position.Y - 18
    rotation: float = -8
    locs: list[Location] = (
        Location((x, y)), 
        Location((Choc.cap.width_x + x, y + Choc.cap.length_y/rotation)), 
    )

class Keys:
    pinkie = PinkieDimensions()
    ring = RingFingerDimensions()
    middle = MiddleFingerDimensions()
    pointer = PointerFingerDimensions()
    inner = InnerFingerDimensions()
    thumb = ThumbDimensions()
    finger_cols = [pinkie, ring, middle, pointer, inner]
    keycols: list[KeyCol] = [*finger_cols, thumb]
    