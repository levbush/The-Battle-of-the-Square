import arcade
from pyglet.graphics import Batch

class SettingsView(arcade.View):
    def __init__(self, music_volume=50, sfx_volume=70):
        super().__init__()
        
        self.music_volume = music_volume
        self.sfx_volume = sfx_volume
        self.current_selection = 0
        
        self.slider_width = 300
        self.slider_height = 20
        self.music_slider_y = 400
        self.sfx_slider_y = 300
        
        self.dragging_music = False
        self.dragging_sfx = False
        
        self.background_color = arcade.color.DARK_BLUE_GRAY
        
        self.batch = Batch()
        self.title = arcade.Text("НАСТРОЙКИ", 400, 650,
                               arcade.color.GOLD, 54, anchor_x="center",
                               batch=self.batch)
        
        self.music_text = arcade.Text(f"Громкость музыки: {self.music_volume}%", 
                                    250, 450, arcade.color.LIGHT_GRAY, 28,
                                    batch=self.batch)
        
        self.sfx_text = arcade.Text(f"Громкость звуков: {self.sfx_volume}%", 
                                  250, 350, arcade.color.LIGHT_GRAY, 28,
                                  batch=self.batch)
        
        self.exit_text = arcade.Text("Выход из игры", 400, 200,
                                   arcade.color.WHITE, 32, anchor_x="center", 
                                   anchor_y="center", batch=self.batch)
        
        self.back_text = arcade.Text("Назад в меню", 400, 100,
                                   arcade.color.WHITE, 32, anchor_x="center", 
                                   anchor_y="center", batch=self.batch)
        
        self.exit_rect_shape = None
        self.back_rect_shape = None
        self.music_slider_bg_shape = None
        self.music_slider_fill_shape = None
        self.sfx_slider_bg_shape = None
        self.sfx_slider_fill_shape = None
        self.music_slider_handle_shape = None
        self.sfx_slider_handle_shape = None
        
    def on_draw(self):
        self.clear()
        
        width = self.window.width
        slider_x = width // 2 - self.slider_width // 2
        
        music_color = arcade.color.GOLD if self.current_selection == 0 else arcade.color.LIGHT_GRAY
        sfx_color = arcade.color.GOLD if self.current_selection == 1 else arcade.color.LIGHT_GRAY
        exit_color = arcade.color.GOLD if self.current_selection == 2 else arcade.color.LIGHT_GRAY
        back_color = arcade.color.GOLD if self.current_selection == 3 else arcade.color.LIGHT_GRAY
        
        self.music_text.text = f"Громкость музыки: {self.music_volume}%"
        self.music_text.color = music_color
        
        self.sfx_text.text = f"Громкость звуков: {self.sfx_volume}%"
        self.sfx_text.color = sfx_color
        
        music_fill_width = int(self.slider_width * (self.music_volume / 100))
        sfx_fill_width = int(self.slider_width * (self.sfx_volume / 100))
        
        button_width = 350
        button_height = 60
        button_x = width // 2
        
        exit_rect = arcade.rect.XYWH(button_x, 200, button_width, button_height)
        back_rect = arcade.rect.XYWH(button_x, 100, button_width, button_height)
        
        music_slider_bg = arcade.rect.XYWH(slider_x + self.slider_width/2, self.music_slider_y + self.slider_height/2,
                                         self.slider_width, self.slider_height)
        music_slider_fill = arcade.rect.XYWH(slider_x + music_fill_width/2, self.music_slider_y + self.slider_height/2,
                                           music_fill_width, self.slider_height)
        
        sfx_slider_bg = arcade.rect.XYWH(slider_x + self.slider_width/2, self.sfx_slider_y + self.slider_height/2,
                                        self.slider_width, self.slider_height)
        sfx_slider_fill = arcade.rect.XYWH(slider_x + sfx_fill_width/2, self.sfx_slider_y + self.slider_height/2,
                                          sfx_fill_width, self.slider_height)
        
        music_slider_pos = slider_x + music_fill_width
        sfx_slider_pos = slider_x + sfx_fill_width
        
        arcade.draw_rect_filled(exit_rect, exit_color)
        arcade.draw_rect_outline(exit_rect, arcade.color.WHITE, 3)
        
        arcade.draw_rect_filled(back_rect, back_color)
        arcade.draw_rect_outline(back_rect, arcade.color.WHITE, 3)
        
        arcade.draw_rect_filled(music_slider_bg, arcade.color.DARK_GRAY)
        arcade.draw_rect_filled(music_slider_fill, arcade.color.CORNFLOWER_BLUE)
        
        arcade.draw_rect_filled(sfx_slider_bg, arcade.color.DARK_GRAY)
        arcade.draw_rect_filled(sfx_slider_fill, arcade.color.CORNFLOWER_BLUE)
        
        arcade.draw_circle_filled(music_slider_pos, 
                                 self.music_slider_y + self.slider_height // 2,
                                 self.slider_height + 2, arcade.color.GOLD)
        arcade.draw_circle_filled(sfx_slider_pos, 
                                 self.sfx_slider_y + self.slider_height // 2,
                                 self.slider_height + 2, arcade.color.GOLD)
        
        self.batch.draw()
        
    def on_update(self, delta_time):
        mouse_x = self.window._mouse_x
        mouse_y = self.window._mouse_y
        
        width = self.window.width
        slider_x = width // 2 - self.slider_width // 2
        
        button_width = 350
        button_height = 60
        button_x = width // 2
        
        def rect_contains(rect, point_x, point_y):
            return (rect.x - rect.width/2 <= point_x <= rect.x + rect.width/2 and
                    rect.y - rect.height/2 <= point_y <= rect.y + rect.height/2)
        
        music_slider_area = arcade.rect.XYWH(slider_x + self.slider_width/2, self.music_slider_y,
                                           self.slider_width, self.slider_height + 20)
        sfx_slider_area = arcade.rect.XYWH(slider_x + self.slider_width/2, self.sfx_slider_y,
                                         self.slider_width, self.slider_height + 20)
        
        exit_rect = arcade.rect.XYWH(button_x, 200, button_width, button_height)
        back_rect = arcade.rect.XYWH(button_x, 100, button_width, button_height)
        
        if rect_contains(exit_rect, mouse_x, mouse_y):
            self.current_selection = 2
        elif rect_contains(back_rect, mouse_x, mouse_y):
            self.current_selection = 3
        elif rect_contains(music_slider_area, mouse_x, mouse_y):
            self.current_selection = 0
        elif rect_contains(sfx_slider_area, mouse_x, mouse_y):
            self.current_selection = 1
            
    def on_key_press(self, key, modifiers):
        if key == arcade.key.UP:
            self.current_selection = (self.current_selection - 1) % 4
        elif key == arcade.key.DOWN:
            self.current_selection = (self.current_selection + 1) % 4
        elif key == arcade.key.LEFT:
            if self.current_selection == 0:
                self.music_volume = max(0, self.music_volume - 5)
            elif self.current_selection == 1:
                self.sfx_volume = max(0, self.sfx_volume - 5)
        elif key == arcade.key.RIGHT:
            if self.current_selection == 0:
                self.music_volume = min(100, self.music_volume + 5)
            elif self.current_selection == 1:
                self.sfx_volume = min(100, self.sfx_volume + 5)
        elif key == arcade.key.ENTER or key == arcade.key.SPACE:
            if self.current_selection == 2:
                arcade.close_window()
            elif self.current_selection == 3:
                self.window.close()
        elif key == arcade.key.ESCAPE:
            self.window.close()
            
    def on_mouse_press(self, x, y, button, modifiers):
        width = self.window.width
        slider_x = width // 2 - self.slider_width // 2
        
        button_width = 350
        button_height = 60
        button_x = width // 2
        
        def rect_contains(rect, point_x, point_y):
            return (rect.x - rect.width/2 <= point_x <= rect.x + rect.width/2 and
                    rect.y - rect.height/2 <= point_y <= rect.y + rect.height/2)
        
        music_slider_area = arcade.rect.XYWH(slider_x + self.slider_width/2, self.music_slider_y,
                                           self.slider_width, self.slider_height + 20)
        sfx_slider_area = arcade.rect.XYWH(slider_x + self.slider_width/2, self.sfx_slider_y,
                                         self.slider_width, self.slider_height + 20)
        
        exit_rect = arcade.rect.XYWH(button_x, 200, button_width, button_height)
        back_rect = arcade.rect.XYWH(button_x, 100, button_width, button_height)
        
        if rect_contains(music_slider_area, x, y):
            self.dragging_music = True
            self.update_music_volume_from_mouse(x, slider_x)
        elif rect_contains(sfx_slider_area, x, y):
            self.dragging_sfx = True
            self.update_sfx_volume_from_mouse(x, slider_x)
        elif rect_contains(exit_rect, x, y):
            arcade.close_window()
        elif rect_contains(back_rect, x, y):
            self.window.close()
            
    def on_mouse_release(self, x, y, button, modifiers):
        self.dragging_music = False
        self.dragging_sfx = False
        
    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        width = self.window.width
        slider_x = width // 2 - self.slider_width // 2
        
        if self.dragging_music:
            self.update_music_volume_from_mouse(x, slider_x)
        elif self.dragging_sfx:
            self.update_sfx_volume_from_mouse(x, slider_x)
            
    def update_music_volume_from_mouse(self, mouse_x, slider_x):
        relative_x = mouse_x - slider_x
        self.music_volume = max(0, min(100, int((relative_x / self.slider_width) * 100)))
        
    def update_sfx_volume_from_mouse(self, mouse_x, slider_x):
        relative_x = mouse_x - slider_x
        self.sfx_volume = max(0, min(100, int((relative_x / self.slider_width) * 100)))

def main():
    window = arcade.Window(800, 700, "Настройки")
    settings_view = SettingsView()
    window.show_view(settings_view)
    arcade.run()

if __name__ == "__main__":
    main()