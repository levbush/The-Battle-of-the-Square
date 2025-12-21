import arcade
import arcade.color
from terrain.create_map import create_map


SCREEN_WIDTH, SCREEN_HEIGHT = arcade.window_commands.get_display_size()

class MapView(arcade.View):
    def __init__(self, size_map, bot_amount, player_amount, bot_difficulty):
        super().__init__()
        self.size_map = size_map
        self.player_amount = player_amount
        self.move = False
        self.move_start = (0, 0)
        self.camera_start = (0, 0)
        self.world_camera = arcade.camera.Camera2D()
        self.gui_camera = arcade.camera.Camera2D()
        arcade.set_background_color(arcade.color.SKY_BLUE)
        self.setup()

    def setup(self):
        self.map = create_map(self.size_map, self.size_map, self.player_amount)
        spr_texture_land = arcade.load_texture("assets\img\Terrain\Tiles\ground_1.png")
        spr_texture_mount = arcade.load_texture("assets\img\Terrain\Mountains\mountain_1.png")
        spr_texture_water = arcade.load_texture("assets\img\Terrain\Water\water.png")
        self.tiles = arcade.SpriteList()
        
        for row_idx, row in enumerate(self.map):
            for col_idx, tile_type in enumerate(row):
                screen_x = (col_idx - row_idx) * 150 + SCREEN_WIDTH // 2
                screen_y = (col_idx + row_idx) * 90 + 150
                
                if tile_type.type == 0:
                    spr = arcade.Sprite(spr_texture_land, scale=0.3, center_x=screen_x, center_y=screen_y)
                    self.tiles.append(spr)
                if tile_type.type == 1:
                    spr = arcade.Sprite(spr_texture_water, scale=0.3, center_x=screen_x, center_y=screen_y)
                    self.tiles.append(spr)
                if tile_type.type == 2:
                    land_spr = arcade.Sprite(spr_texture_land, scale=0.3, center_x=screen_x, center_y=screen_y)
                    mount_spr = arcade.Sprite(spr_texture_mount, scale=0.3, center_x=screen_x, center_y=screen_y)
                    self.tiles.append(mount_spr)
                    self.tiles.append(land_spr)
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
