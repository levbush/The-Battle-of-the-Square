import arcade
import arcade.color
from arcade.gui import UIManager, UITextureButton
from views.next_turn_view import NextTurnView
from terrain.create_map import create_map
from classes import Player
from random import shuffle
from terrain.terrain_classes import *
from pyglet.graphics import Batch
import math


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

        self.world_camera = arcade.camera.Camera2D()
        self.gui_camera = arcade.camera.Camera2D()
        self.manager = UIManager()
        self.manager.enable()
        self.setup()

    def setup(self):
        if self.new_game:
            self.players = []
            for i in range(self.player_amount - 1):
                self.players.append(Player(None, False))
            for i in range(self.bot_amount):
                self.players.append(Player(None, True))
            shuffle(self.players)
            self.players.insert(0, Player(None, False))
            for i in range(self.player_amount + self.bot_amount):
                self.players[i].id = i
            self.current_player: Player | None = None
            
            self.tiles = arcade.SpriteList(use_spatial_hash=True)
            self.modifiers = arcade.SpriteList(use_spatial_hash=True)
            self.cities = arcade.SpriteList(use_spatial_hash=True)
            self.units = arcade.SpriteList(use_spatial_hash=True)
            self.move_popups = arcade.SpriteList()
            self.city_tooltips = []
            self.map = create_map(self.size_map, self.players)
  
            btn_normal = arcade.load_texture("assets/misc/next_turn.png")
            self.next_turn_btn = UITextureButton(
                x=self.width // 2 + self.width * 0.05,
                y=self.height * 0.05,
                texture=btn_normal,
                scale=2)
            self.manager.add(self.next_turn_btn)
            self.next_turn_btn.on_click = lambda *_: self.change_POV()
            self.move_n = 0

        self.spr_texture_fog = arcade.load_texture("assets/terrain/fog.png")
        self.bot_city_textures = [arcade.load_texture(f'assets/cities/bot/House_{i}.png') for i in range(6)]
        self.player_city_textures = [arcade.load_texture(f'assets/cities/player/House_{i}.png') for i in range(6)]
        self.enemy_city_textures = [arcade.load_texture(f'assets/cities/enemy/House_{i}.png') for i in range(6)]
        self.city_textures = {'bot': self.bot_city_textures, 'ally': self.player_city_textures, 'enemy': self.enemy_city_textures}
        self.resource = arcade.load_texture('assets/misc/resource.png')
        self.move_tooltip = arcade.load_texture('assets/misc/moveTarget.png')
        self.attack_tooltip = arcade.load_texture('assets/misc/attackTarget.png')
        self.batch = Batch()
        self.world_batch = Batch()
        self.star_label = arcade.Text('', self.width / 2 - 50, self.height - 30, font_size=20, color=arcade.color.BLACK, anchor_y='center', batch=self.batch)
        self.move_label = arcade.Text('', self.width / 2 - 250, self.height - 30, font_size=20, color=arcade.color.BLACK, anchor_y='center', batch=self.batch)

    def on_show_view(self):
        self.manager.enable()
        if self.current_player is None:
            self.change_POV()

    def change_POV(self):
        self.world_camera.position = self.camera_start
        self.world_camera.zoom = 0.5**(((121, 196, 256, 324, 400, 900).index(self.size_map ** 2) + 1) / 2)
        if self.current_player is None:
            self.current_player = self.players[0]
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

        # self.tiles.clear()
        # self.modifiers.clear()
        # self.cities.clear()
        # self.units.clear()

        # for row_idx, row in enumerate(self.map):
        #     for col_idx, tile in enumerate(row):
        #         screen_x = (col_idx - row_idx) * 150 + SCREEN_WIDTH // 2
        #         screen_y = (col_idx + row_idx) * 90 + 150
        #         if not tile.visible_mapping[self.current_player.id]:
        #             self.tiles.append(arcade.Sprite(self.spr_texture_fog, 0.3, screen_x, screen_y))
        #             continue
        #         self.tiles.append(arcade.Sprite(tile.texture.texture, 0.3, screen_x, screen_y))
        #         if tile.modifier:
        #             for i in range(len(tile.modifier.textures)):
        #                 self.modifiers.append(
        #                     arcade.Sprite(
        #                         tile.modifier.textures[i].texture,
        #                         tile.modifier.scales[i],
        #                         screen_x,
        #                         screen_y + tile.modifier.offsets[i],
        #                     )
        #                 )
        #         elif tile.city:
        #             if tile.city.owner.is_bot:
        #                 texture = 'bot'
        #             elif tile.city.owner == self.current_player:
        #                 texture = 'ally'
        #             else:
        #                 texture = 'enemy'
        #             self.cities.append(
        #                 arcade.Sprite(
        #                     self.city_textures[texture][tile.city.level], 0.5, screen_x, screen_y + 150
        #                 )
        #             )
        #         if tile.unit:
        #             if tile.unit.owner == self.current_player:
        #                 texture = tile.unit.textures.ally
        #             elif tile.unit.owner.is_bot:
        #                 texture = tile.unit.textures.bot
        #             else:
        #                 texture = tile.unit.textures.enemy
        #             self.units.append(arcade.Sprite(texture, 0.5, center_x=screen_x + 10, center_y=screen_y + 90))
                        
        # self.tiles.reverse()
        # self.modifiers.reverse()
        # self.cities.reverse()
        # self.units.reverse()
        self.update_sprites()

        self.manager.disable()
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
        self.world_batch.draw()
        self.draw_valid_moves()
        self.draw_path()
        self.draw_unit_hp()
        self.gui_camera.use()
        self.manager.draw()
        arcade.draw_texture_rect(self.resource, arcade.rect.LBWH(self.width / 2 - 120, self.height - 50, 40, 40))
        self.batch.draw()

    def draw_unit_hp(self):
        for row_idx, row in enumerate(self.map):
            for col_idx, tile in enumerate(row):
                if tile.unit and tile.visible_mapping[self.current_player.id] and tile.unit.is_alive:
                    screen_x = (col_idx - row_idx) * 150 + self.width // 2
                    screen_y = (col_idx + row_idx) * 90 + 150
                    
                    hp_text = f"{tile.unit.health}"
                    hp_x = screen_x - 50
                    hp_y = screen_y + 130
                    
                    arcade.draw_text(
                        hp_text,
                        hp_x,
                        hp_y,
                        arcade.color.WHITE,
                        30,
                        anchor_x="center",
                        anchor_y="center",
                        bold=True
                    )

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
            self.world_camera.position = (
                self.camera_start[0] - dx,
                self.camera_start[1] - dy
            )

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
                center_x=x + 10,
                center_y=y + 90,
                radius=40,
                color=arcade.color.YELLOW,
                border_width=4,
            )

        if self.selected_modifier or self.selected_city:
            width = 120
            height = 80
            left = x - width / 2
            right = x + width / 2
            bottom = y + 70 + bool(self.selected_city) * 20 - height / 2
            top = y + 70 + bool(self.selected_city) * 20 + height / 2
            
            arcade.draw_lrbt_rectangle_outline(
                left=left,
                right=right,
                bottom=bottom,
                top=top,
                color=arcade.color.BLEU_DE_FRANCE,
                border_width=4,
            )
            if self.selected_modifier and self.selected_modifier.cost is not None and self.selected_tile.owner is not None and self.selected_tile.owner.owner == self.current_player and self.selected_tile.modifier and not self.selected_tile.modifier.is_collected:
                self.cost_tooltip = arcade.Text(str(self.selected_modifier.cost), right, top, arcade.color.BLACK, anchor_x='center', anchor_y='center', batch=self.world_batch, font_size=24)

    def draw_valid_moves(self):
        self.move_popups.clear()
        for tile in self.valid_move_tiles:
            x, y = self.tile_to_world(tile)
            
            self.move_popups.append(arcade.Sprite(self.move_tooltip if not tile.unit else self.attack_tooltip, 0.5, x, y + 60))
        self.move_popups.draw()

    def draw_path(self):
        if len(self.path) < 2:
            return
        
        for i in range(len(self.path) - 1):
            start_x, start_y = self.tile_to_world(self.path[i])
            end_x, end_y = self.tile_to_world(self.path[i + 1])
            
            start_x += 10
            start_y += 90
            end_x += 10
            end_y += 90
            
            arcade.draw_line(
                start_x, start_y,
                end_x, end_y,
                color=arcade.color.BLUE,
                line_width=3
            )
            
            angle = math.atan2(end_y - start_y, end_x - start_x)
            arrow_length = 20
            arrow_angle = math.pi / 6
            
            left_x = end_x - arrow_length * math.cos(angle - arrow_angle)
            left_y = end_y - arrow_length * math.sin(angle - arrow_angle)
            
            right_x = end_x - arrow_length * math.cos(angle + arrow_angle)
            right_y = end_y - arrow_length * math.sin(angle + arrow_angle)
            
            arcade.draw_triangle_outline(
                end_x, end_y,
                left_x, left_y,
                right_x, right_y,
                color=arcade.color.BLUE,
                border_width=2
            )

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
        
        directions = [
            (-1, -1),
            (-1, 0),
            (-1, 1),
            (0, -1),
            (0, 1),
            (1, -1),
            (1, 0),
            (1, 1),
        ]
        
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
                
                if (0 <= new_row < len(self.map) and 
                    0 <= new_col < len(self.map[new_row]) and
                    max(abs(dr), abs(dc)) <= radius):
                    
                    tile = self.map[new_row][new_col]
                    tiles_in_range.append(tile)
        
        return tiles_in_range

    def update_visibility_around_unit(self, unit_tile: TileBase):
        player_id = self.current_player.id
        
        visible_tiles = self.get_tiles_in_range(unit_tile, 1)
        
        for tile in visible_tiles:
            tile.visible_mapping[player_id] = True

    def is_passable(self, tile: TileBase) -> bool:
        return isinstance(tile, Land)

    def calculate_valid_moves(self, start_tile: TileBase):
        self.valid_move_tiles = []
        self.path = []
        
        if not start_tile or not start_tile.unit:
            return
        
        # print(f"Calculating moves for unit at ({start_tile.row}, {start_tile.col})")
        # print(f"Unit movement: {start_tile.unit.movement}")
        # print(f"Tile type: {type(start_tile).__name__}")
        
        movement_range = start_tile.unit.movement
        
        visited = []
        queue = [(start_tile, 0, [])]
        
        while queue:
            current_tile, distance, path = queue.pop(0)
            
            if current_tile in visited:
                continue
                
            visited.append(current_tile)
            
            if current_tile != start_tile:
                can_move = False
                
                if not self.is_passable(current_tile):
                    # print(f"  Tile at ({current_tile.row}, {current_tile.col}) is not passable (type: {type(current_tile).__name__})")
                    continue
                
                if current_tile.unit is None:
                    can_move = True
                elif current_tile.unit.owner != self.current_player:
                    can_move = True
                
                if can_move and distance <= movement_range:
                    self.valid_move_tiles.append(current_tile)
                    # print(f"  Valid move to ({current_tile.row}, {current_tile.col}) at distance {distance} (type: {type(current_tile).__name__})")
            
            if distance >= movement_range:
                continue
            
            for neighbor in self.get_neighbors(current_tile):
                if neighbor not in visited and self.is_passable(neighbor):
                    new_path = path + [current_tile]
                    queue.append((neighbor, distance + 1, new_path))
                elif neighbor in visited:
                    # print(f"  Neighbor at ({neighbor.row}, {neighbor.col}) already visited")
                    ...
                else:
                    ...
                    # print(f"  Neighbor at ({neighbor.row}, {neighbor.col}) not passable (type: {type(neighbor).__name__})")
        
        # print(f"Found {len(self.valid_move_tiles)} valid moves")
        # print(f"Expected up to: {(movement_range * 2 + 1)**2 - 1} cells (theoretical maximum)")
        for tile in self.valid_move_tiles:
            # print(f"  - ({tile.row}, {tile.col}) - type: {type(tile).__name__}")
            ...

    def move_unit(self, from_tile: TileBase, to_tile: TileBase):
        if not from_tile.unit or from_tile.unit.owner != self.current_player:
            # print("No unit to move or wrong owner")
            return False
        
        # print(f"Attempting to move unit from ({from_tile.row}, {from_tile.col}) to ({to_tile.row}, {to_tile.col})")
        # print(f"Unit type: {type(from_tile.unit).__name__}")
        # print(f"Unit movement remains: {from_tile.unit.move_remains}")
        # print(f"From tile type: {type(from_tile).__name__}")
        # print(f"To tile type: {type(to_tile).__name__}")
        
        if not self.is_passable(to_tile):
            # print(f"Cannot move to tile - not passable (type: {type(to_tile).__name__})")
            return False
        
        if not from_tile.unit.move_remains:
            # print("Unit has no movement left")
            return False
        
        if to_tile not in self.valid_move_tiles:
            # print("Target tile not in valid moves")
            return False
        
        try:
            distance = max(abs(to_tile.row - from_tile.row), abs(to_tile.col - from_tile.col))
            # print(f"Distance to move: {distance}")
            
            if to_tile.unit:
                if to_tile.unit.owner != self.current_player:
                    # print(f"Attacking enemy unit at ({to_tile.row}, {to_tile.col})")
                    UnitBase.attack_unit(from_tile.unit, to_tile.unit)
                    
                    if not to_tile.unit.is_alive:
                        # print(f"Enemy defeated, moving to tile")
                        from_tile.unit.move((to_tile.row, to_tile.col))
                        from_tile.unit.move_remains = False
                        
                        self.update_visibility_around_unit(to_tile)
                        
                        to_tile.unit = from_tile.unit
                        from_tile.unit = None
                    else:
                        from_tile.unit.move_remains = False
                        # print(f"Attack completed but enemy still alive")
                else:
                    # print("Cannot attack ally")
                    return False
            else:
                # print(f"Moving to empty tile")
                from_tile.unit.move((to_tile.row, to_tile.col))
                from_tile.unit.move_remains = False
                
                self.update_visibility_around_unit(to_tile)
                
                to_tile.unit = from_tile.unit
                from_tile.unit = None
            
            self.update_sprites()
            
            self.selected_unit = None
            self.selected_tile = None
            self.valid_move_tiles = []
            self.path = []
            
            # print("Move completed successfully")
            return True
            
        except Exception as e:
            # print(f"Error during move: {e}")
            import traceback
            traceback.print_exc()
            return False

    def update_sprites(self):
        # print("Updating sprites...")
        self.tiles.clear()
        self.modifiers.clear()
        self.cities.clear()
        self.units.clear()
        self.city_tooltips.clear()
        self.deselect_all()
        
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
                        arcade.Sprite(
                            self.city_textures[texture][tile.city.level], 0.5, screen_x, screen_y + 150
                        )
                    )
                    self.city_tooltips.append(arcade.Text(f'{tile.city.population}/{tile.city.level + 2}', screen_x + 50, screen_y + 140, arcade.color.BLACK, batch=self.world_batch, anchor_x='center', anchor_y='center', font_size=24))
                
                if tile.unit:
                    if tile.unit.owner == self.current_player:
                        texture = tile.unit.textures.ally
                    elif tile.unit.owner.is_bot:
                        texture = tile.unit.textures.bot
                    else:
                        texture = tile.unit.textures.enemy
                    self.units.append(arcade.Sprite(texture, 0.5, center_x=screen_x + 10, center_y=screen_y + 90))
                    # print(f"  Unit sprite at ({row_idx}, {col_idx}) - {type(tile.unit).__name__}")
        
        self.tiles.reverse()
        self.modifiers.reverse()
        self.cities.reverse()
        self.units.reverse()
        # print(f"Total unit sprites: {len(self.units)}")

    def make_bot_move(self):
        if not self.current_player.is_bot or not self.current_player.is_alive:
            return
        # TODO: Реализовать логику хода бота
        pass

    def get_stars_for_player(self):
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
                    # print(f"Reset movement and updated visibility for unit at ({tile.row}, {tile.col})")
        
        self.update_sprites()

    def select_unit(self, tile: TileBase):
        if tile.unit and not tile.unit.move_remains:
            # print(f"Cannot select unit - no movement left")
            return False
            
        self.selected_unit = tile.unit
        self.selected_tile = tile
        self.valid_move_tiles = []
        self.path = []
        
        self.calculate_valid_moves(tile)
        # print(f"Unit selected at ({tile.row}, {tile.col}) - {type(tile.unit).__name__}")
        return True

    def select_modifier(self, tile: TileBase):
        self.selected_tile = tile
        self.selected_modifier = tile.modifier
        self.valid_move_tiles = []
        self.path = []
        # print("Modifier selected", repr(tile.modifier))

    def select_city(self, tile: TileBase):
        self.selected_tile = tile
        self.selected_city = tile.city
        self.valid_move_tiles = []
        self.path = []
        # print("City selected", repr(tile.city))

    def handle_click(self, x, y):
        self.cost_tooltip = None
        tile = self.screen_to_tile(x, y)
        print(repr(tile))
        if not tile:
            # print("No tile at clicked position")
            self.deselect_all()
            return
            
        if not tile.visible_mapping[self.current_player.id]:
            # print("Tile not visible")
            self.deselect_all()
            return

        # print(f"Clicked tile at ({tile.row}, {tile.col})")
        # print(f"  Tile type: {type(tile).__name__}")
        # print(f"  Has unit: {bool(tile.unit)}")
        if tile.unit:
            # print(f"  Unit owner: {tile.unit.owner}")
            # print(f"  Unit movement remains: {tile.unit.move_remains}")
            ...
        # print(f"  Has city: {bool(tile.city)}")
        # print(f"  Has modifier: {bool(tile.modifier)}")

        if self.selected_unit and tile in self.valid_move_tiles:
            # print(f"Attempting to move to valid tile ({tile.row}, {tile.col})")
            success = self.move_unit(self.selected_tile, tile)
            if success:
                # print(f"Юнит перемещен с ({self.selected_tile.row}, {self.selected_tile.col}) на ({tile.row}, {tile.col})")
                ...
            else:
                # print("Move failed")
                ...
            return

        if tile == self.selected_tile:
            # print("Same tile clicked - switching selection")
            self.switch_selection_on_tile(tile)
            return

        if self.selected_tile and tile != self.selected_tile:
            # print("Deselecting all (different tile)")
            self.deselect_all()

        self.primary_selection(tile)

    def handle_right_click(self, x, y):
        if not self.selected_tile or self.selected_tile.owner is None or self.selected_tile.owner.owner != self.current_player or not self.selected_modifier:
            return
        if self.selected_modifier.cost is None:
            return
        tile = self.screen_to_tile(x, y)
        if tile != self.selected_tile or tile.modifier.is_collected:
            return
        if self.current_player.stars < self.selected_modifier.cost:
            return
        tile.add_population_to_city(self.selected_modifier.population)
        tile.modifier.collect()
        self.current_player.stars -= self.selected_modifier.cost
        self.star_label.text = f'{self.current_player.stars} (+ {self.get_stars_for_player()})'
        self.update_sprites()

    def switch_selection_on_tile(self, tile: TileBase):
        if self.selected_unit:
            if tile.modifier:
                # # print("Switching from unit to modifier")
                self.deselect_all()
                self.select_modifier(tile)
            elif tile.city:
                # # print("Switching from unit to city")
                self.deselect_all()
                self.select_city(tile)
            else:
                # print("Deselecting unit")
                self.deselect_all()
        
        elif self.selected_modifier:
            if tile.unit and tile.unit.owner == self.current_player:
                # print("Switching from modifier to unit")
                self.deselect_all()
                self.select_unit(tile)
            elif tile.city:
                # print("Switching from modifier to city")
                self.deselect_all()
                self.select_city(tile)
            else:
                # print("Deselecting modifier")
                self.deselect_all()
        
        elif self.selected_city:
            if tile.unit and tile.unit.owner == self.current_player:
                # print("Switching from city to unit")
                self.deselect_all()
                self.select_unit(tile)
            elif tile.modifier:
                # print("Switching from city to modifier")
                self.deselect_all()
                self.select_modifier(tile)
            else:
                # print("Deselecting city")
                self.deselect_all()
        
        else:
            self.primary_selection(tile)

    def primary_selection(self, tile: TileBase):
        if tile.unit:
            if tile.unit.owner == self.current_player:
                # print("Selecting unit")
                if self.select_unit(tile):
                    return
            else:
                # print("Cannot select enemy unit and nothing under it")
                self.deselect_all()
        if tile.city:
            # print("Selecting city")
            self.select_city(tile)
        elif tile.modifier:
            # print("Selecting modifier")
            self.select_modifier(tile)
        else:
            # print("Empty tile clicked")
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
        # print("All selections cleared")