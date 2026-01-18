from helpers.terrain.terrain_classes import TileBase, ModifierType, TerrainType, Mountain
from helpers.unit_classes import UnitBase
if __name__ == '__main__':
    from views.game_view import GameView


class MovementSystem:
    def __init__(self, game_view: 'GameView'):
        self.game = game_view

    def get_valid_moves(self, start_tile: TileBase) -> list[TileBase]:
        'Return all tiles the unit can move to this turn.'
        valid_moves = []
        if not start_tile or not start_tile.unit:
            return valid_moves

        movement_range = start_tile.unit.movement
        visited = set()
        queue = [(start_tile, 0)]

        while queue:
            current_tile, distance = queue.pop(0)
            if current_tile in visited:
                continue
            visited.add(current_tile)

            if current_tile != start_tile and distance <= movement_range:
                if self._can_move_to_tile(current_tile):
                    valid_moves.append(current_tile)

            if distance >= movement_range:
                continue

            for neighbor in self.game.get_neighbors(current_tile):
                if neighbor not in visited and self._is_passable_for_movement(neighbor):
                    queue.append((neighbor, distance + 1))

        return valid_moves

    def _can_move_to_tile(self, tile: TileBase) -> bool:
        return self._is_passable_for_movement(tile) and tile.unit is None

    def _is_passable_for_movement(self, tile: TileBase) -> bool:
        if tile.type != TerrainType.LAND:
            return False
        if tile.modifier and tile.modifier.type in (ModifierType.MOUNTAIN, ModifierType.GOLD_MOUNTAIN):
            if not self.game.current_player.open_tech.tech_map.get(Mountain, False):
                return False
        if tile.unit is not None:
            return False
        return True

    def move_unit(self, from_tile: TileBase, to_tile: TileBase) -> bool:
        if not from_tile.unit or from_tile.unit.owner != self.game.current_player:
            return False
        if not from_tile.unit.move_remains:
            return False

        if to_tile.unit and to_tile.unit.owner != from_tile.unit.owner:
            return self.game.attack_system.attack_unit(from_tile, to_tile)

        return self._perform_movement(from_tile, to_tile)

    def _perform_movement(self, from_tile: TileBase, to_tile: TileBase) -> bool:
        try:
            from_tile.unit.move((to_tile.row, to_tile.col))
            from_tile.unit.move_remains = False

            self.game.update_visibility_around_unit(to_tile)

            to_tile.unit = from_tile.unit
            from_tile.unit = None

            self.game.update_sprites()
            return True
        except Exception:
            import traceback
            traceback.print_exc()
            return False


class AttackSystem:
    def __init__(self, game_view: 'GameView'):
        self.game = game_view

    def get_defense_bonus(self, tile: TileBase) -> float:
        if tile.modifier:
            if tile.modifier.type in (ModifierType.MOUNTAIN, ModifierType.GOLD_MOUNTAIN, ModifierType.FOREST):
                return 1.5
        return 1

    def get_valid_attacks(self, attacker_tile: TileBase) -> list[TileBase]:
        """Return all enemy tiles this unit can attack using BFS style."""
        valid_attacks = []
        attacker = attacker_tile.unit
        if not attacker:
            return valid_attacks

        attack_range = attacker.range
        visited = set()
        queue = [(attacker_tile, 0)]

        while queue:
            current_tile, distance = queue.pop(0)
            key = (current_tile.row, current_tile.col)
            if key in visited:
                continue
            visited.add(key)

            if distance > 0 and distance <= attack_range:
                if current_tile.unit and current_tile.unit.owner != attacker.owner:
                    valid_attacks.append(current_tile)

            if distance >= attack_range:
                continue

            for neighbor in self.game.get_neighbors(current_tile):
                neighbor_key = (neighbor.row, neighbor.col)
                if neighbor_key not in visited:
                    queue.append((neighbor, distance + 1))

        return valid_attacks


    def attack_unit(self, attacker_tile: TileBase, defender_tile: TileBase):
        attacker = attacker_tile.unit
        defender = defender_tile.unit

        if not attacker or not defender or attacker.owner == defender.owner:
            return False
        if not attacker.move_remains:
            return False
        if not defender_tile.visible_mapping[self.game.current_player.id]:
            return False

        distance = max(abs(defender_tile.row - attacker_tile.row),
                       abs(defender_tile.col - attacker_tile.col))
        if distance > attacker.range:
            return False

        try:
            self._perform_attack(attacker, defender, attacker_tile, defender_tile)
            return True
        except Exception:
            import traceback
            traceback.print_exc()
            return False

    def _perform_attack(self, attacker: UnitBase, defender: UnitBase, atk_tile: TileBase, def_tile: TileBase):
        defense_bonus = self.get_defense_bonus(def_tile)

        atk = attacker.attack * (attacker.health / attacker.max_health)
        dfs = defender.defense * (defender.health / defender.max_health) * defense_bonus
        total = atk + dfs

        defender.health -= round((atk / total) * attacker.attack * 4.5)
        if defender.health <= 0:
            defender.is_alive = False
            def_tile.unit = None

        if defender.is_alive and max(abs(def_tile.row - atk_tile.row), abs(def_tile.col - atk_tile.col)) <= defender.range:
            attacker.health -= round((dfs / total) * defender.defense * 4.5)
            if attacker.health <= 0:
                attacker.is_alive = False

        if not defender.is_alive:
            mover = MovementSystem(self.game)
            if mover._is_passable_for_movement(def_tile) and not attacker.is_ranged:
                attacker.move((def_tile.row, def_tile.col))
                def_tile.unit = attacker
                atk_tile.unit = None
                self.game.update_visibility_around_unit(def_tile)

        if not attacker.is_alive:
            atk_tile.unit = None

        attacker.move_remains = False
        self.game.update_sprites()

    def can_attack_from_position(self, attacker_tile: TileBase, target_tile: TileBase):
        attacker = attacker_tile.unit
        if not attacker or not target_tile.visible_mapping[self.game.current_player.id]:
            return False

        distance = max(abs(target_tile.row - attacker_tile.row),
                       abs(target_tile.col - attacker_tile.col))
        return distance <= attacker.range
