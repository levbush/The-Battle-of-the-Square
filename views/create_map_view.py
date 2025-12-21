import arcade
import arcade.color
from terrain.create_map import create_map


SCREEN_WIDTH, SCREEN_HEIGHT = arcade.window_commands.get_display_size()

class MapView(arcade.View):
    def __init__(self, size_map, bot_amount, player_amount, bot_difficulty):
        super().__init__()
        self.size_map = size_map
        self.player_amount = player_amount
        self.setup()
        arcade.set_background_color(arcade.color.SKY_BLUE)

    def setup(self):
        self.map = create_map(self.size_map, self.size_map, self.player_amount)
        spr_texture_land = arcade.load_texture("img\Terrain\Tiles\ground_1.png")
        spr_texture_mount = arcade.load_texture("img\Terrain\Mountains\mountain_1.png")
        spr_texture_water = arcade.load_texture("img\Terrain\Water\water.png")
        self.tiles = arcade.SpriteList()
        for row_idx, row in enumerate(self.map):
            for col_idx, tile_type in enumerate(row):
                screen_x = (col_idx - row_idx) * 150 + SCREEN_WIDTH // 2
                screen_y = (col_idx + row_idx) * 90 + 150
                if tile_type.type == 0:
                    spr = arcade.Sprite(spr_texture_land, scale=0.3, center_x=screen_x, center_y=screen_y)
                if tile_type.type == 1:
                    spr = arcade.Sprite(spr_texture_water, scale=0.3, center_x=screen_x, center_y=screen_y)
                if tile_type.type == 2:
                    spr = arcade.Sprite(spr_texture_mount, scale=0.3, center_x=screen_x, center_y=screen_y)
                    self.tiles.append(spr)
                    spr = arcade.Sprite(spr_texture_land, scale=0.3, center_x=screen_x, center_y=screen_y)
                self.tiles.append(spr)
        self.tiles.reverse()

    def on_draw(self):
        self.clear()
        self.tiles.draw()

    def on_update(self, delta_time):
        pass

