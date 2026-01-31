from helpers.terrain.terrain_classes import TileBase, ModifierType, TerrainType, Mountain
from helpers.unit_classes import UnitBase
from helpers.traits import TraitType
from random import choice
import arcade
import math
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
        if not from_tile.unit:
            return False
        if not from_tile.unit.move_remains:
            return False

        return self._perform_movement(from_tile, to_tile)

    def _perform_movement(self, from_tile: TileBase, to_tile: TileBase) -> bool:
        try:
            from_tile.unit.move_remains = False
            if TraitType.MOBILE not in from_tile.unit.traits: from_tile.unit.attack_remains = False

            self.game.update_visibility_around_unit(to_tile)

            to_tile.unit = from_tile.unit
            from_tile.unit = None
            x = (to_tile.col - to_tile.row) * 150 + self.game.width // 2
            y = (to_tile.col + to_tile.row) * 90 + 150
            if not to_tile.unit.owner.is_bot:
                to_tile.unit.sprite.start_move(x + 10, y + 90)
            else:
                to_tile.unit.move([to_tile.row, to_tile.col])
            self.game.update_sprites()
            return True
        except Exception:
            import traceback
            traceback.print_exc()
            return False
        
    def random_move(self, tile: TileBase):
        if not tile.unit: return
        tile.unit.move_remains = True
        tile.unit.attack_remains = True
        moves = self.get_valid_moves(tile)
        if not moves:
            return
        self.move_unit(tile, choice(moves))


class AttackSystem:
    def __init__(self, game_view: 'GameView'):
        self.game = game_view
        self.active_arrows = []

    def get_defense_bonus(self, tile: TileBase) -> float:
        if tile.modifier:
            if tile.modifier.type in (ModifierType.MOUNTAIN, ModifierType.GOLD_MOUNTAIN, ModifierType.FOREST):
                return 1.25
        return 1

    def get_valid_attacks(self, attacker_tile: TileBase) -> list[TileBase]:
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

        if TraitType.RANGED in attacker.traits and not attacker.owner.is_bot:
            self.create_arrow_animation(attacker_tile, defender_tile)

        if not attacker or not defender or attacker.owner == defender.owner:
            return False
        if not (attacker.move_remains or attacker.attack_remains and TraitType.MOBILE in attacker.traits):
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
            defender.owner.units.remove(defender)
            def_tile.unit = None
            attacker.owner.kills += 1

        if defender.is_alive and max(abs(def_tile.row - atk_tile.row), abs(def_tile.col - atk_tile.col)) <= defender.range:
            attacker.health -= round((dfs / total) * defender.defense * 4.5)
            if attacker.health <= 0:
                attacker.is_alive = False

        if not defender.is_alive:
            mover = MovementSystem(self.game)
            if mover._is_passable_for_movement(def_tile) and TraitType.RANGED not in attacker.traits:
                mover._perform_movement(atk_tile, def_tile)
        else:
            x1 = (atk_tile.col - atk_tile.row) * 150 + self.game.width // 2
            y1 = (atk_tile.col + atk_tile.row) * 90 + 150
            x2 = (def_tile.col - def_tile.row) * 150 + self.game.width // 2
            y2 = (def_tile.col + def_tile.row) * 90 + 150
            if not attacker.owner.is_bot:
                attacker.sprite.start_attack(x1 + 10, y1 + 90, x2 + 10, y2 + 90, defender.sprite)
            
        if not attacker.is_alive:
            attacker.owner.units.remove(attacker)
            atk_tile.unit = None

        attacker.move_remains = False
        attacker.attack_remains = False
        self.game.update_sprites()

    def can_attack_from_position(self, attacker_tile: TileBase, target_tile: TileBase):
        attacker = attacker_tile.unit
        if not attacker or not target_tile.visible_mapping[self.game.current_player.id]:
            return False

        distance = max(abs(target_tile.row - attacker_tile.row),
                       abs(target_tile.col - attacker_tile.col))
        return distance <= attacker.range

    def create_arrow_animation(self, from_tile: TileBase, to_tile: TileBase):
        from_x, from_y = self.game.tile_to_world(from_tile)
        to_x, to_y = self.game.tile_to_world(to_tile)
        
        from_y += 90
        to_y += 90
        
        arrow = Arrow(from_x + 10, from_y, to_x + 10, to_y)
        
        self.active_arrows.append(arrow)
        
        self.game.attack_sprites.append(arrow)

    def update_arrow_animations(self, dt):
        arrows_to_remove = []
        
        for arrow in self.active_arrows:
            arrow.update(dt)
            
            if arrow.animation_complete:
                arrows_to_remove.append(arrow)
        
        for arrow in arrows_to_remove:
            self.active_arrows.remove(arrow)
            if arrow in self.game.attack_sprites:
                self.game.attack_sprites.remove(arrow)


class Arrow(arcade.Sprite):
    
    def __init__(self, start_x, start_y, target_x, target_y, speed=500.0):
        texture = arcade.load_texture("assets/animation/arrow.png")
        
        super().__init__(texture, scale=0.5)
        
        self.center_x = start_x
        self.center_y = start_y
        
        self.target_x = target_x
        self.target_y = target_y
        
        self.dx = target_x - start_x
        self.dy = target_y - start_y
        
        distance = math.sqrt(self.dx ** 2 + self.dy ** 2)
        
        if distance > 0:
            self.dx /= distance
            self.dy /= distance
            
            angle_rad = math.atan2(-self.dy, self.dx)
            self.angle = math.degrees(angle_rad)
        
        else:
            self.dx = 0
            self.dy = 0
            self.angle = 0
        
        self.speed = speed
        self.distance = distance
        self.traveled = 0
        
        self.animation_complete = False
        
        self.alpha = 255
    
    def update(self, dt):
        if self.animation_complete:
            return
        
        frame_distance = self.speed * dt
        self.traveled += frame_distance
        
        if self.traveled < self.distance:
            self.center_x += self.dx * frame_distance
            self.center_y += self.dy * frame_distance
        else:
            self.center_x = self.target_x
            self.center_y = self.target_y
            self.animation_complete = True
            self.alpha = 0
    
    def draw(self):
        if self.alpha > 0:
            original_color = self._color
            
            self._color = (original_color[0], original_color[1], original_color[2], self.alpha)
            
            super().draw()
            
            self._color = original_color