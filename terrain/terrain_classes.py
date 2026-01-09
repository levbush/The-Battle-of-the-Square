from classes import City, Player
from unitclasses import UnitBase, Unit, UnitType
from arcade import load_texture, Texture
from dataclasses import dataclass, field
from enum import IntEnum


class ModifierType(IntEnum):
    FRUITS = 0
    ANIMAL = 1
    MOUNTAIN = 2
    GOLD_MOUNTAIN = 3
    FOREST = 4
    VILLAGE = 5
    FISH = 6


class TerrainType(IntEnum):
    LAND = 0
    WATER = 1


class CustomTexture:
    def __init__(self, path):
        self.path = path
        self.texture = load_texture(path)
    
    def __repr__(self):
        return f'CustomTexture("{self.path}")'


class ModifierBase:
    weight: int
    type: ModifierType
    textures: tuple[CustomTexture]
    offsets: tuple[int]
    scales: tuple[float]
    cost: int | None
    population: int | None
    tile: 'TileBase' = None

    def __init__(self, is_collected=False):
        self.is_collected = is_collected

    def __eq__(self, value):
        return self.__class__ == value.__class__

    def __repr__(self):
        return f'{self.__class__.__name__}({self.is_collected})'
    
    def collect(self):
        self.is_collected = True


class Fruits(ModifierBase):
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
    weight = 3
    type = ModifierType.GOLD_MOUNTAIN
    textures = CustomTexture("assets/resources/gold.png"), Mountain.textures[0]
    offsets = 75, Mountain.offsets[0]
    scales = 0.2, Mountain.scales[0]
    cost = 4
    population = 2

    def collect(self):
        super().collect()
        self.textures = CustomTexture("assets/resources/goldCollected.png"), Mountain.textures[0]


class Forest(ModifierBase):
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
    weight = 35
    type = ModifierType.FISH
    textures = (CustomTexture("assets/resources/fish.png"),)
    offsets = (60,)
    scales = (0.2,)
    cost = 2
    population = 1

    def collect(self):
        self.tile.modifier = None


MODIFIER_TYPES: list[type] = [Fruits, Animal, Mountain, GoldMountain, Forest, Village, Fish]
LAND_MODIFIERS: list[type] = [lambda: None, Fruits, Animal, Mountain, GoldMountain, Forest, Village]
WATER_MODIFIERS: list[type] = [lambda: None, Fish]


def land_modifiers_weights():
    return [100 - sum([modifier.weight for modifier in LAND_MODIFIERS if modifier()])] + [
        modifier.weight for modifier in LAND_MODIFIERS if modifier()
    ]


def water_modifiers_weights():
    return [100 - sum([modifier.weight for modifier in WATER_MODIFIERS if modifier()])] + [
        modifier.weight for modifier in WATER_MODIFIERS if modifier()
    ]


@dataclass
class TileBase:
    visible_mapping: list[bool]
    city: City | None = None
    unit: UnitBase | None = None
    modifier: ModifierBase | None = None

    weight: int = field(init=False, repr=False)
    type: TerrainType = field(init=False, repr=False)
    texture: CustomTexture = field(init=False, repr=False)
    row: int = field(init=False, repr=False)
    col: int = field(init=False, repr=False)
    owner: City | None = None

    def add_population_to_city(self, n: int):
        if not self.owner:
            return
        self.owner.population += n
        if self.owner.population >= self.owner.level + 2:
            self.owner.population -= self.owner.level + 2
            self.owner.level += 1
            if self.owner.level > 1:
                # self.unit.random_move()
                self.owner.tile.unit = Unit(UnitType.GIANT, self.owner.owner, self.row, self.col)
                self.owner.tile.unit.move_remains = False
    
    def __post_init__(self):
        if self.modifier:
            self.modifier.tile = self
        if self.city:
            self.city.tile = self


class Land(TileBase):
    weight = 75
    type = TerrainType.LAND
    texture = CustomTexture("assets/terrain/ground.png")
    def __str__(self):
        return "."


class Water(TileBase):
    weight = 20
    type = TerrainType.WATER
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
        tile: TileBase = terrain_type(visible_mapping, city, unit, modifier)
        tile.row = row
        tile.col = col
        return tile