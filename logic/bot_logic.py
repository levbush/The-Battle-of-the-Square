from helpers.terrain.terrain_classes import TileBase
from helpers.unit_classes import UnitBase, Unit, UNIT_TYPES
from random import choices, randint

if __name__ == '__main__':
    from views.game_view import GameView


def dist(a: TileBase, b: TileBase) -> int:
    return abs(a.row - b.row) + abs(a.col - b.col)


class BotLogic:
    def __init__(self, game: 'GameView'):
        '''AI controller for a non-human player'''
        self.game = game

    def move(self) -> None:
        '''Perform one AI turn'''
        visible_enemy_cities: list[TileBase] = []
        visible_enemy_units: list[TileBase] = []
        fog: list[TileBase] = []
        own_units: list[UnitBase] = []

        for row in self.game.map:
            for tile in row:
                if not tile.visible_mapping[self.game.current_player.id]:
                    fog.append(tile)
                    continue

                if tile.city and tile.city.owner != self.game.current_player:
                    visible_enemy_cities.append(tile)

                if tile.unit:
                    if tile.unit.owner == self.game.current_player:
                        own_units.append(tile.unit)
                    else:
                        visible_enemy_units.append(tile)

        for unit in list(own_units):
            if not unit.move_remains:
                continue

            target: TileBase | None = self.get_priority_target(
                unit,
                visible_enemy_units,
                visible_enemy_cities,
                fog
            )
            print(repr(target))

            if target:
                self.move_towards(unit, target)

        for city in self.game.current_player.cities:
            if not city.tile.unit:
                if choices([0, 1], [50, 50 + 30 * self.game.bot_difficulty], k=1)[0]:
                    city.tile.unit = Unit(
                        randint(0, len(UNIT_TYPES) - 1),
                        self.game.current_player,
                        city.tile.row,
                        city.tile.col
                    )

            cx, cy = city.tile.row, city.tile.col
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    tile = self.game.map[cx + dx][cy + dy]
                    modifier = tile.modifier
                    if modifier and modifier.cost and not modifier.is_collected:
                        if choices([0, 1], [20, 10 + 15 * self.game.bot_difficulty], k=1)[0]:
                            modifier.collect()
                            city.tile.add_population_to_city(modifier.population)

    def move_towards(self, unit: UnitBase, target: TileBase) -> bool:
        '''Move unit toward target or attack if possible'''
        if not unit.move_remains:
            return False

        movement = self.game.movement_system
        attack = self.game.attack_system

        start_tile: TileBase = self.game.map[unit.pos[0]][unit.pos[1]]

        if target.unit and attack.can_attack_from_position(start_tile, target):
            return movement.move_unit(start_tile, target)

        valid_moves: list[TileBase] = movement.get_valid_moves(start_tile)
        if not valid_moves:
            return False

        best_tile: TileBase = min(
            valid_moves,
            key=lambda x: dist(x, target)
        )

        if target.unit:
            return movement.move_unit(start_tile, best_tile)

        if choices([0, 1], [50 - 50 * self.game.bot_difficulty, 100], k=1)[0]:
            return movement.move_unit(start_tile, best_tile)

        return False

    def get_priority_target(
        self,
        unit: UnitBase,
        enemy_units: list[TileBase],
        enemy_cities: list[TileBase],
        fog: list[TileBase]
    ) -> TileBase | None:
        print(enemy_units)
        '''Select best target tile for unit'''
        start_tile: TileBase = self.game.map[unit.pos[0]][unit.pos[1]]
        attack = self.game.attack_system

        for tile in enemy_units:
            if tile.unit and attack.can_attack_from_position(start_tile, tile):
                return tile

        if enemy_units:
            return min(enemy_units, key=lambda t: dist(self.game.map[unit.pos[0]][unit.pos[1]], t))

        if enemy_cities:
            return min(enemy_cities, key=lambda t: dist(self.game.map[unit.pos[0]][unit.pos[1]], t))

        if fog:
            return min(fog, key=lambda t: dist(self.game.map[unit.pos[0]][unit.pos[1]], t))

        return None