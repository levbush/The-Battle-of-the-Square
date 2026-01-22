from math import sin, cos, atan2, hypot
if __name__ == '__main__':
    from helpers.classes import Player
from dataclasses import dataclass, field
from helpers.traits import TraitType
from enum import IntEnum
from helpers.custom_texture import CustomTexture
from random import shuffle
from arcade import Sprite, get_window

SKIN = [i for i in range(1, 15)]
shuffle(SKIN)


class UnitType(IntEnum):
    'Enum class for unit types'
    WARRIOR = 0
    DEFENDER = 1
    RIDER = 2
    ARCHER = 3
    SWORDSMAN = 4
    GIANT = 5


@dataclass
class UnitBase:
    'The base class for units'

    owner: 'Player'
    pos: list[int, int]
    max_health: int = field(repr=False)
    attack: int = field(repr=False)
    defense: int = field(repr=False)
    movement: int = field(repr=False)
    range: int = field(repr=False)
    move_remains: bool = True
    attack_remains: bool = True
    health: int = None

    type: UnitType = field(init=False, repr=False)
    name: str = field(init=False, repr=False)
    texture: CustomTexture = field(init=False, repr=False)
    is_alive: bool = field(init=False, default=True, repr=False)
    cost: int | None = field(init=False, repr=False)
    traits: list[TraitType] = field(init=False, repr=False)
    sprite: 'AnimatedUnitSprite' = field(init=False, repr=False, default=None)

    def __post_init__(self):
        if self.health is None:
            self.health = self.max_health
        self.texture = CustomTexture(f'assets/units/{SKIN[self.owner.id]}/{self.name}.png')
        self.is_moving = False
        self.is_attacking = False
        self.frm = None
        self.to = None

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

    def move(self, pos: list[int, int]):
        self.pos = list(pos)
        screen_x = (pos[1] - pos[0]) * 150 + get_window().width // 2 + 10
        screen_y = (pos[1] + pos[0]) * 90 + 240
        self.sprite.position = (screen_x, screen_y)

    # def die(self):
    #     """Mark the unit as dead"""
    #     self.is_alive = False
    #     self.health = 0
    #     print(f"Unit died: {self}")

    # def move_animation(self, frm, to):
    #     self.is_moving = True
    #     self.frm = frm
    #     self.to = to
    #     self.move(frm)
    #     # if frm[1] > to[1]:
    #     #     self.sprite.scale_x = -0.5
    #     # elif frm[1] < to[1]:
    #     #     self.sprite.scale_x = 0.5
    #     while self.is_moving:
    #         self.update()

    # def attack_animation(self, frm, to):
    #     self.is_attacking = True
    #     self.frm = frm
    #     self.to = to
    #     self.move(self.frm)
    #     # if frm[1] > to[1]:
    #     #     self.sprite.scale_x = -0.5
    #     # elif frm[1] < to[1]:
    #     #     self.sprite.scale_x = 0.5
    #     while self.is_attacking:
    #         self.update()
    
    # def update(self):
    #     get_window().current_view.on_draw()
    #     if self.is_moving:
    #         remains = dist(self.to, self.pos)
    #         angle = atan2(self.to[0] - self.frm[0], self.to[1] - self.frm[1])
    #         dx = cos(angle) * SPEED
    #         dy = sin(angle) * SPEED
    #         self.pos[0] += dx
    #         self.pos[1] += dy
    #         self.sprite.center_x += dx
    #         self.sprite.center_y += dy
    #         if dist(self.pos, self.to) >= remains:
    #             self.move(self.to)
    #             self.is_moving = False
    #     elif self.is_attacking:
    #         self.is_attacking = False
        


class Warrior(UnitBase):
    'The warrior unit class'

    type = UnitType.WARRIOR
    name = 'warrior'
    cost = 2
    traits = [TraitType.MOBILE]

    def __init__(self, owner, pos, move_remains=True, attack_remains=True, health=None):
        super().__init__(owner, pos, 10, 2, 2, 1, 1, move_remains, attack_remains, health)


class Defender(UnitBase):
    'The defender unit class'

    type = UnitType.DEFENDER
    name = 'defender'
    cost = 3
    traits = []

    def __init__(self, owner, pos, move_remains=True, attack_remains=True, health=None):
        super().__init__(owner, pos, 15, 1, 3, 1, 1, move_remains, attack_remains, health)


class Rider(UnitBase):
    'The rider unit class'

    type = UnitType.RIDER
    name = 'rider'
    cost = 2
    traits = [TraitType.MOBILE]

    def __init__(self, owner, pos, move_remains=True, attack_remains=True, health=None):
        super().__init__(owner, pos, 10, 2, 1, 2, 1, move_remains, attack_remains, health)


class Archer(UnitBase):
    'The archer unit class'

    type = UnitType.ARCHER
    name = 'archer'
    cost = 3
    traits = [TraitType.RANGED, TraitType.MOBILE]

    def __init__(self, owner, pos, move_remains=True, attack_remains=True, health=None):
        super().__init__(owner, pos, 10, 2, 1, 1, 2, move_remains, attack_remains, health)


class Swordsman(UnitBase):
    'The swordman unit class'
    type = UnitType.SWORDSMAN
    name = 'swordsman'
    cost = 4
    traits = [TraitType.MOBILE]

    def __init__(self, owner, pos, move_remains=True, attack_remains=True, health=None):
        super().__init__(owner, pos, 15, 3, 3, 1, 1, move_remains, attack_remains, health)

class Giant(UnitBase):
    'The giant unit class'

    type = UnitType.GIANT
    name = 'giant'
    cost = None
    traits = []

    def __init__(self, owner, pos, move_remains=True, attack_remains=True, health=None):
        super().__init__(owner, pos, 40, 5, 4, 1, 1, move_remains, attack_remains, health)


UNIT_TYPES: dict[UnitType, type[UnitBase]] = {
    UnitType.WARRIOR: Warrior,
    UnitType.DEFENDER: Defender,
    UnitType.RIDER: Rider,
    UnitType.ARCHER: Archer,
    UnitType.SWORDSMAN: Swordsman,
    UnitType.GIANT: Giant,
}


class Unit:
    'Builder class for units, uses `UNIT_TYPES`'

    def __new__(cls, unit_type: UnitType, owner: 'Player', x: int, y: int) -> UnitBase:
        return UNIT_TYPES[unit_type](owner, [x, y])


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


class AnimatedUnitSprite(Sprite):
    def __init__(self, texture, scale=1.0):
        super().__init__(texture, scale)

        self._moving = False
        self._target = None
        self._speed = 0.0

        self._attacking = False
        self._attack_timer = 0.0

    def start_move(self, target_x: float, target_y: float, duration: float = 0.15):
        if self.center_x > target_x:
            self.scale_x = -0.5
        elif self.center_x < target_x:
            self.scale_x = 0.5

        dx = target_x - self.center_x
        dy = target_y - self.center_y

        distance = hypot(dx, dy)

        if distance == 0 or duration <= 0:
            self.center_x = target_x
            self.center_y = target_y
            self._moving = False
            return

        self._target = (target_x, target_y)
        self._speed = distance / duration
        self._moving = True

    def _update_move(self, dt: float):
        if not self._moving or self._target is None:
            return

        tx, ty = self._target
        dx = tx - self.center_x
        dy = ty - self.center_y
        dist = hypot(dx, dy)

        if dist <= self._speed * dt:
            self.center_x = tx
            self.center_y = ty
            self._moving = False
            self._target = None
            return

        nx = dx / dist
        ny = dy / dist

        self.center_x += nx * self._speed * dt
        self.center_y += ny * self._speed * dt

    def start_attack(self, x1, y1, x2, y2, duration=0.5):
        self._attacking = True
        self._attack_timer = duration

    def _update_attack(self, dt: float):
        if not self._attacking:
            return

        self._attack_timer -= dt
        if self._attack_timer <= 0:
            self._attacking = False

    def update(self, dt: float = 1 / 60):
        self._update_move(dt)
        self._update_attack(dt)