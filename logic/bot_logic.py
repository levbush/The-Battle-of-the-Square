from helpers.terrain.terrain_classes import TileBase, ModifierType
from helpers.unit_classes import UnitBase, Unit, UNIT_TYPES
from random import choices, randint, choice

if __name__ == '__main__':
    from views.game_view import GameView


def dist(a: TileBase, b: TileBase) -> int:
    return abs(a.row - b.row) + abs(a.col - b.col)


from helpers.terrain.terrain_classes import TileBase, ModifierType
from helpers.unit_classes import UnitBase, Unit, UNIT_TYPES
from random import choices, randint, choice

if __name__ == '__main__':
    from views.game_view import GameView


def dist(a: TileBase, b: TileBase) -> int:
    return abs(a.row - b.row) + abs(a.col - b.col)


class BotLogic:
    def __init__(self, game: 'GameView'):
        '''AI controller for a non-human player'''
        self.game = game

    def move(self) -> None:
        self.game.update_sprites()

        visible_enemy_units: list[TileBase] = []
        visible_enemy_cities: list[TileBase] = []
        fog: list[TileBase] = []
        own_units: list[TileBase] = []
        villages: list[TileBase] = []

        for row in self.game.map:
            for tile in row:
                if not tile.visible_mapping[self.game.current_player.id]:
                    fog.append(tile)
                    continue

                if tile.unit:
                    if tile.unit.owner == self.game.current_player:
                        tile.unit.move_remains = True
                        tile.unit.attack_remains = True
                        own_units.append(tile)
                    else:
                        visible_enemy_units.append(tile)

                if tile.city and tile.city.owner != self.game.current_player:
                    visible_enemy_cities.append(tile)

                if tile.modifier and tile.modifier.type == ModifierType.VILLAGE:
                    villages.append(tile)

        for tile in own_units:
            if tile.unit and tile.unit.is_alive:
                self.act_unit(tile, visible_enemy_units, visible_enemy_cities, fog, villages)

        self.handle_city_actions()

    def act_unit(
        self,
        start_tile: TileBase,
        enemy_units: list[TileBase],
        enemy_cities: list[TileBase],
        fog: list[TileBase],
        villages: list[TileBase],
    ) -> None:
        unit = start_tile.unit
        if not unit:
            return

        movement = self.game.movement_system
        attack = self.game.attack_system

        for tile in enemy_cities + villages:
            if tile == start_tile:
                self.game.capture(tile)
                return

        valid_moves = movement.get_valid_moves(start_tile)
        if not valid_moves:
            return

        for tile in enemy_units:
            if tile.unit and attack.can_attack_from_position(start_tile, tile):
                attack.attack_unit(start_tile, tile)
                return

        target = self.select_reachable_target(
            start_tile, valid_moves, enemy_units, enemy_cities, fog, villages
        )
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
        fog: list[TileBase],
        villages: list[TileBase]
    ) -> TileBase | None:
        '''Pick nearest target that can be approached'''

        def reachable(target: TileBase) -> bool:
            return any(dist(m, target) < dist(start, target) for m in valid_moves)

        for group in (enemy_units + enemy_cities, villages):
            candidates = [t for t in group if reachable(t)]
            if candidates:
                return min(candidates, key=lambda t: dist(start, t))
        return choice(fog) if fog else None

    def handle_city_actions(self) -> None:
        '''Produce units and collect modifiers'''
        for city in self.game.current_player.cities:
            tile = city.tile
            if not tile.unit:
                if choices([0, 1], [50, 50 + 30 * self.game.bot_difficulty], k=1)[0]:
                    tile.unit = Unit(
                        randint(0, len(UNIT_TYPES) - 2),
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
                            # self.game.movement_system.random_move(tile)
                            tile.add_population_to_city(mod.population)
