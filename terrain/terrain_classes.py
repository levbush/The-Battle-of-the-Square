class TileBase:
    weight: int
    def __init__(self):
        self.terrain_type = self.__class__.__name__.lower()
    

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
    def __new__(cls, terrain_type):
        if terrain_type in TERRAIN_TYPES:
            return TERRAIN_TYPES[terrain_type]()
        raise ValueError("Invalid terrain type")