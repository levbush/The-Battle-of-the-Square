from classes import City
from unitclasses import UnitBase
from arcade import load_texture, Texture


class ModifierBase:
    weight: int
    type: int
    textures: tuple[Texture]
    offsets: tuple[int]
    scales: tuple[float]

    def __eq__(self, value):
        return self.__class__ == value.__class__

    def __repr__(self):
        return f'{self.__class__.__name__}()'


class Fruits(ModifierBase):
    weight = 18
    type = 0
    textures = (load_texture("assets/Resources/fruits.png"),)
    offsets = (60,)
    scales = (0.2,)


class Animal(ModifierBase):
    weight = 18
    type = 1
    textures = (load_texture("assets/Resources/animal.png"),)
    offsets = (80,)
    scales = (0.1,)


class Mountain(ModifierBase):
    weight = 6
    type = 2
    textures = (load_texture("assets/Terrain/mountain.png"),)
    offsets = (50,)
    scales = (0.3,)


class GoldMountain(ModifierBase):
    weight = 3
    type = 3
    textures = load_texture("assets/Resources/gold.png"), Mountain.textures[0]
    offsets = 75, Mountain.offsets[0]
    scales = 0.2, Mountain.scales[0]


class Forest(ModifierBase):
    weight = 13
    type = 4
    textures = (load_texture("assets/Terrain/forest.png"),)
    offsets = (80,)
    scales = (0.3,)


class Village(ModifierBase):
    weight = 5
    type = 5
    textures = (load_texture("assets/village.png"),)
    offsets = (80,)
    scales = (0.3,)


class Fish(ModifierBase):
    weight = 35
    type = 6
    textures = (load_texture("assets/Resources/fish.png"),)
    offsets = (60,)
    scales = (0.2,)


MODIFIER_TYPES: list[ModifierBase] = [Fruits, Animal, Mountain, GoldMountain, Forest, Village, Fish]
LAND_MODIFIERS: list[None | ModifierBase] = [None, Fruits, Animal, Mountain, GoldMountain, Forest, Village]
WATER_MODIFIERS: list[None | ModifierBase] = [None, Fish]


def land_modifiers_weights():
    return [100 - sum([modifier.weight for modifier in LAND_MODIFIERS if modifier])] + [
        modifier.weight for modifier in LAND_MODIFIERS if modifier
    ]


def water_modifiers_weights():
    return [100 - sum([modifier.weight for modifier in WATER_MODIFIERS if modifier])] + [
        modifier.weight for modifier in WATER_MODIFIERS if modifier
    ]


class TileBase:
    weight: int
    type: int
    texture: Texture

    def __init__(
        self, visible_mapping: list[bool], city: City = None, unit: UnitBase = None, modifier: ModifierBase | None = None
    ):
        self.visible_mapping = visible_mapping
        self.city = city
        self.unit = unit
        self.modifier = modifier

    def __repr__(self):
        return f'{self.__class__.__name__}({self.visible_mapping}, {repr(self.city)}, {repr(self.unit)}, {None if not self.modifier else self.modifier().__class__.__name__})'

    def __eq__(self, value):
        return self.__class__ == value.__class__


class Land(TileBase):
    weight = 75
    type = 0
    texture = load_texture("assets/Terrain/ground.png")

    def __init__(self, visible_mapping, city=None, unit=None, modifier=None):
        super().__init__(visible_mapping, city, unit, modifier)

    def __str__(self):
        return '.'


class Water(TileBase):
    texture = load_texture("assets/Terrain/water.png")
    weight = 20
    type = 1

    def __init__(self, visible_mapping, city=None, unit=None, modifier=None):
        super().__init__(visible_mapping, city, unit, modifier)

    def __str__(self):
        return '~'


TERRAIN_TYPES: list[TileBase] = [Land, Water]


def terrain_types_weights():
    return [type.weight for type in TERRAIN_TYPES]


class Tile:
    def __new__(
        cls,
        terrain_type: type,
        visible_mapping: list[bool],
        modifier: type = None,
        city: City | None = None,
        unit: UnitBase | None = None,
    ) -> TileBase:
        if terrain_type in TERRAIN_TYPES:
            return terrain_type(visible_mapping, city, unit, modifier)
        raise ValueError("Invalid terrain type")
