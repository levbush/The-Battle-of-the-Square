from helpers.terrain.terrain_classes import TileBase
from helpers.unit_classes import UnitBase, Unit, UNIT_TYPES
from random import choices, randint
from pprint import pprint

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
        visible_enemy_units: list[TileBase] = []
        visible_enemy_cities: list[TileBase] = []
        fog: list[TileBase] = []
        own_units: list[UnitBase] = []

        for row in self.game.map:
            for tile in row:
                if not tile.visible_mapping[self.game.current_player.id]:
                    fog.append(tile)
                    continue
                if tile.unit:
                    if tile.unit.owner == self.game.current_player:
                        own_units.append(tile.unit)
                    else:
                        visible_enemy_units.append(tile)

                if tile.city and tile.city.owner != self.game.current_player:
                    visible_enemy_cities.append(tile)
        for unit in list(own_units):
            unit.move_remains = True
                
        for unit in list(own_units):
            if not unit.move_remains or not unit.is_alive:
                continue

            self.act_unit(unit, visible_enemy_units, visible_enemy_cities, fog)

        self.handle_city_actions()

    def act_unit(
        self,
        unit: UnitBase,
        enemy_units: list[TileBase],
        enemy_cities: list[TileBase],
        fog: list[TileBase]
    ) -> None:
        '''Resolve a single unit action'''
        start_tile = self.game.map[unit.pos[0]][unit.pos[1]]
        movement = self.game.movement_system
        attack = self.game.attack_system

        for tile in enemy_cities:
            if tile == start_tile:
                self.game.capture(tile)

        valid_moves = movement.get_valid_moves(start_tile)
        if not valid_moves:
            return

        for tile in enemy_units:
            if tile.unit and attack.can_attack_from_position(start_tile, tile):
                movement.move_unit(start_tile, tile)
                return

        target = self.select_reachable_target(start_tile, valid_moves, enemy_units, enemy_cities, fog)
        if not target:
            return

        best_tile = min(valid_moves, key=lambda t: dist(t, target))
        movement.move_unit(start_tile, best_tile)

    def select_reachable_target(
        self,
        start: TileBase,
        valid_moves: list[TileBase],
        enemy_units: list[TileBase],
        enemy_cities: list[TileBase],
        fog: list[TileBase]
    ) -> TileBase | None:
        '''Pick nearest target that can be approached'''

        def reachable(target: TileBase) -> bool:
            return any(dist(m, target) < dist(start, target) for m in valid_moves)

        for group in (enemy_units + enemy_cities, fog):
            candidates = [t for t in group if reachable(t)]
            if candidates:
                return min(candidates, key=lambda t: dist(start, t))

        return None

    def handle_city_actions(self) -> None:
        '''Produce units and collect modifiers'''
        for city in self.game.current_player.cities:
            tile = city.tile
            if not tile.unit:
                if choices([0, 1], [50, 50 + 30 * self.game.bot_difficulty], k=1)[0]:
                    tile.unit = Unit(
                        randint(0, len(UNIT_TYPES) - 1),
                        self.game.current_player,
                        tile.row,
                        tile.col
                    )

            cx, cy = tile.row, tile.col
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    t = self.game.map[cx + dx][cy + dy]
                    mod = t.modifier
                    if mod and mod.cost and not mod.is_collected:
                        if choices([0, 1], [20, 10 + 15 * self.game.bot_difficulty], k=1)[0]:
                            mod.collect()
                            tile.add_population_to_city(mod.population)
