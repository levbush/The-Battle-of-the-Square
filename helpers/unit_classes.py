from math import hypot
if __name__ == '__main__':
    from helpers.classes import Player
from dataclasses import dataclass, field
from helpers.traits import TraitType
from enum import IntEnum
from helpers.custom_texture import CustomTexture
from helpers.skin import get_skin
from arcade import Sprite, get_window, Texture, load_texture, check_for_collision
from enum import Enum, auto


class Weapon(Sprite):
    BASE_ANGLE = 0

    def __init__(self, *args, **kwargs):
        super().__init__(scale=0.5, *args, **kwargs)
        self.anim_time = 0.0
        self.animating = False
        self._rotated = 0.0
        self._target_rotation = 0.0

    def animate(self, direction: int, time: float):
        self.anim_time = time
        self.animating = True
        self._rotated = 0.0

        self._target_rotation = 90.0 * direction
        self.angle = self.BASE_ANGLE + (270 if direction == 1 else 180)

    def update(self, dt):
        if not self.animating:
            return

        delta = self._target_rotation / self.anim_time * dt
        self.angle += delta
        self._rotated += delta

        if abs(self._rotated) >= abs(self._target_rotation):
            self.animating = False


class Club(Weapon):
    BASE_ANGLE = 0  # points right
    def __init__(self, **kwargs):
        super().__init__(load_texture('assets/animation/club.png'), **kwargs)


class Sword(Weapon):
    BASE_ANGLE = 90
    def __init__(self, **kwargs):
        super().__init__(load_texture('assets/animation/sword.png'), **kwargs)


class Arrow(Weapon):
    BASE_ANGLE = 0
    def __init__(self, **kwargs):
        super().__init__(load_texture('assets/animation/arrow.png'), **kwargs)


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

    weapon: type[Club | Sword | Arrow] = field(init=False, repr=False)
    type: UnitType = field(init=False, repr=False)
    name: str = field(init=False, repr=False)
    texture: CustomTexture = field(init=False, repr=False)
    is_alive: bool = field(init=False, default=True, repr=False)
    cost: int | None = field(init=False, repr=False)
    traits: list[TraitType] = field(init=False, repr=False)
    sprite: 'AnimatedUnitSprite' = field(init=False, repr=False, default=None)
    attack_sprite: Sprite = field(init=False, repr=False, default=None)

    def __post_init__(self, skins_map=None):
        if self.health is None:
            self.health = self.max_health
        self.texture = CustomTexture(f'assets/units/{get_skin()[self.owner.id] if skins_map is None else skins_map[self.owner.id]}/{self.name}.png')
        self.is_moving = False
        self.is_attacking = False
        self.frm = None
        self.to = None

    def move(self, pos: list[int, int]):
        self.pos = list(pos)
        screen_x = (pos[1] - pos[0]) * 150 + get_window().width // 2 + 10
        screen_y = (pos[1] + pos[0]) * 90 + 240
        self.sprite.position = (screen_x, screen_y)


class Warrior(UnitBase):
    'The warrior unit class'

    type = UnitType.WARRIOR
    name = 'warrior'
    cost = 2
    traits = [TraitType.MOBILE]
    weapon = 'Club'

    def __init__(self, owner, pos, move_remains=True, attack_remains=True, health=None):
        super().__init__(owner, pos, 10, 2, 2, 1, 1, move_remains, attack_remains, health)


class Defender(UnitBase):
    'The defender unit class'

    type = UnitType.DEFENDER
    name = 'defender'
    cost = 3
    traits = []
    weapon = 'Sword'

    def __init__(self, owner, pos, move_remains=True, attack_remains=True, health=None):
        super().__init__(owner, pos, 15, 1, 3, 1, 1, move_remains, attack_remains, health)


class Rider(UnitBase):
    'The rider unit class'

    type = UnitType.RIDER
    name = 'rider'
    cost = 2
    traits = [TraitType.MOBILE]
    weapon = 'Club'

    def __init__(self, owner, pos, move_remains=True, attack_remains=True, health=None):
        super().__init__(owner, pos, 10, 2, 1, 2, 1, move_remains, attack_remains, health)


class Archer(UnitBase):
    'The archer unit class'

    type = UnitType.ARCHER
    name = 'archer'
    cost = 3
    traits = [TraitType.RANGED, TraitType.MOBILE]
    weapon = 'Arrow'

    def __init__(self, owner, pos, move_remains=True, attack_remains=True, health=None):
        super().__init__(owner, pos, 10, 2, 1, 1, 2, move_remains, attack_remains, health)


class Swordsman(UnitBase):
    'The swordman unit class'
    type = UnitType.SWORDSMAN
    name = 'swordsman'
    cost = 4
    traits = [TraitType.MOBILE]
    weapon = 'Sword'

    def __init__(self, owner, pos, move_remains=True, attack_remains=True, health=None):
        super().__init__(owner, pos, 15, 3, 3, 1, 1, move_remains, attack_remains, health)

class Giant(UnitBase):
    'The giant unit class'

    type = UnitType.GIANT
    name = 'giant'
    cost = None
    traits = []
    weapon = 'Sword'

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


class AttackPhase(Enum):
    APPROACH = auto()
    ATTACK = auto()
    RETURN = auto()


class AnimatedUnitSprite(Sprite):
    def __init__(self, texture: Texture, attack_sprite: Unit | Sword | Arrow, scale=1.0):
        super().__init__(texture, scale)

        self._moving = False
        self._target = None
        self._speed = 0.0

        self._attacking = False
        self._attack_phase = None
        self._attack_duration = 0.0
        self._attack_elapsed = 0.0
        self._approach_time = 0.0
        self._attack_time = 0.0


        self.attack_sprite = attack_sprite
        self._to_return = None
        self._target_unit = None
        self.unit: UnitBase = None

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

    def start_attack(
        self,
        x1: float, y1: float,
        x2: float, y2: float,
        target_unit: Sprite,
        duration: float = 0.6
    ):
        
        if self.center_x > x2:
            self.scale_x = -0.5
        elif self.center_x < x2:
            self.scale_x = 0.5
        self._attacking = True
        self._attack_elapsed = 0.0
        self._attack_duration = duration

        self._approach_time = duration * 0.4
        self._attack_time = duration * 0.2
        
        dx = x2 - self.center_x
        dy = y2 - self.center_y
        self._approach_speed = hypot(dx, dy) / self._approach_time
        
        self._to_return = (x1, y1)
        self._target = (x2, y2)
        self._target_unit = target_unit

        self._attack_phase = AttackPhase.APPROACH


    def _update_attack(self, dt: float):
        self._attack_elapsed += dt

        if self._attack_phase == AttackPhase.APPROACH:
            self._update_attack_move(dt)

            if self._attack_elapsed >= self._approach_time:
                self._attack_phase = AttackPhase.ATTACK
                self._attack_elapsed = 0.0
                self._start_attack_animation(dt)

        elif self._attack_phase == AttackPhase.ATTACK:
            if self._attack_elapsed >= self._attack_time:
                self._attack_phase = AttackPhase.RETURN
                self._attack_elapsed = 0.0
                self._start_return()

        elif self._attack_phase == AttackPhase.RETURN:
            self._update_return(dt)

    def _update_attack_move(self, dt: float):
        if self.unit.type != 3:
            tx, ty = self._target
            dx = tx - self.center_x
            dy = ty - self.center_y
            dist = hypot(dx, dy)

            if check_for_collision(self, self._target_unit):
                return

            speed = self._approach_speed
            nx, ny = dx / dist, dy / dist
            self.center_x += nx * speed * dt
            self.center_y += ny * speed * dt

    def _start_attack_animation(self, dt):
        self.attack_sprite.center_x = self.center_x 
        self.attack_sprite.center_y = self.center_y
        self.attack_sprite.visible = True
        self.attack_sprite.animate(self.scale_x / abs(self.scale_x), self._attack_duration / 3)

    def _start_return(self):
        self.attack_sprite.visible = False

    def _update_return(self, dt: float): 
        if self.unit.type != 3:
            tx, ty = self._to_return
            dx = tx - self.center_x
            dy = ty - self.center_y
            dist = hypot(dx, dy)

            if dist == 0:
                self._attacking = False
                self._attack_phase = None
                return

            speed = 600
            step = speed * dt

            if step >= dist:
                self.center_x, self.center_y = tx, ty
                self._attacking = False
                self._attack_phase = None
                return

            nx, ny = dx / dist, dy / dist
            self.center_x += nx * step
            self.center_y += ny * step


    def update(self, dt: float = 1 / 60):
        self._update_move(dt)
        self._update_attack(dt)
