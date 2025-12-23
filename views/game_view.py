import arcade
import arcade.color
from terrain.create_map import create_map
from classes import Player
from random import shuffle

# from pprint import pprint
from terrain.terrain_classes import *


SCREEN_WIDTH, SCREEN_HEIGHT = arcade.window_commands.get_display_size()


class GameView(arcade.View):
    def __init__(self, size_map, bot_amount, player_amount, bot_difficulty):
        super().__init__()
        self.size_map = size_map
        self.player_amount = player_amount
        self.bot_amount = bot_amount
        self.bot_difficulty = bot_difficulty
        self.move = False
        self.move_start = (0, 0)
        self.camera_start = (0, 0)
        self.world_camera = arcade.camera.Camera2D()
        self.gui_camera = arcade.camera.Camera2D()
        arcade.set_background_color(arcade.color.SKY_BLUE)
        self.setup()

    def setup(self):
        self.players = []
        for i in range(self.player_amount - 1):
            self.players.append(Player(None, False))
        for i in range(self.bot_amount):
            self.players.append(Player(None, True))
        shuffle(self.players)
        self.players.insert(0, Player(None, False))
        for i in range(self.player_amount + self.bot_amount):
            self.players[i].id = i
        self.current_player = 0

        self.spr_texture_fog = arcade.load_texture(r"assets/Terrain/fog.png")
        self.bot_city_textures = [arcade.load_texture(rf'assets/Cities/bot/House_{i}.png') for i in range(6)]
        self.player_city_textures = [arcade.load_texture(rf'assets/Cities/player/House_{i}.png') for i in range(6)]
        self.city_textures = {True: self.bot_city_textures, False: self.player_city_textures}
        self.sprite_offsets = {}

        self.create_map()

    def create_map(self):
        self.map = create_map(self.size_map, self.players)
        # pprint(self.map)

        self.tiles = arcade.SpriteList()
        self.modifiers = arcade.SpriteList()
        self.cities = arcade.SpriteList()

        for row_idx, row in enumerate(self.map):
            for col_idx, tile in enumerate(row):
                screen_x = (col_idx - row_idx) * 150 + SCREEN_WIDTH // 2
                screen_y = (col_idx + row_idx) * 90 + 150
                if not tile.visible_mapping[self.current_player]:
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
        self.tiles.reverse()
        self.modifiers.reverse()
        self.cities.reverse()

    def on_draw(self):
        self.clear()
        self.world_camera.use()
        self.tiles.draw()
        self.modifiers.draw()
        self.cities.draw()
        self.gui_camera.use()

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

    def on_update(self, delta_time):
        pass
