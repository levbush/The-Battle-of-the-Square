import arcade
import arcade.color
from arcade.gui import UIManager, UITextureButton
from views.next_turn_view import NextTurnView
from terrain.create_map import create_map
from classes import Player
from random import shuffle
from terrain.terrain_classes import *
from pyglet.graphics import Batch


SCREEN_WIDTH, SCREEN_HEIGHT = arcade.window_commands.get_display_size()


class GameView(arcade.View):
    def __init__(self, size_map, bot_amount, player_amount, bot_difficulty, new_game=True):
        super().__init__(background_color=arcade.color.SKY_BLUE)
        self.size_map = size_map
        self.player_amount = player_amount
        self.bot_amount = bot_amount
        self.bot_difficulty = bot_difficulty
        self.move = False
        self.move_start = (0, 0)
        self.camera_start = (250 * self.size_map / 4, 250 * self.size_map *(1 / 2 - 1 / 6))
        self.new_game = new_game
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
            
            self.tiles = arcade.SpriteList()
            self.modifiers = arcade.SpriteList()
            self.cities = arcade.SpriteList()
            self.units = arcade.SpriteList()
            self.map = create_map(self.size_map, self.players)

            btn_normal = arcade.load_texture("assets/next_turn.png")
            self.next_turn_btn = UITextureButton(
                x=SCREEN_WIDTH // 2 + SCREEN_WIDTH * 0.05,
                y=SCREEN_HEIGHT * 0.05,
                texture=btn_normal,
                scale=2)
            self.manager.add(self.next_turn_btn)
            self.next_turn_btn.on_click = lambda *_: self.change_POV()
            self.move_n = 0

        self.spr_texture_fog = arcade.load_texture("assets/terrain/fog.png")
        self.bot_city_textures = [arcade.load_texture(f'assets/cities/bot/House_{i}.png') for i in range(6)]
        self.player_city_textures = [arcade.load_texture(f'assets/cities/player/House_{i}.png') for i in range(6)]
        self.city_textures = {True: self.bot_city_textures, False: self.player_city_textures}
        self.resource = arcade.load_texture('assets/resource.png')
        self.batch = Batch()
        self.star_label = arcade.Text('', SCREEN_WIDTH / 2 - 50, SCREEN_HEIGHT - 30, font_size=20, color=arcade.color.BLACK, anchor_y='center', batch=self.batch)
        self.move_label = arcade.Text('', SCREEN_WIDTH / 2 - 250, SCREEN_HEIGHT - 30, font_size=20, color=arcade.color.BLACK, anchor_y='center', batch=self.batch)

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
        

        self.tiles.clear()
        self.modifiers.clear()
        self.cities.clear()
        self.units.clear()

        for row_idx, row in enumerate(self.map):
            for col_idx, tile in enumerate(row):
                screen_x = (col_idx - row_idx) * 150 + SCREEN_WIDTH // 2
                screen_y = (col_idx + row_idx) * 90 + 150
                if not tile.visible_mapping[self.current_player.id]:
                    self.tiles.append(arcade.Sprite(self.spr_texture_fog, 0.3, screen_x, screen_y))
                    continue
                self.tiles.append(arcade.Sprite(tile.texture, 0.3, screen_x, screen_y))
                if tile.modifier:
                    for i in range(len(tile.modifier.textures)):
                        self.modifiers.append(
                            arcade.Sprite(
                                tile.modifier.textures[i],
                                tile.modifier.scales[i],
                                screen_x,
                                screen_y + tile.modifier.offsets[i],
                            )
                        )
                elif tile.city:
                    self.cities.append(
                        arcade.Sprite(
                            self.city_textures[tile.city.owner.is_bot][tile.city.level], 0.5, screen_x, screen_y + 150
                        )
                    )
                if tile.unit:
                    if tile.unit.owner == self.current_player:
                        texture = tile.unit.textures.ally
                    elif tile.unit.owner.is_bot:
                        texture = tile.unit.textures.bot
                    else:
                        texture = tile.unit.textures.enemy
                    self.units.append(arcade.Sprite(texture, 0.5, center_x=screen_x, center_y=screen_y + 80))

                        
        self.tiles.reverse()
        self.modifiers.reverse()
        self.cities.reverse()
        self.units.reverse()

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
        self.gui_camera.use()
        self.manager.draw()
        arcade.draw_texture_rect(self.resource, arcade.rect.LBWH(SCREEN_WIDTH / 2 - 120, SCREEN_HEIGHT - 50, 40, 40))
        self.batch.draw()

    def on_mouse_press(self, x, y, button, modifiers):
        if button == arcade.MOUSE_BUTTON_LEFT:
            self.move = True
            self.move_start = (x, y)
            self.camera_start = (self.world_camera.position[0], self.world_camera.position[1])

    def on_mouse_motion(self, x, y, dx, dy):
        if self.move:
            dx = x - self.move_start[0]
            dy = y - self.move_start[1]

            self.world_camera.position = (self.camera_start[0] - dx, self.camera_start[1] - dy)

    def on_mouse_release(self, x, y, button, modifiers):
        if button == arcade.MOUSE_BUTTON_LEFT:
            self.move = False

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
        zoom_point_y = y - 150

        mouse_world_x_before = self.world_camera.position[0] + (zoom_point_x - self.window.width / 2) / current_zoom
        mouse_world_y_before = self.world_camera.position[1] + (zoom_point_y - self.window.height / 2) / current_zoom

        self.world_camera.zoom = new_zoom

        mouse_world_x_after = self.world_camera.position[0] + (zoom_point_x - self.window.width / 2) / new_zoom
        mouse_world_y_after = self.world_camera.position[1] + (zoom_point_y - self.window.height / 2) / new_zoom

        self.world_camera.position = (
            self.world_camera.position[0] - (mouse_world_x_after - mouse_world_x_before),
            self.world_camera.position[1] - (mouse_world_y_after - mouse_world_y_before),
        )

    def make_bot_move(self):
        if not self.current_player.is_bot or not self.current_player.is_alive:
            return
    
    def get_stars_for_player(self):
        return sum((city.level + 1) for city in self.current_player.cities) + 1 if self.move_n else 0

    def make_player_move(self):
        stars = self.get_stars_for_player()
        self.current_player.stars += stars
        self.star_label.text = str(self.current_player.stars) + (f" (+ {stars})" if stars else '')
        self.move_label.text = f'Ход {self.move_n}'