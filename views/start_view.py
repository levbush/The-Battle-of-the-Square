import arcade
import sqlite3
import random
from classes import AnimatedButton
from arcade.gui import UIManager
from arcade.gui.widgets.layout import UIAnchorLayout, UIBoxLayout
from database import DB_PATH, SPARK_TEX
from views.create_game_view import CreateGameView, GameView
from arcade.particles import EmitMaintainCount, Emitter, FadeParticle


class StartView(arcade.View):
    'The fist view'

    def __init__(self):
        super().__init__()
        self.back_img = arcade.load_texture(r'assets/misc/menu_background.jpg')

        self.manager = UIManager()
        self.manager.enable()

        self.anchor_layout = UIAnchorLayout()
        self.box_layout = UIBoxLayout(vertical=True, space_between=10)

        self.setup_widgets()

        self.anchor_layout.add(self.box_layout)
        self.manager.add(self.anchor_layout)

        self.trail = Emitter(
            center_xy=(0, 0),
            emit_controller=EmitMaintainCount(45),
            particle_factory=lambda e: FadeParticle(
                filename_or_texture=random.choice(SPARK_TEX),
                change_xy=(random.uniform(-0.2, 0.2), random.uniform(-0.8, -0.4)),
                lifetime=random.uniform(1.0, 1.6),
                start_alpha=150,
                end_alpha=0,
                scale=random.uniform(0.55, 0.75),
            ),
        )

    def setup_widgets(self):
        'Setup buttons'
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

        self.new_game_button.on_click = lambda _: self.new_game()
        self.box_layout.add(self.new_game_button)
        if self.resume_game_button:
            self.box_layout.add(self.resume_game_button)
            self.resume_game_button.on_click = lambda _: self.resume_game()

    def on_draw(self):
        self.clear()
        arcade.draw_texture_rect(
            self.back_img, arcade.rect.XYWH(self.width // 2, self.height // 2, self.width, self.height), alpha=200
        )
        self.manager.draw()
        self.trail.draw()

    def on_update(self, delta_time):
        self.new_game_button.update_animation(delta_time)
        if self.resume_game_button:
            self.resume_game_button.update_animation(delta_time)
        self.trail.update()

    def new_game(self):
        'Start the creation of a new game'
        view = CreateGameView()
        self.manager.disable()
        self.window.show_view(view)

    def on_mouse_motion(self, x, y, dx, dy):
        self.trail.center_x = x
        self.trail.center_y = y - 20

    def resume_game(self):
        'Load the game from db'

        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()

        c.execute('SELECT key, value FROM game_state')
        state = {k: eval(v) for k, v in c.fetchall()}

        conn.close()

        size_map = state["size_map"]
        bot_amount = state["bot_amount"]
        player_amount = state["player_amount"]
        bot_difficulty = state["bot_difficulty"]
        view = GameView(new_game=False, size_map=size_map, bot_amount=bot_amount, player_amount=player_amount, bot_difficulty=bot_difficulty)

        self.manager.disable()
        self.window.show_view(view)
