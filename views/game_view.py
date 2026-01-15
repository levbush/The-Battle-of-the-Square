import arcade
import arcade.color
from arcade.gui import UIManager, UITextureButton
from views.next_turn_view import NextTurnView
from terrain.create_map import create_map
from classes import Player, TechTree, City
from random import shuffle
from terrain.terrain_classes import *
from pyglet.graphics import Batch
import sqlite3
from database import DB_PATH, init_db, SETTINGS
from views.settings_view import SettingsView
from views.discovery_view import DiscoveryView
from views.winner_view import WinnerView
from unitclasses import *


class MovementSystem:
    def __init__(self, game_view):
        self.game = game_view
        
    def get_valid_moves(self, start_tile: TileBase):
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
    
    def _can_move_to_tile(self, unit, target_tile):
        if not self._is_passable_for_movement(target_tile):
            return False
            
        if target_tile.unit is None:
            return True
        elif target_tile.unit.owner != unit.owner:
            return True
            
        return False
    
    def _is_passable_for_movement(self, tile: TileBase) -> bool:
        if not isinstance(tile, Land):
            return False
            
        if tile.modifier and tile.modifier.type in (ModifierType.MOUNTAIN, ModifierType.GOLD_MOUNTAIN):
            if not self.game.current_player.open_tech.tech_map.get('Mountain', False):
                return False
                
        return True
    
    def move_unit(self, from_tile: TileBase, to_tile: TileBase):
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
    
    def _perform_movement(self, from_tile: TileBase, to_tile: TileBase):
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
    def __init__(self, game_view):
        self.game = game_view
        
    def get_attack_range(self, unit):
        return getattr(unit, 'attack_range', 1)
    
    def get_attack_power(self, unit):
        return getattr(unit, 'attack', 10)
    
    def get_defense_bonus(self, tile: TileBase, defender):
        if tile.modifier:
            if tile.modifier.type in (ModifierType.MOUNTAIN, ModifierType.GOLD_MOUNTAIN):
                return 2
            elif tile.modifier.type == ModifierType.WOODS:
                return 1
        return 0
    
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
        
        if distance > self.get_attack_range(attacker):
            return False
            
        try:
            self._perform_attack(attacker, defender, attacker_tile, defender_tile)
            return True
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            return False
    
    def _perform_attack(self, attacker, defender, attacker_tile, defender_tile):
        attack_power = self.get_attack_power(attacker)
        defense_bonus = self.get_defense_bonus(defender_tile, defender)
        
        damage = max(1, attack_power - defense_bonus)
        
        defender.health -= damage
        
        if not defender.is_alive:
            attacker.move((defender_tile.row, defender_tile.col))
            defender_tile.unit = attacker
            attacker_tile.unit = None
            
            self.game.update_visibility_around_unit(defender_tile)
            
        attacker.move_remains = False
        
        self.game.update_sprites()
    
    def can_attack_from_position(self, attacker_tile, target_tile):
        attacker = attacker_tile.unit
        if not attacker:
            return False
            
        distance = max(abs(target_tile.row - attacker_tile.row), 
                      abs(target_tile.col - attacker_tile.col))
        
        return distance <= self.get_attack_range(attacker)


class GameView(arcade.View):
    def __init__(self, size_map, bot_amount, player_amount, bot_difficulty, new_game=True):
        super().__init__(background_color=arcade.color.SKY_BLUE)
        self.size_map = size_map
        self.player_amount = player_amount
        self.bot_amount = bot_amount
        self.bot_difficulty = bot_difficulty
        self.move = False
        self.move_start = (0, 0)
        self.camera_start = (250 * self.size_map / 4, 250 * self.size_map * (1 / 2 - 1 / 6))
        self.new_game = new_game
        self.click_threshold = 5
        self.mouse_down_pos = None
        self.dragging = False
        self.selected_tile = None
        self.selected_unit = None
        self.selected_modifier = None
        self.selected_city = None
        self.valid_move_tiles = []
        self.path = []
        self.cost_tooltip = None
        self.first_move_in_session = True

        self.world_camera = arcade.camera.Camera2D()
        self.gui_camera = arcade.camera.Camera2D()
        self.manager = UIManager()
        self.manager.enable()
        self.setup()

    def setup(self):
        if self.new_game:
            self.players: list[Player] = []
            for i in range(self.player_amount - 1):
                self.players.append(Player(None, False))
            for i in range(self.bot_amount):
                self.players.append(Player(None, True))
            shuffle(self.players)
            self.players.insert(0, Player(None, False))
            for i in range(self.player_amount + self.bot_amount):
                self.players[i].id = i
            self.current_player: Player | None = None

            self.map = create_map(self.size_map, self.players)
            self.move_n = 0

        else:
            self.load_game()

        self.tiles = arcade.SpriteList(use_spatial_hash=True)
        self.modifiers = arcade.SpriteList(use_spatial_hash=True)
        self.cities = arcade.SpriteList(use_spatial_hash=True)
        self.units = arcade.SpriteList(use_spatial_hash=True)
        self.move_popups = arcade.SpriteList()
        self.next_turn_btn = UITextureButton(
            x=self.width // 2 + self.width * 0.075,
            y=self.height * 0.05,
            texture=arcade.load_texture("assets/misc/next_turn.png"),
            scale=2,
        )
        self.tech_btn = UITextureButton(
            x=self.width // 2 + self.width * 0.035,
            y=self.height * 0.05,
            texture=arcade.load_texture('assets/misc/techbg.png'),
            scale=0.2098,
        )
        self.manager.add(self.next_turn_btn)
        self.manager.add(self.tech_btn)
        self.next_turn_btn.on_click = lambda *_: self.change_POV()
        self.tech_btn.on_click = lambda *_: self.window.show_view(DiscoveryView(self))
        self.city_tooltips = []
        self.health_tooltips = []

        self.spr_texture_fog = arcade.load_texture("assets/terrain/fog.png")
        self.bot_city_textures = [arcade.load_texture(f'assets/cities/bot/House_{i}.png') for i in range(6)]
        self.player_city_textures = [arcade.load_texture(f'assets/cities/player/House_{i}.png') for i in range(6)]
        self.enemy_city_textures = [arcade.load_texture(f'assets/cities/enemy/House_{i}.png') for i in range(6)]
        self.city_textures = {
            'bot': self.bot_city_textures,
            'ally': self.player_city_textures,
            'enemy': self.enemy_city_textures,
        }
        self.resource = arcade.load_texture('assets/misc/resource.png')
        self.science = arcade.load_texture("assets/misc/science.png")
        self.move_tooltip = arcade.load_texture('assets/misc/moveTarget.png')
        self.attack_tooltip = arcade.load_texture('assets/misc/attackTarget.png')
        self.batch = Batch()
        self.world_batch = Batch()
        self.star_label = arcade.Text(
            '',
            self.width / 2 - 50,
            self.height - 30,
            font_size=20,
            color=arcade.color.BLACK,
            anchor_y='center',
            batch=self.batch,
        )
        self.move_label = arcade.Text(
            '',
            self.width / 2 - 250,
            self.height - 30,
            font_size=20,
            color=arcade.color.BLACK,
            anchor_y='center',
            batch=self.batch,
        )

        self.movement_system = MovementSystem(self)
        self.attack_system = AttackSystem(self)

    def on_show_view(self):
        self.manager.enable()
        if self.current_player is None or self.first_move_in_session:
            self.change_POV()

    def change_POV(self):
        self.world_camera.position = self.camera_start
        self.world_camera.zoom = 0.5 ** (((121, 196, 256, 324, 400, 900).index(self.size_map**2) + 1) / 2)
        
        if self.check_win():
            return
            

        if self.current_player is None or self.first_move_in_session:
            if self.current_player is None:
                self.current_player = self.players[0]
            self.first_move_in_session = False
            self.make_player_move()
        else:
            prev = self.current_player.id
            self.current_player = self.players[(self.current_player.id + 1) % len(self.players)]

            while self.current_player.is_bot or not self.current_player.is_alive:
                if self.current_player.is_bot and self.current_player.is_alive:
                    self.make_bot_move()
                    self.current_player = self.players[(self.current_player.id + 1) % len(self.players)]
                    continue
            if self.current_player.id <= prev:
                self.move_n += 1
            self.make_player_move()

        self.deselect_all()
        self.valid_move_tiles = []
        self.path = []

        self.update_sprites()

        view = NextTurnView(self.current_player, parent=self)
        arcade.get_window().show_view(view)

    def next_turn(self):
        self.window.show_view(self)
        self.manager.enable()

    def on_draw(self):
        self.clear()
        self.world_camera.use()
        self.tiles.draw()
        self.modifiers.draw()
        self.cities.draw()
        self.units.draw()
        self.draw_selection_highlight()
        self.draw_city_borders()
        self.world_batch.draw()
        self.draw_valid_moves()
        self.gui_camera.use()
        self.manager.draw()
        arcade.draw_texture_rect(self.resource, arcade.rect.LBWH(self.width / 2 - 120, self.height - 50, 40, 40))
        arcade.draw_texture_rect(
            self.science, arcade.rect.LBWH(self.width // 2 + self.width * 0.035, self.height * 0.05, 60, 60)
        )

        self.batch.draw()

    def draw_city_borders(self):
        for row_idx, row in enumerate(self.map):
            for col_idx, tile in enumerate(row):
                if tile.city and tile.visible_mapping[self.current_player.id]:
                    if tile.city.owner == self.current_player:
                        color = arcade.color.BLUE
                    elif tile.city.owner.is_bot:
                        color = arcade.color.RED
                    else:
                        color = arcade.color.RED

                    city_x, city_y = self.tile_to_world(tile)
                    city_y += 55

                    points = [
                        (city_x, city_y + 270),
                        (city_x + 450, city_y),
                        (city_x, city_y - 270),
                        (city_x - 450, city_y),
                    ]

                    arcade.draw_polygon_outline(points, color, 3)

    def on_mouse_press(self, x, y, button, modifiers):
        if button == arcade.MOUSE_BUTTON_LEFT:
            self.mouse_down_pos = (x, y)
            self.dragging = False
            self.move = True
            self.move_start = (x, y)
            self.camera_start = self.world_camera.position

    def on_mouse_motion(self, x, y, dx, dy):
        if not self.move:
            return

        dist = abs(x - self.mouse_down_pos[0]) + abs(y - self.mouse_down_pos[1])
        if dist > self.click_threshold:
            self.dragging = True

        if self.dragging:
            dx = x - self.move_start[0]
            dy = y - self.move_start[1]
            self.world_camera.position = (self.camera_start[0] - dx, self.camera_start[1] - dy)

    def on_mouse_release(self, x, y, button, modifiers):
        match button:
            case arcade.MOUSE_BUTTON_LEFT:
                self.move = False
                if not self.dragging:
                    self.handle_click(x, y)
                self.dragging = False
                self.mouse_down_pos = None
            case arcade.MOUSE_BUTTON_RIGHT:
                self.handle_right_click(x, y)

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        zoom_speed = 0.1
        min_zoom = 0.2
        max_zoom = 3.0

        current_zoom = self.world_camera.zoom

        if scroll_y > 0:
            new_zoom = current_zoom * (1 + zoom_speed)
        elif scroll_y < 0:
            new_zoom = current_zoom * (1 - zoom_speed)
        else:
            return

        new_zoom = max(min_zoom, min(max_zoom, new_zoom))

        zoom_point_x = x - 150

        mouse_world_x_before = self.world_camera.position[0] + (zoom_point_x - self.window.width / 2) / current_zoom
        mouse_world_y_before = self.world_camera.position[1] + (zoom_point_x - self.window.height / 2) / current_zoom

        self.world_camera.zoom = new_zoom

        mouse_world_x_after = self.world_camera.position[0] + (zoom_point_x - self.window.width / 2) / new_zoom
        mouse_world_y_after = self.world_camera.position[1] + (zoom_point_x - self.window.height / 2) / new_zoom

        self.world_camera.position = (
            self.world_camera.position[0] - (mouse_world_x_after - mouse_world_x_before),
            self.world_camera.position[1] - (mouse_world_y_after - mouse_world_y_before),
        )

    def draw_selection_highlight(self):
        if not self.selected_tile:
            return

        x, y = self.tile_to_world(self.selected_tile)

        if self.selected_unit:
            arcade.draw_circle_outline(
                center_x=x + 10, center_y=y + 90, radius=40, color=arcade.color.YELLOW, border_width=4
            )

        if self.selected_modifier or self.selected_city:
            width = 120
            height = 80
            left = x - width / 2
            right = x + width / 2
            bottom = y + 70 + bool(self.selected_city) * 20 - height / 2
            top = y + 70 + bool(self.selected_city) * 20 + height / 2

            arcade.draw_lrbt_rectangle_outline(
                left=left, right=right, bottom=bottom, top=top, color=arcade.color.BLEU_DE_FRANCE, border_width=4
            )
            if (
                self.is_collectible(self.selected_tile)
            ):
                self.cost_tooltip = arcade.Text(
                    str(self.selected_modifier.cost),
                    right,
                    top,
                    arcade.color.BLACK,
                    anchor_x='center',
                    anchor_y='center',
                    batch=self.world_batch,
                    font_size=24,
                )

    def draw_valid_moves(self):
        self.move_popups.clear()
        for tile in self.valid_move_tiles:
            x, y = self.tile_to_world(tile)

            if tile.unit and tile.unit.owner != self.current_player:
                if self.attack_system.can_attack_from_position(self.selected_tile, tile):
                    texture = self.attack_tooltip
                else:
                    continue
            else:
                texture = self.move_tooltip
                
            self.move_popups.append(
                arcade.Sprite(texture, 0.5, x, y + 60)
            )
        self.move_popups.draw()

    def screen_to_world(self, x, y):
        cam = self.world_camera
        world_x = cam.position[0] + (x - self.window.width / 2) / cam.zoom
        world_y = cam.position[1] + (y - 35 - self.window.height / 2) / cam.zoom
        return world_x, world_y

    def screen_to_tile(self, x, y) -> TileBase | None:
        world_x, world_y = self.screen_to_world(x, y)
        world_x -= self.width // 2
        world_y -= 150

        col = round((world_x / 150 + world_y / 90) / 2)
        row = round((world_y / 90 - world_x / 150) / 2)

        if 0 <= row < len(self.map) and 0 <= col < len(self.map[row]):
            return self.map[row][col]
        return None

    def tile_to_world(self, tile: TileBase):
        x = (tile.col - tile.row) * 150 + self.width // 2
        y = (tile.col + tile.row) * 90 + 150
        return x, y

    def get_neighbors(self, tile: TileBase):
        neighbors = []

        directions = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]

        for dr, dc in directions:
            new_row = tile.row + dr
            new_col = tile.col + dc

            if 0 <= new_row < len(self.map) and 0 <= new_col < len(self.map[new_row]):
                neighbor = self.map[new_row][new_col]

                if neighbor.visible_mapping[self.current_player.id]:
                    neighbors.append(neighbor)

        return neighbors

    def get_tiles_in_range(self, center_tile: TileBase, radius: int):
        tiles_in_range = []

        for dr in range(-radius, radius + 1):
            for dc in range(-radius, radius + 1):
                new_row = center_tile.row + dr
                new_col = center_tile.col + dc

                if (
                    0 <= new_row < len(self.map)
                    and 0 <= new_col < len(self.map[new_row])
                    and max(abs(dr), abs(dc)) <= radius
                ):

                    tile = self.map[new_row][new_col]
                    tiles_in_range.append(tile)

        return tiles_in_range

    def update_visibility_around_unit(self, unit_tile: TileBase):
        player_id = self.current_player.id

        visible_tiles = self.get_tiles_in_range(unit_tile, 1)

        for tile in visible_tiles:
            tile.visible_mapping[player_id] = True

    def is_passable(self, tile: TileBase) -> bool:
        return isinstance(tile, Land) and (not (tile.modifier and tile.modifier.type in (ModifierType.MOUNTAIN, ModifierType.GOLD_MOUNTAIN)) or self.current_player.open_tech.tech_map[Mountain])
    

    def is_collectible(self, tile: TileBase) -> bool:
        if not tile.modifier:
            return False
        if tile.modifier.cost is None:
            return False
        if tile.modifier.is_collected:
            return False
        if self.selected_tile.owner is None or self.selected_tile.owner.owner != self.current_player:
            return False
        if self.current_player.stars < self.selected_modifier.cost:
            False
        
        return self.current_player.open_tech.tech_map.get(tile.modifier.__class__, True)
    
    def calculate_valid_moves(self, start_tile: TileBase):
        self.valid_move_tiles = self.movement_system.get_valid_moves(start_tile)
        self.path = []

    def move_unit(self, from_tile: TileBase, to_tile: TileBase):
        success = self.movement_system.move_unit(from_tile, to_tile)
        
        if success:
            self.selected_unit = None
            self.selected_tile = None
            self.valid_move_tiles = []
            self.path = []
            
        return success

    def reset_all(self):
        self.tiles.clear()
        self.modifiers.clear()
        self.cities.clear()
        self.units.clear()
        self.city_tooltips.clear()
        self.health_tooltips.clear()
        self.deselect_all()

    def update_sprites(self):
        self.reset_all()
        self.star_label.text = f'{self.current_player.stars} (+ {self.get_stars_for_player()})'

        for row_idx, row in enumerate(self.map):
            for col_idx, tile in enumerate(row):
                screen_x = (col_idx - row_idx) * 150 + self.width // 2
                screen_y = (col_idx + row_idx) * 90 + 150

                if not tile.visible_mapping[self.current_player.id]:
                    self.tiles.append(arcade.Sprite(self.spr_texture_fog, 0.3, screen_x, screen_y))
                    continue

                self.tiles.append(arcade.Sprite(tile.texture.texture, 0.3, screen_x, screen_y))

                if tile.modifier:
                    for i in range(len(tile.modifier.textures)):
                        self.modifiers.append(
                            arcade.Sprite(
                                tile.modifier.textures[i].texture,
                                tile.modifier.scales[i],
                                screen_x,
                                screen_y + tile.modifier.offsets[i],
                            )
                        )
                elif tile.city:
                    if tile.city.owner.is_bot:
                        texture = 'bot'
                    elif tile.city.owner == self.current_player:
                        texture = 'ally'
                    else:
                        texture = 'enemy'
                    self.cities.append(
                        arcade.Sprite(self.city_textures[texture][tile.city.level], 0.5, screen_x, screen_y + 150)
                    )
                    self.city_tooltips.append(
                        arcade.Text(
                            f'{tile.city.population}/{tile.city.level + 2}',
                            screen_x + 50,
                            screen_y + 140,
                            arcade.color.BLACK,
                            batch=self.world_batch,
                            anchor_x='center',
                            anchor_y='center',
                            font_size=24,
                        )
                    )

                if tile.unit:
                    if tile.unit.owner == self.current_player:
                        texture = tile.unit.textures.ally
                    elif tile.unit.owner.is_bot:
                        texture = tile.unit.textures.bot
                    else:
                        texture = tile.unit.textures.enemy
                    self.units.append(arcade.Sprite(texture, 0.5, center_x=screen_x + 10, center_y=screen_y + 90))

                    self.health_tooltips.append(
                        arcade.Text(
                            f"{tile.unit.health}",
                            screen_x - 50,
                            screen_y + 130,
                            arcade.color.WHITE,
                            30,
                            anchor_x="center",
                            anchor_y="center",
                            bold=True,
                            batch=self.world_batch,
                        )
                    )

        self.tiles.reverse()
        self.modifiers.reverse()
        self.cities.reverse()
        self.units.reverse()

    def make_bot_move(self):
        if not self.current_player.is_bot or not self.current_player.is_alive:
            return
        pass

    def get_stars_for_player(self) -> int:
        return sum((city.level + 1) for city in self.current_player.cities) + 1

    def make_player_move(self):
        stars = self.get_stars_for_player()
        self.current_player.stars += stars
        self.star_label.text = f'{self.current_player.stars} (+ {stars})'
        self.move_label.text = f'Ход {self.move_n}'

        for row in self.map:
            for tile in row:
                if tile.unit and tile.unit.owner == self.current_player:
                    tile.unit.move_remains = True
                    self.update_visibility_around_unit(tile)

        self.update_sprites()

    def select_unit(self, tile: TileBase):
        if tile.unit and not tile.unit.move_remains:
            return False

        self.selected_unit = tile.unit
        self.selected_tile = tile
        self.valid_move_tiles = []
        self.path = []

        self.calculate_valid_moves(tile)
        return True

    def select_modifier(self, tile: TileBase):
        self.selected_tile = tile
        self.selected_modifier = tile.modifier
        self.valid_move_tiles = []
        self.path = []

    def select_city(self, tile: TileBase):
        self.selected_tile = tile
        self.selected_city = tile.city
        self.valid_move_tiles = []
        self.path = []

    def handle_click(self, x: float, y: float):
        self.cost_tooltip = None
        tile = self.screen_to_tile(x, y)
        if not tile:
            self.deselect_all()
            return

        if not tile.visible_mapping[self.current_player.id]:
            self.deselect_all()
            return

        if self.selected_unit and tile in self.valid_move_tiles:
            self.move_unit(self.selected_tile, tile)
            return

        if tile == self.selected_tile:
            self.switch_selection_on_tile(tile)
            return

        if self.selected_tile and tile != self.selected_tile:
            self.deselect_all()

        self.primary_selection(tile)

    def handle_right_click(self, x, y):
        if (
            not self.selected_tile
            or self.selected_tile.owner is None
            or self.selected_tile.owner.owner != self.current_player
            or not self.selected_modifier
        ):
            return
        tile = self.screen_to_tile(x, y)
        if tile != self.selected_tile:
            return
        if not self.is_collectible(tile):
            return
        tile.add_population_to_city(self.selected_modifier.population)
        tile.modifier.collect()
        self.current_player.stars -= self.selected_modifier.cost
        self.update_sprites()

    def switch_selection_on_tile(self, tile: TileBase):
        if self.selected_unit:
            if tile.modifier:
                self.deselect_all()
                self.select_modifier(tile)
            elif tile.city:
                self.deselect_all()
                self.select_city(tile)
            else:
                self.deselect_all()

        elif self.selected_modifier:
            if tile.unit and tile.unit.owner == self.current_player:
                self.deselect_all()
                self.select_unit(tile)
            elif tile.city:
                self.deselect_all()
                self.select_city(tile)
            else:
                self.deselect_all()

        elif self.selected_city:
            if tile.unit and tile.unit.owner == self.current_player:
                self.deselect_all()
                self.select_unit(tile)
            elif tile.modifier:
                self.deselect_all()
                self.select_modifier(tile)
            else:
                self.deselect_all()

        else:
            self.primary_selection(tile)

    def primary_selection(self, tile: TileBase):
        if tile.unit:
            if tile.unit.owner == self.current_player:
                if self.select_unit(tile):
                    return
            else:
                self.deselect_all()
        if tile.city:
            self.select_city(tile)
        elif tile.modifier:
            self.select_modifier(tile)
        else:
            self.deselect_all()

    def deselect_all(self):
        self.selected_unit = None
        self.selected_modifier = None
        self.selected_city = None
        self.selected_tile = None
        self.valid_move_tiles = []
        self.path = []
        self.move_popups.clear()
        self.cost_tooltip = None

    def on_key_press(self, key, modifiers):
        if key == arcade.key.ESCAPE:
            arcade.get_window().show_view(SettingsView(parent=self))

        if key == arcade.key.H:
            arcade.get_window().show_view(DiscoveryView(parent=self))

    def check_win(self) -> bool:
        if all(player.is_bot or not player.is_alive for player in self.players): self.end_game(); return True
        p = None
        c = 0
        for player in self.players:
            if player.is_alive:
                c += 1
                p = player
        if c > 1 or (len(self.players) == 1 and c == 1):
            return False
        self.end_game(p)
        return True

    def end_game(self, winner=None):
        self.window.show_view(WinnerView(winner, self))

    def save_map(self):
        with open(DB_PATH, 'w'):
            pass

        init_db()
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()

        data = [
            (x, y, repr(self.map[x][y]))
            for x in range(self.size_map)
            for y in range(self.size_map)
        ]

        c.executemany(
            '''
            INSERT OR REPLACE INTO map (x, y, value)
            VALUES (?, ?, ?)
            ''',
            data
        )

        c.executemany(
            'INSERT OR REPLACE INTO players (id, value) VALUES (?, ?)',
            [(p.id, repr(p)) for p in self.players]
        )

        c.executemany(
            'INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)',
            [(k, getattr(self.window, k) * 100) for k in SETTINGS]
        )

        game_state = {
            "current_player": self.current_player.id,
            "move_n": self.move_n,
            "size_map": self.size_map,
            "bot_amount": self.bot_amount,
            "player_amount": self.player_amount,
            "bot_difficulty": self.bot_difficulty,
        }

        c.executemany(
            'INSERT OR REPLACE INTO game_state (key, value) VALUES (?, ?)',
            [(k, str(v)) for k, v in game_state.items()]
        )

        conn.commit()
        conn.close()

    def load_game(self):
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        self.map = [[0 for _ in range(self.size_map)] for _ in range(self.size_map)]
        c.execute('SELECT value FROM players')
        self.players = [eval(v) for (v,) in c.fetchall()]
        players_by_id = {p.id: p for p in self.players}

        c.execute('SELECT x, y, value FROM map')
        for x, y, value in c.fetchall():
            print(value)
            tile: TileBase = eval(value)
            tile.row = x
            tile.col = y

            if tile.unit:
                tile.unit.owner = players_by_id[tile.unit.owner.id]

            if tile.city:
                tile.city.owner = players_by_id[tile.city.owner.id]

            if tile.owner:
                tile.owner.owner = players_by_id[tile.owner.owner.id]

            self.map[x][y] = tile

        c.execute('SELECT key, value FROM settings')
        for key, value in c.fetchall():
            setattr(self.window, key, value / 100)

        c.execute('SELECT key, value FROM game_state')
        game_state = {k: eval(v) for k, v in c.fetchall()}

        if "current_player" in game_state:
            self.current_player = players_by_id[game_state["current_player"]]

        if "move_n" in game_state:
            self.move_n = game_state["move_n"]

        conn.close()