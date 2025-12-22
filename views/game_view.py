import arcade
import arcade.color
from terrain.create_map import create_map
from terrain.terrain_classes import Land, Water
from classes import Player
from random import shuffle
from pprint import pprint



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
        
        self.spr_texture_land = arcade.load_texture(r"assets\Terrain\ground.png")
        self.spr_texture_mount = arcade.load_texture(r"assets\Terrain\mountain.png")
        self.spr_texture_water = arcade.load_texture(r"assets\Terrain\water.png")
        self.spr_texture_fruit = arcade.load_texture(r"assets\Resources\fruits.png")
        self.spr_texture_animal = arcade.load_texture(r"assets\Resources\animal.png")
        self.spr_texture_forest = arcade.load_texture(r"assets\Terrain\forest.png")
        self.spr_texture_fog = arcade.load_texture(r"assets\Terrain\fog.png")
        self.bot_city_textures = [arcade.load_texture(rf'assets\Cities\bot\House_{i}.png') for i in range(6)]
        self.player_city_textures = [arcade.load_texture(rf'assets\Cities\player\House_{i}.png') for i in range(6)]
        self.spr_texture_gold = arcade.load_texture(r"assets\Resources\gold.png")
        self.spr_texture_fish = arcade.load_texture(r"assets\Resources\fish.png")
        self.spr_texture_n_village = arcade.load_texture(r"assets\Resources\n_village.png")
        
        self.create_map()

    def create_map(self):
        self.map = create_map(self.size_map, self.players)
        # pprint(self.map)
        
        self.tiles = arcade.SpriteList()
        
        for row_idx, row in enumerate(self.map):
            for col_idx, tile in enumerate(row):
                screen_x = (col_idx - row_idx) * 150 + SCREEN_WIDTH // 2
                screen_y = (col_idx + row_idx) * 90 + 150
                # if not tile.visible_mapping[self.current_player]:
                #     self.tiles.append(arcade.Sprite(self.spr_texture_fog, 0.3, screen_x, screen_y))
                #     continue
                if tile.type == 0:
                    tile: Land
                    match tile.modifier:
                        case 'fruits':
                            self.tiles.append(arcade.Sprite(self.spr_texture_fruit, 0.2, screen_x, screen_y + 60))
                        case 'animal':
                            self.tiles.append(arcade.Sprite(self.spr_texture_animal, 0.1, screen_x, screen_y + 80))
                        case "forest":
                            self.tiles.append(arcade.Sprite(self.spr_texture_forest, 0.3, screen_x, screen_y + 80))
                        case "n_village":
                            self.tiles.append(arcade.Sprite(self.spr_texture_n_village, 0.3, screen_x, screen_y + 80))
                        case 'mountain':
                            if tile.gold:
                                gold_spr = arcade.Sprite(self.spr_texture_gold, scale=0.2, center_x=screen_x, center_y=screen_y + 75)
                                self.tiles.append(gold_spr)
                            mount_spr = arcade.Sprite(self.spr_texture_mount, scale=0.3, center_x=screen_x, center_y=screen_y + 50)
                            self.tiles.append(mount_spr)
                    if tile.city:
                        if tile.city.owner.is_bot:
                            self.tiles.append(arcade.Sprite(self.bot_city_textures[tile.city.level], 0.5, screen_x, screen_y + 120))
                        else:
                            self.tiles.append(arcade.Sprite(self.player_city_textures[tile.city.level], 0.5, screen_x, screen_y + 120))
                    spr = arcade.Sprite(self.spr_texture_land, scale=0.3, center_x=screen_x, center_y=screen_y)
                    self.tiles.append(spr)

                if tile.type == 1:
                    tile: Water
                    match tile.modifier:
                        case 'fish':
                            self.tiles.append(arcade.Sprite(self.spr_texture_fish, 0.2, screen_x, screen_y + 60))
                    spr = arcade.Sprite(self.spr_texture_water, scale=0.3, center_x=screen_x, center_y=screen_y)
                    self.tiles.append(spr)                    
        self.tiles.reverse()
    
    def on_draw(self):
        self.clear()
        self.world_camera.use()
        self.tiles.draw()
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
            
            self.world_camera.position = (
                self.camera_start[0] - dx,
                self.camera_start[1] - dy
            )

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
            self.world_camera.position[1] - (mouse_world_y_after - mouse_world_y_before)
        )

    def on_update(self, delta_time):
        pass
