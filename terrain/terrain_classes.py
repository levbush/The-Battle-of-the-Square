from classes import City
from unitclasses import UnitBase
from random import choices


class TileBase:
    weight: int
    type: int
    def __init__(self, visible_mapping, city: City=None, unit: UnitBase=None, modifier=None):
        self.visible_mapping: list[bool] = visible_mapping
        self.unit = unit
        self.city = city
        self.modifier = None

    def __repr__(self):
        return f'{self.__class__.__name__}({self.visible_mapping}, {repr(self.city)}, {repr(self.unit)})'
    

class Land(TileBase):
    weight = 75
    type = 0
    def __init__(self, visible_mapping, city = None, unit = None, modifier=None, gold=False):
        super().__init__(visible_mapping, city, unit, modifier)
        self.gold = gold
        if self.city is None and self.modifier is None:
            self.modifier = choices([False, 'fruits', 'animal', 'mountain', "forest", "n_village"], [40, 18, 18, 9, 13, 2], k=1)[0]
        if self.modifier == "mountain" and self.gold == False:
            self.gold = choices([False, True], [60, 40], k=1)[0]

    def __str__(self):
        return '.'
    
    def __repr__(self):
        return f'{self.__class__.__name__}({self.visible_mapping}, {repr(self.city)}, {repr(self.unit)}, {self.modifier})'


class Water(TileBase):
    weight = 20
    type = 1
    def __init__(self, visible_mapping, city = None, unit = None, modifier=None):
        super().__init__(visible_mapping, city, unit, modifier)
        if self.city is None and self.modifier is None:
            self.modifier = choices([False, 'fish'], [65, 35], k=1)[0]
    def __str__(self):
        return '~'


TERRAIN_TYPES: dict[int, TileBase] = {0: Land, 1: Water}


class Tile:
    def __new__(cls, terrain_type: int, player_count: int, modifier=None) -> TileBase:
        if terrain_type in TERRAIN_TYPES:
            return TERRAIN_TYPES[terrain_type]([False] * player_count, modifier)
        raise ValueError("Invalid terrain type")