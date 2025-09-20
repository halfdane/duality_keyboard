from dataclasses import dataclass
from build123d import *
from models.switch import Choc

class KeyCol:
    rotation: float = 0
    locs: list[Vector] = []

@dataclass
class PinkieDimensions(KeyCol):
    x: float = 0
    y: float = 0
    offset_x: float = -1
    rotation: float = 8
    locs: list[Vector] = (
        Vector((0, 0)), 
        Vector((-Choc.cap.width_x/rotation, Choc.cap.length_y)), 
        Vector((-2*Choc.cap.width_x/rotation, 2*Choc.cap.length_y))
    )

@dataclass
class RingFingerDimensions(KeyCol):
    x: float = Choc.cap.width_x + PinkieDimensions.offset_x
    y: float = 14
    rotation: float = 0
    locs: list[Vector] = (
        Vector((x, y)), 
        Vector((x, Choc.cap.length_y + y)), 
        Vector((x, 2*Choc.cap.length_y + y))
    )

@dataclass
class MiddleFingerDimensions(KeyCol):
    x: float = 2*Choc.cap.width_x + PinkieDimensions.offset_x
    y: float = 22.4
    rotation: float = 0
    locs: list[Vector] = (
        Vector((x, y)), 
        Vector((x, Choc.cap.length_y + y)), 
        Vector((x, 2*Choc.cap.length_y + y))
    )

@dataclass
class PointerFingerDimensions(KeyCol):
    x: float = 3*Choc.cap.width_x + PinkieDimensions.offset_x
    y: float = 18
    rotation: float = 0
    locs: list[Vector] = (
        Vector((x, y)), 
        Vector((x, Choc.cap.length_y + y)), 
        Vector((x, 2*Choc.cap.length_y + y))
    )

@dataclass
class InnerFingerDimensions(KeyCol):
    x: float = 4*Choc.cap.width_x + PinkieDimensions.offset_x
    y: float = 14
    rotation: float = 0
    locs: list[Vector] = (
        Vector((x, y)), 
        Vector((x, Choc.cap.length_y + y)), 
        Vector((x, 2*Choc.cap.length_y + y))
    )

@dataclass
class ThumbDimensions(KeyCol):
    x: float = InnerFingerDimensions.locs[0].X - 6.5
    y: float = InnerFingerDimensions.locs[0].Y - 18
    rotation: float = -8
    locs: list[Vector] = (
        Vector((x, y)), 
        Vector((Choc.cap.width_x + x, y + Choc.cap.width_x/rotation)), 
    )

class Keys:
    
    def __init__(self, switch_offset=(0,0)):
        offset_vector = Vector(switch_offset)
        self.pinkie = PinkieDimensions()
        self.ring = RingFingerDimensions()
        self.middle = MiddleFingerDimensions()
        self.pointer = PointerFingerDimensions()
        self.inner = InnerFingerDimensions()
        self.thumb = ThumbDimensions()        

        self.finger_cols = [self.pinkie, self.ring, self.middle, self.pointer, self.inner]
        self.keycols: list[KeyCol] = [*self.finger_cols, self.thumb]

        for col in self.keycols:
            col.locs = [loc + offset_vector for loc in col.locs]