import arcade
from pyglet.graphics import Batch


class StatisticsView(arcade.View):
    """View для отображения статистики игры"""
    def __init__(self, parent, player_name="Игрок", turn=0, units_killed=0, custom_value="X"):
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
        self.gray_color = arcade.color.LIGHT_GRAY

        arcade.set_background_color(self.background_color)
        self.setup()
    
    def setup(self):
        self.batch = Batch()
        self.stat_y = self.window.height - 200
        self.line_height = 50

        self.main_label = arcade.Text(
            "СТАТИСТИКА ИГРЫ",
            self.window.width // 2,
            self.window.height - 100,
            self.title_color,
            36,
            anchor_x="center",
            font_name="Gothic",
            batch=self.batch
        )

        self.player_label = arcade.Text(
            "Игрок:",
            self.window.width // 2 - 150,
            self.stat_y,
            self.highlight_color,
            24,
            anchor_x="left",
            font_name="Arial",
            batch=self.batch
        )
        self.player_value = arcade.Text(
            str(self.stats["player"]),
            self.window.width // 2 + 100,
            self.stat_y,
            self.text_color,
            24,
            anchor_x="left",
            font_name="Arial",
            batch=self.batch
        )

        self.turn_label = arcade.Text(
            "Ход:",
            self.window.width // 2 - 150,
            self.stat_y - self.line_height,
            self.highlight_color,
            24,
            anchor_x="left",
            font_name="Arial",
            batch=self.batch
        )
        self.turn_value = arcade.Text(
            str(self.stats["turn"]),
            self.window.width // 2 + 100,
            self.stat_y - self.line_height,
            self.text_color,
            24,
            anchor_x="left",
            font_name="Arial",
            batch=self.batch
        )

        self.kills_label = arcade.Text(
            "Юнитов убито:",
            self.window.width // 2 - 150,
            self.stat_y - self.line_height * 2,
            self.highlight_color,
            24,
            anchor_x="left",
            font_name="Arial",
            batch=self.batch
        )
        self.kills_value = arcade.Text(
            str(self.stats["units_killed"]),
            self.window.width // 2 + 100,
            self.stat_y - self.line_height * 2,
            self.text_color,
            24,
            anchor_x="left",
            font_name="Arial",
            batch=self.batch
        )

        self.custom_label = arcade.Text(
            "X:",
            self.window.width // 2 - 150,
            self.stat_y - self.line_height * 3,
            self.highlight_color,
            24,
            anchor_x="left",
            font_name="Arial",
            batch=self.batch
        )
        self.custom_value = arcade.Text(
            str(self.stats["custom"]),
            self.window.width // 2 + 100,
            self.stat_y - self.line_height * 3,
            self.text_color,
            24,
            anchor_x="left",
            font_name="Arial",
            batch=self.batch
        )

        self.continue_label = arcade.Text(
            "Нажмите ПРОБЕЛ для продолжения",
            self.window.width // 2,
            100,
            self.gray_color,
            20,
            anchor_x="center",
            font_name="Arial",
            batch=self.batch
        )

    def on_draw(self):
        self.clear()

        arcade.draw_line(
            self.window.width // 2 - 200,
            self.window.height - 130,
            self.window.width // 2 + 200,
            self.window.height - 130,
            self.title_color,
            3
        )

        self.batch.draw()
        
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
        if key == arcade.key.SPACE or key == arcade.key.ESCAPE or key == arcade.key.L:
            if self.parent:
                self.window.show_view(self.parent)
