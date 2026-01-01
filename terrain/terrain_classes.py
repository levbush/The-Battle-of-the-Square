from classes import City
from unitclasses import UnitBase
from arcade import load_texture, Texture
from dataclasses import dataclass, field
from typing import Optional


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
    textures = (load_texture("assets/resources/fruits.png"),)
    offsets = (60,)
    scales = (0.2,)


class Animal(ModifierBase):
    weight = 18
    type = 1
    textures = (load_texture("assets/resources/animal.png"),)
    offsets = (80,)
    scales = (0.1,)


class Mountain(ModifierBase):
    weight = 6
    type = 2
    textures = (load_texture("assets/terrain/mountain.png"),)
    offsets = (50,)
    scales = (0.3,)


class GoldMountain(ModifierBase):
    weight = 3
    type = 3
    textures = load_texture("assets/resources/gold.png"), Mountain.textures[0]
    offsets = 75, Mountain.offsets[0]
    scales = 0.2, Mountain.scales[0]


class Forest(ModifierBase):
    weight = 13
    type = 4
    textures = (load_texture("assets/terrain/forest.png"),)
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
    textures = (load_texture("assets/resources/fish.png"),)
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


@dataclass
class TileBase:
    visible_mapping: list[bool]
    city: Optional[City] = None
    unit: Optional[UnitBase] = None
    modifier: Optional[ModifierBase] = None

    weight: int = field(init=False)
    type: int = field(init=False)
    texture: Texture = field(init=False)


class Land(TileBase):
    weight = 75
    type = 0
    texture = load_texture("assets/terrain/ground.png")
    def __str__(self):
        return "."


class Water(TileBase):
    weight = 20
    type = 1
    texture = load_texture("assets/terrain/water.png")
    def __str__(self):
        return "~"



TERRAIN_TYPES: list[TileBase] = [Land, Water]


def terrain_types_weights():
    return [t.weight for t in TERRAIN_TYPES]


class Tile:
    def __new__(
        cls,
        terrain_type: type,
        visible_mapping: list[bool],
        modifier: ModifierBase | None = None,
        city: City | None = None,
        unit: UnitBase | None = None,
    ) -> TileBase:
        if terrain_type not in TERRAIN_TYPES:
            raise ValueError("Invalid terrain type")
        return terrain_type(visible_mapping, city, unit, modifier)
