if __name__ == '__main__':
    from helpers.classes import City
from helpers.unit_classes import UnitBase
from dataclasses import dataclass, field
from enum import IntEnum
from helpers.custom_texture import CustomTexture


class ModifierType(IntEnum):
    'Enum class for modifier types'

    FRUITS = 0
    ANIMAL = 1
    MOUNTAIN = 2
    GOLD_MOUNTAIN = 3
    FOREST = 4
    VILLAGE = 5
    FISH = 6


class TerrainType(IntEnum):
    'Enum class for tile types'

    LAND = 0
    WATER = 1


class ModifierBase:
    'Base class for modifiers'

    weight: int
    type: ModifierType
    textures: tuple[CustomTexture]  # These are tuples because some modifiers use multiple textures
    offsets: tuple[int]
    scales: tuple[float]
    cost: int | None
    population: int | None
    tile: 'TileBase' = None

    def __init__(self, is_collected=False):
        self.is_collected = is_collected
        if self.is_collected: self.collect()

    def __eq__(self, value):
        return self.__class__ == value.__class__

    def __repr__(self):
        return f'{self.__class__.__name__}({self.is_collected})'

    def collect(self):
        self.is_collected = True


class Fruits(ModifierBase):
    'Fruits modifier class'
    weight = 18
    type = ModifierType.FRUITS
    textures = (CustomTexture("assets/resources/fruits.png"),)
    offsets = (60,)
    scales = (0.2,)
    cost = 2
    population = 1

    def __repr__(self):
        return super().__repr__()

    def collect(self):
        self.tile.modifier = None


class Animal(ModifierBase):
    'Animal modifier class'

    weight = 18
    type = ModifierType.ANIMAL
    textures = (CustomTexture("assets/resources/animal.png"),)
    offsets = (80,)
    scales = (0.1,)
    cost = 2
    population = 1

    def __repr__(self):
        return super().__repr__()

    def collect(self):
        self.tile.modifier = None


class Mountain(ModifierBase):
    'Mountain modifier class'

    weight = 6
    type = ModifierType.MOUNTAIN
    textures = (CustomTexture("assets/terrain/mountain.png"),)
    offsets = (50,)
    scales = (0.3,)
    cost = None
    population = None

    def collect(self):
        return NotImplemented


class GoldMountain(ModifierBase):
    'Mountain with gold modifier class'

    weight = 3
    type = ModifierType.GOLD_MOUNTAIN
    textures = CustomTexture("assets/resources/gold.png"), Mountain.textures[0]  # Multiple as gold isn't a mountain by itself
    offsets = 75, Mountain.offsets[0]
    scales = 0.2, Mountain.scales[0]
    cost = 4
    population = 2

    def collect(self):
        super().collect()
        self.textures = CustomTexture("assets/resources/goldCollected.png"), Mountain.textures[0]


class Forest(ModifierBase):
    'Mountain modifier class'

    weight = 13
    type = ModifierType.FOREST
    textures = (CustomTexture("assets/terrain/forest.png"),)
    offsets = (80,)
    scales = (0.3,)
    cost = 3
    population = 1

    def collect(self):
        super().collect()
        self.textures = CustomTexture('assets/resources/hut.png'), CustomTexture("assets/terrain/forest.png")
        self.offsets = (80, 80)
        self.scales = (0.3, 0.3)


class Village(ModifierBase):
    'Village modifier class'

    weight = 5
    type = ModifierType.VILLAGE
    textures = (CustomTexture("assets/misc/village.png"),)
    offsets = (80,)
    scales = (0.3,)
    cost = None
    population = None

    def collect(self):
        return NotImplemented


class Fish(ModifierBase):
    'Fish modifier class'

    weight = 35
    type = ModifierType.FISH
    textures = (CustomTexture("assets/resources/fish.png"),)  # It's a very exotic type of fish
    offsets = (60,)
    scales = (0.2,)
    cost = 2
    population = 1

    def collect(self):
        self.tile.modifier = None


MODIFIER_TYPES: list[type[ModifierBase]] = [Fruits, Animal, Mountain, GoldMountain, Forest, Village, Fish]
LAND_MODIFIERS: list[type[ModifierBase]] = [lambda: None, Fruits, Animal, Mountain, GoldMountain, Forest, Village]
WATER_MODIFIERS: list[type[ModifierBase]] = [lambda: None, Fish]


def land_modifiers_weights() -> list[int]:
    'Gives a list of weights using `LAND_MODIFIERS`. `sum(land_modifiers_weights()) == 100`'
    return [100 - sum([modifier.weight for modifier in LAND_MODIFIERS if modifier()])] + [
        modifier.weight for modifier in LAND_MODIFIERS if modifier()
    ]


def water_modifiers_weights() -> list[int]:
    'Gives a list of weights using `WATER_MODIFIERS`. `sum(water_modifiers_weights()) == 100`'

    return [100 - sum([modifier.weight for modifier in WATER_MODIFIERS if modifier()])] + [
        modifier.weight for modifier in WATER_MODIFIERS if modifier()
    ]


@dataclass
class TileBase:
    'Base class for tiles'

    visible_mapping: list[bool]
    city: 'City' = None
    unit: UnitBase | None = None
    modifier: ModifierBase | None = None

    weight: int = field(init=False, repr=False)
    type: TerrainType = field(init=False, repr=False)
    texture: CustomTexture = field(init=False, repr=False)
    row: int = field(init=False, repr=False)
    col: int = field(init=False, repr=False)
    owner: 'City' = None

    def add_population_to_city(self, n: int):
        if not self.owner:
            return
        self.owner.population += n
        if self.owner.population >= self.owner.level + 2:
            self.owner.population -= self.owner.level + 2
            self.owner.level_up()

    def __post_init__(self):
        if self.modifier:
            self.modifier.tile = self
        if self.city:
            self.city.tile = self


class Land(TileBase):
    'Land tile class'

    weight = 75
    type = TerrainType.LAND
    texture = CustomTexture("assets/terrain/ground.png")

    def __str__(self):
        return "."


class Water(TileBase):
    'Water tile class'

    weight = 20
    type = TerrainType.WATER
    texture = CustomTexture("assets/terrain/water.png")

    def __str__(self):
        return "~"


TERRAIN_TYPES: dict[TerrainType, type[TileBase]] = {TerrainType.LAND: Land, TerrainType.WATER: Water}


def terrain_types_weights() -> list[int]:
    'Gives a list of weights using `TERRAIN_TYPES`'
    return [t.weight for t in TERRAIN_TYPES.values()]


class Tile:
    'Builder class for tiles, uses `TERRAIN_TYPES`'

    def __new__(
        cls,
        row,
        col,
        terrain_type: TerrainType,
        visible_mapping: list[bool],
        modifier: ModifierBase | None = None,
        city: 'City' = None,
        unit: UnitBase | None = None,
    ) -> TileBase:
        tile = TERRAIN_TYPES[terrain_type](visible_mapping, city, unit, modifier)
        tile.row = row
        tile.col = col
        return tile
