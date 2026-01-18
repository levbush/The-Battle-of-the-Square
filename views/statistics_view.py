import arcade

class StatisticsView(arcade.View):
    """View для отображения статистики игры"""
    def __init__(self, parent, player_name="Игрок", turn=1, units_killed=0, custom_value="X"):
        super().__init__()
        
        self.parent = parent
        self.stats = {
            "player": player_name,
            "turn": turn,
            "units_killed": units_killed,
            "custom": custom_value
        }
        
        self.background_color = arcade.color.DARK_SLATE_GRAY
        self.title_color = arcade.color.GOLD
        self.text_color = arcade.color.WHITE
        self.highlight_color = arcade.color.LIGHT_BLUE

        arcade.set_background_color(self.background_color)

        # self.center_x = self.window.width // 2
        # self.center_y = self.window.height // 2
    
    def on_draw(self):
        self.clear()

        arcade.draw_text(
            "СТАТИСТИКА ИГРЫ",
            self.center_x,
            self.window.height - 100,
            self.title_color,
            36,
            anchor_x="center",
            font_name="Gothic"
        )
        
        arcade.draw_line(
            self.center_x - 200,
            self.window.height - 130,
            self.center_x + 200,
            self.window.height - 130,
            self.title_color,
            3
        )

        stat_y = self.window.height - 200
        line_height = 50

        arcade.draw_text(
            "Игрок:",
            self.center_x - 150,
            stat_y,
            self.highlight_color,
            24,
            anchor_x="left",
            font_name="Arial"
        )
        arcade.draw_text(
            str(self.stats["player"]),
            self.center_x + 50,
            stat_y,
            self.text_color,
            24,
            anchor_x="left",
            font_name="Arial"
        )

        arcade.draw_text(
            "Ход:",
            self.center_x - 150,
            stat_y - line_height,
            self.highlight_color,
            24,
            anchor_x="left",
            font_name="Arial"
        )
        arcade.draw_text(
            str(self.stats["turn"]),
            self.center_x + 50,
            stat_y - line_height,
            self.text_color,
            24,
            anchor_x="left",
            font_name="Arial"
        )
        
        arcade.draw_text(
            "Юнитов убито:",
            self.center_x - 150,
            stat_y - line_height * 2,
            self.highlight_color,
            24,
            anchor_x="left",
            font_name="Arial"
        )
        arcade.draw_text(
            str(self.stats["units_killed"]),
            self.center_x + 50,
            stat_y - line_height * 2,
            self.text_color,
            24,
            anchor_x="left",
            font_name="Arial"
        )
        
        arcade.draw_text(
            "X:",
            self.center_x - 150,
            stat_y - line_height * 3,
            self.highlight_color,
            24,
            anchor_x="left",
            font_name="Arial"
        )
        arcade.draw_text(
            str(self.stats["custom"]),
            self.center_x + 50,
            stat_y - line_height * 3,
            self.text_color,
            24,
            anchor_x="left",
            font_name="Arial"
        )
        
        arcade.draw_text(
            "Нажмите ПРОБЕЛ для продолжения",
            self.center_x,
            100,
            arcade.color.LIGHT_GRAY,
            20,
            anchor_x="center",
            font_name="Arial"
        )
        
        self._draw_decoration()
    
    def _draw_decoration(self):
        corner_size = 20
        corners = [
            (50, self.window.height - 50),
            (self.window.width - 50, self.window.height - 50),
            (50, 50),
            (self.window.width - 50, 50)
        ]
        
        for x, y in corners:
            arcade.draw_rect_outline(arcade.rect.LBWH(x, y, corner_size, corner_size), self.title_color, 2)
    
    def on_key_press(self, key, modifiers):
        """Обработка нажатия клавиш"""
        if key == arcade.key.SPACE:
            print("Возврат в игру...")
            
        elif key == arcade.key.ESCAPE:
            arcade.close_window()
        
        elif key == arcade.key.R:
            self.stats["turn"] += 1
            self.stats["units_killed"] += 5
    
    def update_stat(self, stat_name, value):
        """Обновление статистики"""
        if stat_name in self.stats:
            self.stats[stat_name] = value


class GameStatsManager:
    def __init__(self):
        self.stats = {
            "player": "Игрок 1",
            "turn": 1,
            "units_killed": 0,
            "custom": "Пусто"
        }
    
    def increment_turn(self):
        self.stats["turn"] += 1
    
    def add_kills(self, amount=1):
        self.stats["units_killed"] += amount
    
    def get_stats(self):
        return self.stats.copy()
