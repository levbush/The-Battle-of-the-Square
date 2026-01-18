import arcade
import sqlite3
import time
from arcade.gui import UIManager, UITextureButton
from views.next_turn_view import NextTurnView
from helpers.terrain.create_map import create_map
from helpers.classes import Player, TechTree, City
from random import shuffle
from helpers.terrain.terrain_classes import *
from pyglet.graphics import Batch
from database import DB_PATH, init_db, SETTINGS
from views.settings_view import SettingsView
from views.discovery_view import DiscoveryView
from views.winner_view import WinnerView
from helpers.unit_classes import *
from logic.bot_logic import BotLogic
from logic.move_logic import MovementSystem, AttackSystem
from typing import Literal
from views.statistics_view import StatisticsView


class GameView(arcade.View):
    def __init__(self, size_map: int, bot_amount: int, player_amount: int, bot_difficulty: Literal[0, 1] | None, new_game: bool=True):
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
        self.unit_btns = []
        self.unit_cost_tooltips = []
        self.first_move_in_session = True

        self.world_camera = arcade.camera.Camera2D()
        self.gui_camera = arcade.camera.Camera2D()
        self.manager = UIManager()
        self.manager.enable()
        self.manager1 = UIManager()
        self.manager1.enable()
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
        self.info_btn = UITextureButton(
            x=self.width // 2 + self.width * 0.075 + 65,
            y=self.height * 0.05 + 7,
            texture=arcade.load_texture("assets/misc/infoSymbol.png"),
            scale=0.5,
        )
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
        self.manager.add(self.info_btn)
        self.manager.add(self.next_turn_btn)
        self.manager.add(self.tech_btn)
        self.info_btn.on_click = lambda *_: self.window.show_view(StatisticsView(parent=self, player_name=self.current_player.id + 1, turn=self.move_n, units_killed=self.current_player.kills))
        self.next_turn_btn.on_click = lambda *_: self.change_POV()
        self.tech_btn.on_click = lambda *_: self.window.show_view(DiscoveryView(self))
        self.city_tooltips = []
        self.health_tooltips = []

        self.spr_texture_fog = arcade.load_texture("assets/terrain/fog.png")
        # self.bot_city_textures = [arcade.load_texture(f'assets/cities/bot/House_{i}.png') for i in range(6)]
        # self.player_city_textures = [arcade.load_texture(f'assets/cities/player/House_{i}.png') for i in range(6)]
        # self.enemy_city_textures = [arcade.load_texture(f'assets/cities/enemy/House_{i}.png') for i in range(6)]
        # self.city_textures = {
        #     'bot': self.bot_city_textures,
        #     'ally': self.player_city_textures,
        #     'enemy': self.enemy_city_textures,
        # }
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
        self.bot_logic = BotLogic(self)

    def on_show_view(self):
        self.manager.enable()
        if self.current_player is None or self.first_move_in_session:
            self.change_POV()

    def change_POV(self):
        now = time.time()
        if now - getattr(self, "_last_turn_time", 0) < 0.2:
            return
        self._last_turn_time = now
        self._change_POV_internal()


    def _change_POV_internal(self):
        if self.next_turn_btn.disabled:
            return
        self.next_turn_btn.disabled = True
    
        self.world_camera.position = self.camera_start
        self.world_camera.zoom = 0.5 ** (((121, 196, 256, 324, 400, 900).index(self.size_map**2) + 1) / 2)
        
        if self.check_win():
            return

        if self.current_player is None or self.first_move_in_session:
            if self.current_player is None:
                self.current_player = self.players[0]
            self.make_player_move()
            self.first_move_in_session = False
        else:
            prev = self.current_player.id
            self.current_player = self.players[(self.current_player.id + 1) % len(self.players)]

            while self.current_player.is_bot or not self.current_player.is_alive:
                if self.current_player.is_bot and self.current_player.is_alive:
                    self.make_bot_move()
                    if self.check_win():
                        return
                self.current_player = self.players[(self.current_player.id + 1) % len(self.players)]
            if self.current_player.id <= prev:
                self.move_n += 1
            self.make_player_move()

        self.deselect_all()
        self.update_sprites()

        view = NextTurnView(self.current_player, parent=self)
        arcade.get_window().show_view(view)

    def next_turn(self):
        self.window.show_view(self)
        self.manager.enable()
        self.next_turn_btn.disabled = False

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
        self.on_draw_ui()
        self.gui_camera.use()
        self.manager.draw()
        arcade.draw_texture_rect(self.resource, arcade.rect.LBWH(self.width / 2 - 120, self.height - 50, 40, 40))
        arcade.draw_texture_rect(
            self.science, arcade.rect.LBWH(self.width // 2 + self.width * 0.035, self.height * 0.05, 60, 60)
        )

        self.batch.draw()
    
    def on_draw_ui(self):
        self.manager1.draw()

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
            dx = (x - self.move_start[0]) * 2
            dy = (y - self.move_start[1]) * 2
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
        max_zoom = 1.5

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
        """Draw move and attack highlights on tiles."""
        self.move_popups.clear()

        for tile in self.valid_move_tiles:
            x, y = self.tile_to_world(tile)
            self.move_popups.append(arcade.Sprite(self.move_tooltip, 0.5, x, y + 60))

        for tile in self.valid_attack_tiles:
            x, y = self.tile_to_world(tile)
            self.move_popups.append(arcade.Sprite(self.attack_tooltip, 0.5, x, y + 60))

        self.move_popups.draw()

    def screen_to_world(self, x, y):
        cam = self.world_camera
        world_x = cam.position[0] + (x - self.window.width / 2) / cam.zoom
        world_y = cam.position[1] + (y - 35 - self.window.height / 2) / cam.zoom
        return world_x, world_y

    def screen_to_tile(self, x, y) -> TileBase | None:
        world_x, world_y = self.screen_to_world(x, y)
        world_x -= self.width / 2
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
        
        return self.current_player.open_tech.tech_map.get(tile.modifier.__class__, True)
    
    def calculate_valid_moves(self, start_tile: TileBase):
        """Compute and store valid move and attack tiles for the selected unit."""
        self.valid_move_tiles = self.movement_system.get_valid_moves(start_tile)
        self.valid_attack_tiles = self.attack_system.get_valid_attacks(start_tile)
        self.path = []


    def move_unit(self, from_tile: TileBase, to_tile: TileBase):
        success = self.movement_system.move_unit(from_tile, to_tile)
        
        if success:
            self.deselect_all()
            
        return success
    
    def attack_unit(self, from_tile: TileBase, to_tile: TileBase):
        success = self.attack_system.attack_unit(from_tile, to_tile)
        
        if success:
            self.deselect_all()
            
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
                    self.cities.append(
                        arcade.Sprite(tile.city.texture.texture, 0.5, screen_x, screen_y + 150)
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
                    self.units.append(arcade.Sprite(tile.unit.texture.texture, 0.5, center_x=screen_x + 10, center_y=screen_y + 90))

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

                if tile.unit and tile.city:
                    if tile.unit.owner != tile.city.owner:
                        self.capture_btn = UITextureButton(
                            x=tile.row * 120,
                            y=tile.col * 80,
                            texture=arcade.load_texture("assets/misc/capture.png"),
                            scale=0.2,
                        )
                        self.manager1.add(self.capture_btn)
                        self.capture_btn.on_click = lambda *_: self.capture(tile)

        self.tiles.reverse()
        self.modifiers.reverse()
        self.cities.reverse()
        self.units.reverse()

    def make_bot_move(self):
        if not self.current_player.is_bot or not self.current_player.is_alive:
            return
        self.bot_logic.move()

    def get_stars_for_player(self) -> int:
        return sum((city.level + 1) for city in self.current_player.cities) + 1

    def make_player_move(self):
        if self.new_game or not self.first_move_in_session:
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
        """Select a unit for moving or attacking."""
        if not tile.unit or not tile.unit.move_remains:
            return False

        self.selected_unit = tile.unit
        self.selected_tile = tile
        self.valid_move_tiles = []
        self.valid_attack_tiles = []
        self.path = []

        self.calculate_valid_moves(tile)
        return True

    def select_modifier(self, tile: TileBase):
        self.deselect_all()
        self.selected_tile = tile
        self.selected_modifier = tile.modifier

    def select_city(self, tile: TileBase):
        self.deselect_all()
        self.selected_tile = tile
        self.selected_city = tile.city
        self.handle_selected_city()

    def handle_click(self, x: float, y: float):
        self.cost_tooltip = None
        tile = self.screen_to_tile(x, y)
        if not tile or not tile.visible_mapping[self.current_player.id]:
            self.deselect_all()
            return

        if self.selected_unit and tile in self.valid_move_tiles:
            self.move_unit(self.selected_tile, tile)
            return

        if self.selected_unit and tile in self.valid_attack_tiles:
            self.attack_unit(self.selected_tile, tile)
            return

        if tile == self.selected_tile:
            self.switch_selection_on_tile(tile)
            return

        # Clicked elsewhere → deselect
        if self.selected_tile and tile != self.selected_tile:
            self.deselect_all()

        self.primary_selection(tile)


    def handle_right_click(self, x, y):
        if not self.selected_tile:
            return
        if self.selected_modifier and self.selected_modifier.type != ModifierType.VILLAGE:
            if (
                self.selected_tile.owner is None
                or self.selected_tile.owner.owner != self.current_player
            ):
                return
            tile = self.screen_to_tile(x, y)
            if tile != self.selected_tile:
                return
            if not self.is_collectible(tile):
                return
            if self.current_player.stars < self.selected_modifier.cost:
                return
            
            # self.movement_system.random_move(tile)
            tile.add_population_to_city(self.selected_modifier.population)
            tile.modifier.collect()
            self.current_player.stars -= self.selected_modifier.cost
        elif self.selected_unit or self.selected_city or self.selected_modifier.type == ModifierType.VILLAGE:
            tile = self.screen_to_tile(x, y)
            if tile != self.selected_tile:
                return
            if not tile.unit or tile.unit.owner != self.current_player:
                return
            if not tile.city and not tile.modifier:
                return
            if tile.city and tile.city.owner == self.current_player:
                return
            if tile.modifier and tile.modifier.type != ModifierType.VILLAGE:
                return
            self.capture(tile)

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
        self.valid_attack_tiles = []
        self.move_popups.clear()
        self.cost_tooltip = None
        for btn in self.unit_btns:
            self.manager.remove(btn)
        self.unit_btns = []
        self.unit_cost_tooltips = []

    def on_key_press(self, key, modifiers):
        if key == arcade.key.ESCAPE:
            arcade.get_window().show_view(SettingsView(parent=self))

        if key == arcade.key.L:
            arcade.get_window().show_view(StatisticsView(parent=self, player_name=self.current_player.id + 1, turn=self.move_n, units_killed=self.current_player.kills))

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
        if c > 1 or (self.player_amount + self.bot_amount == 1 and c == 1):
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
        self.map = [[TileBase([]) for _ in range(self.size_map)] for _ in range(self.size_map)]
        c.execute('SELECT value FROM players')
        self.players = [eval(v) for (v,) in c.fetchall()]
        players_by_id = {p.id: p for p in self.players}

        city_tiles = []
        c.execute('SELECT x, y, value FROM map')
        for x, y, value in c.fetchall():
            tile: TileBase = eval(value)
            tile.row = x
            tile.col = y

            if tile.unit:
                tile.unit.owner = players_by_id[tile.unit.owner.id]
                tile.unit.__post_init__()

            if tile.city:
                tile.city.owner = players_by_id[tile.city.owner.id]
                tile.city.__post_init__()
                city_tiles.append(tile)

            if tile.owner:
                tile.owner.owner = players_by_id[tile.owner.owner.id]
                tile.owner.owner.__post_init__()

            self.map[x][y] = tile
        
        for tile in city_tiles:
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    self.map[tile.row + dx][tile.col + dy].owner = tile.city

        c.execute('SELECT key, value FROM game_state')
        game_state = {k: eval(v) for k, v in c.fetchall()}

        if "current_player" in game_state:
            self.current_player = players_by_id[game_state["current_player"]]

        if "move_n" in game_state:
            self.move_n = game_state["move_n"]

        conn.close()

        with open(DB_PATH, 'w'):
            pass
        init_db()

    def capture(self, tile: TileBase):
        player = self.current_player
        if not tile.unit or tile.unit.owner != player:
            return
        if tile.city:
            city_owner = tile.city.owner
            self.players[city_owner.id].cities.remove(tile.city)
            tile.city = City(player, tile.city.level, tile.city.population)
            tile.city.tile = tile

            self.check_defeat_of_player(city_owner)
        elif tile.modifier and tile.modifier.type == ModifierType.VILLAGE:
            tile.modifier = None
            tile.city = City(player)
            tile.city.tile = tile

        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                self.map[tile.row + dx][tile.col + dy].owner = tile.city
        tile.unit.move_remains = False

    def check_defeat_of_player(self, player: Player):
        if player.cities:
            return False
        
        player.is_alive = False
        for row in self.map:
            for tile in row:
                if tile.unit and tile.unit.owner == player:
                    tile.unit = None

        self.check_win()

    def handle_selected_city(self):
        if self.selected_city is None or self.selected_city.owner != self.current_player or self.selected_tile.unit is not None:
            return

        for btn in self.unit_btns:
            self.manager.remove(btn)
        self.unit_btns = []
        classes = []
        for unit in UNIT_TYPES.values():
            if unit.cost is None or not self.current_player.open_tech.tech_map.get(unit, True): continue
            classes.append(unit)
        for i, unit in enumerate(classes):
            btn = UITextureButton(texture=unit(self.current_player, (-1, -1)).texture.texture, scale=0.3, y=100, x=self.width / 2 - len(classes) / 2 * 100 + i * 100)
            self.unit_cost_tooltips.append(arcade.Text(str(unit.cost),y=230, x=self.width / 2 - len(classes) / 2 * 100 + i * 100 + 130, font_size=20, batch=self.batch, anchor_x='center', anchor_y='center'))
            def make_handler(unit: type[UnitBase]):
                return lambda _: self.create_unit(unit.cost, unit.type)
            btn.on_click = make_handler(unit)
            self.manager.add(btn)
            self.unit_btns.append(btn)
    
    def create_unit(self, cost: int, type: UnitType):
        if not cost or self.current_player.stars < cost:
            return
        self.selected_tile.unit = Unit(type, self.current_player, self.selected_tile.row, self.selected_tile.col)
        self.selected_tile.unit.move_remains = False
        self.current_player.stars -= cost
        self.deselect_all()
        self.update_sprites()