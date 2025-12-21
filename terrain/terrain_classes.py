from classes import City
from unitclasses import UnitBase


class TileBase:
    weight: int
    type: int
    def __init__(self, visible_mapping):
        self.visible_mapping: list[bool] = visible_mapping
        self.unit: UnitBase = None
        self.city: City = None

    def __repr__(self):
        return f'{self.__class__.__name__}({self.visible_mapping})'
    

class Land(TileBase):
    weight = 75
    type = 0
    def __str__(self):
        return '.'


class Water(TileBase):
    weight = 20
    type = 1
    def __str__(self):
        return '~'


class Mountain(TileBase):
    weight = 5
    type = 2
    def __str__(self):
        return '^'


TERRAIN_TYPES: dict[int, TileBase] = {0: Land, 1: Water, 2: Mountain}


class Tile:
    def __new__(cls, terrain_type: int, player_count: int) -> TileBase:
        if terrain_type in TERRAIN_TYPES:
            return TERRAIN_TYPES[terrain_type]([False] * player_count)
        raise ValueError("Invalid terrain type")