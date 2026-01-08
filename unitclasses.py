from classes import Player
from dataclasses import dataclass, field
from typing import Type
from classes import Player
from arcade import Texture, load_texture


@dataclass
class UnitBase:
    owner: Player
    pos: tuple[int, int]
    max_health: int
    attack: int
    defense: int
    movement: int
    range: int
    move_remains: bool = True
    health: int = None
    is_alive: bool = True

    type: int = field(init=False)
    name: str = field(init=False)
    textures: 'UnitTexture' = field(init=False)

    def __post_init__(self):
        if self.health is None: self.health = self.max_health

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
    type = 0
    name = 'warrior'
    def __init__(self, owner, pos):
        super().__init__(owner, pos, 10, 2, 2, 1, 1)


class Defender(UnitBase):
    type = 1
    name = 'defender'
    def __init__(self, owner, pos):
        super().__init__(owner, pos, 15, 1, 3, 1, 1)


class Rider(UnitBase):
    type = 2
    name = 'rider'
    def __init__(self, owner, pos):
        super().__init__(owner, pos, 10, 2, 1, 2, 1)


class Archer(UnitBase):
    type = 3
    name = 'archer'
    def __init__(self, owner, pos):
        super().__init__(owner, pos, 10, 2, 1, 1, 2)


class Giant(UnitBase):
    type = 4
    name = 'giant'
    def __init__(self, owner, pos):
        super().__init__(owner, pos, 40, 5, 4, 1, 1)


UNIT_TYPES: dict[int, Type[UnitBase]] = {
    0: Warrior,
    1: Defender,
    2: Rider,
    3: Archer,
    4: Giant,
}


class Unit:
    def __new__(cls, unit_type: int, owner: Player, x: int, y: int) -> UnitBase:
        if unit_type not in UNIT_TYPES:
            raise ValueError("Invalid unit type")
        return UNIT_TYPES[unit_type](owner, (x, y))


class UnitTexture:
    def __init__(self, name):
        self.name = name
        self.ally, self.enemy, self.bot = (load_texture(f'assets/units/{skin}{name}.png') for skin in ('ally/', 'enemy/', 'bot/'))
    
    def __repr__(self):
        return f'UnitTexture({self.name})'


for cls in UNIT_TYPES.values():
    cls.textures = UnitTexture(cls.name)