from classes import Player


class UnitBase:
    type: int

    def __init__(
        self, owner: Player, pos: tuple[int, int], max_health: int, attack: int, defense: int, movement: int, range: int
    ):
        self.owner = owner
        self.pos = pos
        self.max_health = max_health
        self.health = max_health
        self.attack = attack
        self.defense = defense
        self.movement = movement
        self.range = range
        self.args = (owner, pos, max_health, attack, defense, movement, range)

    def __repr__(self):
        return f'{self.__class__.__name__}({",".join(list(map(repr, self.args)))})'

    def __str__(self):
        return f'{self.__class__.__name__}: {self.health}hp\n'

    def attack_unit(attacker, defender: 'UnitBase'):
        if attacker.owner == defender.owner:
            return
        if (
            abs(attacker.pos[0] - defender.pos[0]) > attacker.range
            or abs(attacker.pos[1] - defender.pos[1]) > attacker.range
        ):
            return
        # TODO: add particles
        attackForce = attacker.attack * (attacker.health / attacker.max_health)
        defenseForce = defender.defense * (defender.health / defender.max_health)
        totalDamage = attackForce + defenseForce
        attackResult = round((attackForce / totalDamage) * attacker.attack * 4.5)
        defenseResult = round((defenseForce / totalDamage) * defender.defense * 4.5)

        defender.health -= attackResult
        if defender.health < 0:
            attacker.move(defender.pos)
            defender.die()
            return
        if (
            abs(attacker.pos[0] - defender.pos[0]) <= defender.range
            and abs(attacker.pos[1] - defender.pos[1]) <= defender.range
        ):
            attacker.health -= defenseResult
            if attacker.health < 0:
                attacker.die()

    def die(self):
        # TODO: add particles
        del self

    def move(self, pos):
        # TODO: add animation
        self.pos = pos


class Warrior(UnitBase):
    type = 0

    def __init__(self, *args):
        super().__init__(*args, 10, 2, 2, 1, 1)


class Defender(UnitBase):
    type = 1

    def __init__(self, *args):
        super().__init__(*args, 15, 1, 3, 1, 1)


class Rider(UnitBase):
    type = 2

    def __init__(self, *args):
        super().__init__(*args, 10, 2, 1, 2, 1)


class Archer(UnitBase):
    type = 3

    def __init__(self, *args):
        super().__init__(*args, 10, 2, 1, 1, 2)


class Giant(UnitBase):
    type = 4

    def __init__(self, *args):
        super().__init__(*args, 40, 5, 4, 1, 1)


UNIT_TYPES: dict[int, UnitBase] = {0: Warrior, 1: Defender, 2: Rider, 3: Archer, 4: Giant}


class Unit:
    def __new__(cls, unit_type: int, owner: Player, x: int, y: int) -> UnitBase:
        if unit_type in UNIT_TYPES:
            return UNIT_TYPES[unit_type](owner, (x, y))
        raise ValueError('Invalid unit type')
