from classes import City, Player
from unitclasses import UnitBase
from arcade import load_texture, Texture
from dataclasses import dataclass, field


class CustomTexture:
    def __init__(self, path):
        self.path = path
        self.texture = load_texture(path)
    
    def __repr__(self):
        return f'CustomTexture({self.path})'


class ModifierBase:
    weight: int
    type: int
    textures: tuple[CustomTexture]
    offsets: tuple[int]
    scales: tuple[float]
    cost: int | None
    population: int | None

    def __eq__(self, value):
        return self.__class__ == value.__class__

    def __repr__(self):
        return f'{self.__class__.__name__}()'


class Fruits(ModifierBase):
    weight = 18
    type = 0
    textures = (CustomTexture("assets/resources/fruits.png"),)
    offsets = (60,)
    scales = (0.2,)
    cost = 2
    population = 1

    def __repr__(self):
        return super().__repr__()


class Animal(ModifierBase):
    weight = 18
    type = 1
    textures = (CustomTexture("assets/resources/animal.png"),)
    offsets = (80,)
    scales = (0.1,)
    cost = 2
    population = 1

    def __repr__(self):
        return super().__repr__()


class Mountain(ModifierBase):
    weight = 6
    type = 2
    textures = (CustomTexture("assets/terrain/mountain.png"),)
    offsets = (50,)
    scales = (0.3,)
    cost = None
    population = None


class GoldMountain(ModifierBase):
    weight = 3
    type = 3
    textures = CustomTexture("assets/resources/gold.png"), Mountain.textures[0]
    offsets = 75, Mountain.offsets[0]
    scales = 0.2, Mountain.scales[0]
    cost = 4
    population = 2


class Forest(ModifierBase):
    weight = 13
    type = 4
    textures = (CustomTexture("assets/terrain/forest.png"),)
    offsets = (80,)
    scales = (0.3,)
    cost = 3
    population = 1


class Village(ModifierBase):
    weight = 5
    type = 5
    textures = (CustomTexture("assets/misc/village.png"),)
    offsets = (80,)
    scales = (0.3,)
    cost = None
    population = None


class Fish(ModifierBase):
    weight = 35
    type = 6
    textures = (CustomTexture("assets/resources/fish.png"),)
    offsets = (60,)
    scales = (0.2,)
    cost = 2
    population = 1


MODIFIER_TYPES: list[ModifierBase] = [Fruits(), Animal(), Mountain(), GoldMountain(), Forest(), Village(), Fish()]
LAND_MODIFIERS: list[None | ModifierBase] = [None, Fruits(), Animal(), Mountain(), GoldMountain(), Forest(), Village()]
WATER_MODIFIERS: list[None | ModifierBase] = [None, Fish()]


def land_modifiers_weights():
    return [100 - sum([modifier.weight for modifier in LAND_MODIFIERS if modifier])] + [
        modifier.weight for modifier in LAND_MODIFIERS if modifier
    ]


def water_modifiers_weights():
    return [100 - sum([modifier.weight for modifier in WATER_MODIFIERS if modifier])] + [
        modifier.weight for modifier in WATER_MODIFIERS if modifier
    ]


@dataclass
class TileBase:
    visible_mapping: list[bool]
    city: City | None = None
    unit: UnitBase | None = None
    modifier: ModifierBase | None = None

    weight: int = field(init=False)
    type: int = field(init=False)
    texture: CustomTexture = field(init=False)
    row: int = field(init=False)
    col: int = field(init=False)
    owner: Player = field(init=False)


class Land(TileBase):
    weight = 75
    type = 0
    texture = CustomTexture("assets/terrain/ground.png")
    def __str__(self):
        return "."


class Water(TileBase):
    weight = 20
    type = 1
    texture = CustomTexture("assets/terrain/water.png")
    def __str__(self):
        return "~"



TERRAIN_TYPES: list[TileBase] = [Land, Water]


def terrain_types_weights():
    return [t.weight for t in TERRAIN_TYPES]


class Tile:
    def __new__(
        cls,
        row, col,
        terrain_type: type,
        visible_mapping: list[bool],
        modifier: ModifierBase | None = None,
        city: City | None = None,
        unit: UnitBase | None = None,
    ) -> TileBase:
        if terrain_type not in TERRAIN_TYPES:
            raise ValueError("Invalid terrain type")
        tile: TileBase = terrain_type(visible_mapping, city, unit, modifier)
        tile.row = row
        tile.col = col
        return tile