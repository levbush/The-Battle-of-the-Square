from helpers.terrain.terrain_classes import TileBase, ModifierType
from helpers.unit_classes import UnitBase, Unit, UNIT_TYPES
from random import choices, randint, choice
from collections import deque

if __name__ == '__main__':
    from views.game_view import GameView


EARLY_GAME_MOVES = 5
MAX_EARLY_UNIT_ID = 3
MAX_EARLY_CITY_LEVEL = 1
MAX_BFS_DEPTH = 6


def dist(a: TileBase, b: TileBase) -> int:
    return abs(a.row - b.row) + abs(a.col - b.col)


class BotLogic:
    def __init__(self, game: 'GameView'):
        '''AI controller for a non-human player'''
        self.game = game

    def move(self) -> None:
        game = self.game
        player = game.current_player

        game.update_sprites()

        for unit in player.units:
            unit.move_remains = True
            unit.attack_remains = True
            self.act_unit(game.map[unit.pos[0]][unit.pos[1]])

        self.handle_city_actions()


    def act_unit(self, start_tile: TileBase) -> None:
        unit = start_tile.unit
        if not unit or not unit.is_alive:
            return

        game = self.game
        movement = game.movement_system
        attack = game.attack_system
        player = game.current_player

        if (
            start_tile.city and start_tile.city.owner is not player
            or start_tile.modifier and start_tile.modifier.type == ModifierType.VILLAGE
        ):
            game.capture(start_tile)
            return

        for tile in attack.get_valid_attacks(start_tile):
            if tile.unit and tile.unit.owner is not player:
                attack.attack_unit(start_tile, tile)
                return

        target = self.bfs_find_target(start_tile)
        if not target:
            return

        valid_moves = movement.get_valid_moves(start_tile)
        if not valid_moves:
            return

        tx, ty = target.row, target.col
        best_tile = min(
            valid_moves,
            key=lambda t: abs(t.row - tx) + abs(t.col - ty)
        )

        movement.move_unit(start_tile, best_tile)

    def handle_city_actions(self) -> None:
        '''Produce units and collect modifiers'''
        game = self.game
        player = game.current_player

        is_early_game = game.move_n < EARLY_GAME_MOVES

        for city in player.cities:
            tile = city.tile

            if not tile.unit:
                if choices([0, 1], [50, 50 + 30 * game.bot_difficulty], k=1)[0]:

                    if is_early_game:
                        unit_id = randint(0, MAX_EARLY_UNIT_ID)
                    else:
                        unit_id = randint(0, len(UNIT_TYPES) - 2)

                    tile.unit = Unit(
                        unit_id,
                        player,
                        tile.row,
                        tile.col
                    )
                    player.units.append(tile.unit)

            cx, cy = tile.row, tile.col
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    t = game.map[cx + dx][cy + dy]
                    mod = t.modifier

                    if not mod or not mod.cost or mod.is_collected:
                        continue

                    if (
                        is_early_game
                        and mod.population
                        and city.level >= MAX_EARLY_CITY_LEVEL
                    ):
                        continue

                    if choices([0, 1], [20, 10 + 15 * game.bot_difficulty], k=1)[0]:
                        mod.collect()
                        if tile.add_population_to_city(mod.population):
                            self.game.movement_system.random_move(tile.owner.tile)
                            tile.owner.spawn_giant()


    def bfs_find_target(
        self,
        start: TileBase,
        max_depth: int = 8
    ) -> TileBase | None:
        """
        BFS from unit tile:
        priority:
        1. enemy unit
        2. enemy city
        3. village
        4. fog
        """

        game = self.game
        player = game.current_player

        visited = {start}
        q = deque([(start, 0)])

        while q:
            tile, depth = q.popleft()
            if depth > max_depth:
                break

            if tile.unit and tile.unit.owner is not player:
                return tile

            if tile.city and tile.city.owner is not player:
                return tile

            if tile.modifier and tile.modifier.type == ModifierType.VILLAGE:
                return tile

            for n in game.get_neighbors(tile):
                if n not in visited:
                    visited.add(n)
                    q.append((n, depth + 1))

        return self.game.map[randint(0, self.game.size_map - 1)][randint(0, self.game.size_map - 1)]