from helpers.terrain.terrain_classes import TileBase, ModifierType, TerrainType, Mountain
from helpers.unit_classes import UnitBase
if __name__ == '__main__':
    from views.game_view import GameView


class MovementSystem:
    def __init__(self, game_view: 'GameView'):
        self.game = game_view
        
    def get_valid_moves(self, start_tile: TileBase) -> list[TileBase]:
        'Get valid moves from a tile using `start_tile.unit.movement`'
        valid_moves = []
        
        if not start_tile or not start_tile.unit:
            return valid_moves
            
        movement_range = start_tile.unit.movement
        visited = []
        queue = [(start_tile, 0)]
        
        while queue:
            current_tile, distance = queue.pop(0)
            
            if current_tile in visited:
                continue
                
            visited.append(current_tile)
            
            if current_tile != start_tile:
                if self._can_move_to_tile(start_tile.unit, current_tile) and distance <= movement_range:
                    valid_moves.append(current_tile)
                    
            if distance >= movement_range:
                continue
                
            for neighbor in self.game.get_neighbors(current_tile):
                if neighbor not in visited and self._is_passable_for_movement(neighbor):
                    queue.append((neighbor, distance + 1))
                    
        return valid_moves
    
    def _can_move_to_tile(self, unit: UnitBase, target_tile: TileBase) -> bool:
        if not self._is_passable_for_movement(target_tile):
            return False
            
        if target_tile.unit is None:
            return True
        elif target_tile.unit.owner != unit.owner:
            return True
            
        return False
    
    def _is_passable_for_movement(self, tile: TileBase) -> bool:
        if tile.type != TerrainType.LAND:
            return False
            
        if tile.modifier and tile.modifier.type in (ModifierType.MOUNTAIN, ModifierType.GOLD_MOUNTAIN):
            if not self.game.current_player.open_tech.tech_map.get(Mountain, False):
                return False
        if tile.unit and tile.unit.owner != self.game.current_player:
            return False
        return True
    
    def move_unit(self, from_tile: TileBase, to_tile: TileBase) -> bool:
        if not from_tile.unit or from_tile.unit.owner != self.game.current_player:
            return False
            
        if not from_tile.unit.move_remains:
            return False
            
        if to_tile.unit:
            if to_tile.unit.owner == self.game.current_player:
                return False
            attack_system = AttackSystem(self.game)
            return attack_system.attack_unit(from_tile, to_tile)
            
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
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            return False


class AttackSystem:
    def __init__(self, game_view: 'GameView'):
        self.game = game_view
        
    # def get_attack_range(self, unit: UnitBase):
    #     return getattr(unit, 'attack_range', 1)
    
    # def get_attack_power(self, unit: UnitBase):
    #     return getattr(unit, 'attack', 10)
    
    def get_defense_bonus(self, tile: TileBase) -> float:
        if tile.modifier:
            if tile.modifier.type in (ModifierType.MOUNTAIN, ModifierType.GOLD_MOUNTAIN):
                return 1.5
            elif tile.modifier.type == ModifierType.FOREST:
                return 1.5
        return 1
    
    def attack_unit(self, attacker_tile: TileBase, defender_tile: TileBase):
        attacker = attacker_tile.unit
        defender = defender_tile.unit
        
        if not attacker or not defender:
            return False
            
        if attacker.owner == defender.owner:
            return False
            
        if not attacker.move_remains:
            return False
            
        distance = max(abs(defender_tile.row - attacker_tile.row), 
                      abs(defender_tile.col - attacker_tile.col))
        
        if distance > attacker.range:
            return False
            
        try:
            self._perform_attack(attacker, defender, attacker_tile, defender_tile)
            return True
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            return False
    
    def _perform_attack(
    self,
    attacker: UnitBase,
    defender: UnitBase,
    attacker_tile: TileBase,
    defender_tile: TileBase
    ) -> None:
        defense_bonus = self.get_defense_bonus(defender_tile)

        atk = attacker.attack * (attacker.health / attacker.max_health)
        dfs = defender.defense * (defender.health / defender.max_health) * defense_bonus

        total = atk + dfs
        dmg_def = round((atk / total) * attacker.attack * 4.5)
        dmg_atk = round((dfs / total) * defender.defense * 4.5)

        defender.health -= dmg_def
        if defender.health <= 0:
            defender.is_alive = False
            defender_tile.unit = None

        if defender.is_alive:
            attacker.health -= dmg_atk
            if attacker.health <= 0:
                attacker.is_alive = False

        if not defender.is_alive:
            attacker.move((defender_tile.row, defender_tile.col))
            defender_tile.unit = attacker
            attacker_tile.unit = None

            self.game.update_visibility_around_unit(defender_tile)

        if not attacker.is_alive:
            attacker_tile.unit = None

        attacker.move_remains = False
        self.game.update_sprites()
    
    def can_attack_from_position(self, attacker_tile: TileBase, target_tile: TileBase):
        attacker = attacker_tile.unit
        if not attacker:
            return False
            
        distance = max(abs(target_tile.row - attacker_tile.row), 
                      abs(target_tile.col - attacker_tile.col))
        
        return distance <= attacker.range
