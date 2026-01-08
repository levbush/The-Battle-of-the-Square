from classes import Player
from dataclasses import dataclass, field
from typing import Type
from classes import Player
from arcade import Texture, load_texture
from enum import IntEnum


class UnitType(IntEnum):
    WARRIOR = 0
    DEFENDER = 1
    RIDER = 2
    ARCHER = 3
    GIANT = 4


@dataclass
class UnitBase:
    owner: Player
    pos: tuple[int, int]
    max_health: int = field(repr=False)
    attack: int = field(repr=False)
    defense: int = field(repr=False)
    movement: int = field(repr=False)
    range: int = field(repr=False)
    move_remains: bool = True
    health: int = None

    type: UnitType = field(init=False, repr=False)
    name: str = field(init=False, repr=False)
    textures: 'UnitTexture' = field(init=False, repr=False)
    is_alive: bool = field(init=False, default=True, repr=False)

    def __post_init__(self):
        if self.health is None:
            self.health = self.max_health

    @staticmethod
    def attack_unit(attacker: "UnitBase", defender: "UnitBase"):
        if attacker.owner == defender.owner:
            return

        if (
            abs(attacker.pos[0] - defender.pos[0]) > attacker.range
            or abs(attacker.pos[1] - defender.pos[1]) > attacker.range
        ):
            return

        attack_force = attacker.attack * (attacker.health / attacker.max_health)
        defense_force = defender.defense * (defender.health / defender.max_health)
        total = attack_force + defense_force
        print(attack_force, defense_force)
        print(total)
        # TODO: add particles
        attack_damage = round((attack_force / total) * attacker.attack * 4.5)
        defense_damage = round((defense_force / total) * defender.defense * 4.5)

        defender.health -= attack_damage
        if defender.health <= 0:
            attacker.move(defender.pos)
            defender.die()
            return

        if (
            abs(attacker.pos[0] - defender.pos[0]) <= defender.range
            and abs(attacker.pos[1] - defender.pos[1]) <= defender.range
        ):
            attacker.health -= defense_damage
            if attacker.health <= 0:
                attacker.die()

    def move(self, pos: tuple[int, int]):
        # TODO: add animation
        self.pos = pos

    def die(self):
        """Помечает юнита как мертвого"""
        self.is_alive = False
        self.health = 0
        print(f"Unit died: {self}")


class Warrior(UnitBase):
    type = UnitType.WARRIOR
    name = 'warrior'

    def __init__(self, owner, pos, move_remains=True, health=None):
        super().__init__(owner, pos, 10, 2, 2, 1, 1, move_remains, health)


class Defender(UnitBase):
    type = UnitType.DEFENDER
    name = 'defender'

    def __init__(self, owner, pos, move_remains=True, health=None):
        super().__init__(owner, pos, 15, 1, 3, 1, 1, move_remains, health)


class Rider(UnitBase):
    type = UnitType.RIDER
    name = 'rider'

    def __init__(self, owner, pos, move_remains=True, health=None):
        super().__init__(owner, pos, 10, 2, 1, 2, 1, move_remains, health)


class Archer(UnitBase):
    type = UnitType.ARCHER
    name = 'archer'

    def __init__(self, owner, pos, move_remains=True, health=None):
        super().__init__(owner, pos, 10, 2, 1, 1, 2, move_remains, health)


class Giant(UnitBase):
    type = UnitType.GIANT
    name = 'giant'

    def __init__(self, owner, pos, move_remains=True, health=None):
        super().__init__(owner, pos, 40, 5, 4, 1, 1, move_remains, health)


UNIT_TYPES: dict[UnitType, type[UnitBase]] = {
    UnitType.WARRIOR: Warrior,
    UnitType.DEFENDER: Defender,
    UnitType.RIDER: Rider,
    UnitType.ARCHER: Archer,
    UnitType.GIANT: Giant,
}



class Unit:
    def __new__(cls, unit_type: UnitType, owner: Player, x: int, y: int):
        return UNIT_TYPES[unit_type](owner, (x, y))


class UnitTexture:
    def __init__(self, name):
        self.name = name
        self.ally, self.enemy, self.bot = (load_texture(f'assets/units/{skin}{name}.png') for skin in ('ally/', 'enemy/', 'bot/'))
    
    def __repr__(self):
        return f'UnitTexture("{self.name}")'


for cls in UNIT_TYPES.values():
    cls.textures = UnitTexture(cls.name)