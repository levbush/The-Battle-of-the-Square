from classes import City
from unitclasses import UnitBase


class TileBase:
    weight: int
    def __init__(self, visible_mapping):
        self.terrain_type = list(TERRAIN_TYPES.values()).index(self.__class__)
        self.visible_mapping: list[bool] = visible_mapping
        self.unit: UnitBase = None
        self.city: City = None

    def __repr__(self):
        return f'{self.__class__.__name__}({self.visible_mapping})'
    

class Land(TileBase):
    weight = 70
    def __str__(self):
        return '.'


class Water(TileBase):
    weight = 10
    def __str__(self):
        return '~'


class Mountain(TileBase):
    weight = 20
    def __str__(self):
        return '^'


TERRAIN_TYPES: dict[int, TileBase] = {0: Land, 1: Water, 2: Mountain}


class Tile:
    def __new__(cls, terrain_type: int, player_count: int) -> TileBase:
        if terrain_type in TERRAIN_TYPES:
            return TERRAIN_TYPES[terrain_type]([False] * player_count)
        raise ValueError("Invalid terrain type")