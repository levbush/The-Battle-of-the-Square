import arcade
from classes import AnimatedButton
from arcade.gui import UIManager
from arcade.gui.widgets.layout import UIAnchorLayout, UIBoxLayout
import sqlite3
from database import DB_PATH
from views.create_game_view import CreateGameView


class StartView(arcade.View):
    def __init__(self):
        super().__init__()
        self.back_img = arcade.load_texture(r'assets/menu_background.jpg')

        self.manager = UIManager()
        self.manager.enable()

        self.anchor_layout = UIAnchorLayout()
        self.box_layout = UIBoxLayout(vertical=True, space_between=10)

        self.setup_widgets()

        self.anchor_layout.add(self.box_layout)
        self.manager.add(self.anchor_layout)

    def setup_widgets(self):
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        data = c.execute('SELECT * FROM map').fetchone()
        width = 200
        height = 60
        style = {
            'normal': {
                'bg_color': arcade.types.Color.from_hex_string('#4DA3FF'),
                'font_color': arcade.color.WHITE,
                'border_radius': 16,
            },
            'hover': {
                'bg_color': arcade.types.Color.from_hex_string('#6CB8FF'),
                'font_color': arcade.color.WHITE,
                'border_radius': 16,
            },
            'press': {
                'bg_color': arcade.types.Color.from_hex_string('#3A8BE0'),
                'font_color': arcade.color.WHITE,
                'border_radius': 16,
            },
        }
        self.new_game_button = AnimatedButton(text='Новая игра', style=style, width=width, height=height)
        if data:
            self.resume_game_button = AnimatedButton(text='Продолжить игру', style=style, width=width, height=height)
        else:
            self.resume_game_button = None

        self.new_game_button.on_click = lambda event: self.new_game()
        self.box_layout.add(self.new_game_button)

    def on_draw(self):
        self.clear()
        arcade.draw_texture_rect(
            self.back_img, arcade.rect.XYWH(self.width // 2, self.height // 2, self.width, self.height), alpha=200
        )
        self.manager.draw()

    def on_update(self, delta_time):
        self.new_game_button.update_animation(delta_time)
        if self.resume_game_button:
            self.resume_game_button.update_animation(delta_time)

    def new_game(self):
        view = CreateGameView()
        self.manager.disable()
        self.window.show_view(view)
