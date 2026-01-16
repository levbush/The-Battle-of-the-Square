if __name__ == '__main__':
    from helpers.classes import Player
from dataclasses import dataclass, field
from arcade import load_texture
from enum import IntEnum
from helpers.custom_texture import CustomTexture


class UnitType(IntEnum):
    'Enum class for unit types'
    WARRIOR = 0
    DEFENDER = 1
    RIDER = 2
    ARCHER = 3
    GIANT = 4


@dataclass
class UnitBase:
    'The base class for units'

    owner: 'Player'
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
    texture: CustomTexture = field(init=False, repr=False)
    is_alive: bool = field(init=False, default=True, repr=False)

    def __post_init__(self):
        if self.health is None:
            self.health = self.max_health
        self.texture = CustomTexture(f'assets/units/{self.owner.id + 1}/{self.name}.png')

    # @staticmethod
    # def attack_unit(attacker: "UnitBase", defender: "UnitBase"):
    #     '''Attack unit'''
    #     if attacker.owner == defender.owner:
    #         return

    #     if (
    #         abs(attacker.pos[0] - defender.pos[0]) > attacker.range
    #         or abs(attacker.pos[1] - defender.pos[1]) > attacker.range
    #     ):
    #         return

    #     attackForce = attacker.attack * (attacker.health / attacker.maxHealth)
    #     defenseForce = defender.defense * (defender.health / defender.maxHealth) * defenseBonus 
    #     totalDamage = attackForce + defenseForce 
    #     attackResult = round((attackForce / totalDamage) * attacker.attack * 4.5) 
    #     defenseResult = round((defenseForce / totalDamage) * defender.defense * 4.5)

    #     defender.health -= attack_damage
    #     if defender.health <= 0 and abs(attacker.pos[0] - defender.pos[0]) <= 1 and abs(attacker.pos[1] - defender.pos[1]) <= 1:
    #         attacker.move(defender.pos)
    #         defender.die()
    #         return

    #     if (
    #         abs(attacker.pos[0] - defender.pos[0]) <= defender.range
    #         and abs(attacker.pos[1] - defender.pos[1]) <= defender.range
    #     ):
    #         attacker.health -= defense_damage
    #         if attacker.health <= 0:
    #             attacker.die()

    def move(self, pos: tuple[int, int]):
        self.pos = pos

    # def die(self):
    #     """Mark the unit as dead"""
    #     self.is_alive = False
    #     self.health = 0
    #     print(f"Unit died: {self}")


class Warrior(UnitBase):
    'The warrior unit class'

    type = UnitType.WARRIOR
    name = 'warrior'

    def __init__(self, owner, pos, move_remains=True, health=None):
        super().__init__(owner, pos, 10, 2, 2, 1, 1, move_remains, health)


class Defender(UnitBase):
    'The defender unit class'

    type = UnitType.DEFENDER
    name = 'defender'

    def __init__(self, owner, pos, move_remains=True, health=None):
        super().__init__(owner, pos, 15, 1, 3, 1, 1, move_remains, health)


class Rider(UnitBase):
    'The rider unit class'

    type = UnitType.RIDER
    name = 'rider'

    def __init__(self, owner, pos, move_remains=True, health=None):
        super().__init__(owner, pos, 10, 2, 1, 2, 1, move_remains, health)


class Archer(UnitBase):
    'The archer unit class'

    type = UnitType.ARCHER
    name = 'archer'

    def __init__(self, owner, pos, move_remains=True, health=None):
        super().__init__(owner, pos, 10, 2, 1, 1, 2, move_remains, health)


class Giant(UnitBase):
    'The giant unit class'

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
    'Builder class for units, uses `UNIT_TYPES`'

    def __new__(cls, unit_type: UnitType, owner: 'Player', x: int, y: int):
        return UNIT_TYPES[unit_type](owner, (x, y))


# class UnitTexture:
#     'Fancy and repr-able texture for a unit'

#     def __init__(self, name):
#         self.name = name
#         self.ally, self.enemy, self.bot = (
#             load_texture(f'assets/units/{skin}{name}.png') for skin in ('ally/', 'enemy/', 'bot/')
#         )

#     def __repr__(self):
#         return f'UnitTexture("{self.name}")'


# for cls in UNIT_TYPES.values():
#     cls.textures = UnitTexture(cls.name)
