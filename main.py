import arcade
import random
from views.start_view import StartView
from views.game_view import GameView
from database import init_db


SCREEN_WIDTH, SCREEN_HEIGHT = arcade.window_commands.get_display_size()
SCREEN_TITLE = "Battle of the Square"
COUNT_MUSIC = 6


class MainWindow(arcade.Window):
    'The window of the game.'

    def __init__(self, width, height, title):
        super().__init__(width, height, title, fullscreen=True)
        self.music_volume = 0.6
        self.sfx_volume = 1
        self.is_fullscreen = True
        self.reset()

    def reset(self):
        'Reset self'
        self.music = arcade.play_sound(
            arcade.load_sound(f"assets/music/sound{random.randint(1, COUNT_MUSIC)}.mp3"), self.music_volume, loop=True
        )
        self.music_counter = 0

    def on_key_press(self, key, modifiers):
        if arcade.key.F11 == key:
            self.is_fullscreen = not self.is_fullscreen
            self.set_fullscreen(self.is_fullscreen)

    def on_update(self, delta_time):
        self.music_counter += delta_time
        if self.music_counter >= 120:
            self.music_counter = 0
            arcade.stop_sound(self.music)
            self.music = arcade.play_sound(
                arcade.load_sound(f"assets/music/sound{random.randint(1, COUNT_MUSIC)}.mp3"),
                self.music_volume,
                loop=True,
            )

    def set_settings(self, **kwargs):
        'Set settings'
        self.music_volume = kwargs.get('music_volume') / 100 or self.music_volume
        self.sfx_volume = kwargs.get('sfx_volume') / 100 or self.sfx_volume

    def to_menu(self):
        'Return to the very first view (`StartView()`)'
        self.show_view(StartView())

    def on_close(self):
        if isinstance(self.current_view, GameView): self.current_view.save_map()
        return super().on_close()


def setup_game(width=800, height=600, title="Battle of the Square"):
    '''Setup the game'''
    window = MainWindow(width, height, title)
    start_view = StartView()
    window.show_view(start_view)
    return window


def main():
    '''Start the game'''
    init_db()
    setup_game(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    arcade.run()


if __name__ == "__main__":
    main()
