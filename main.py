import arcade
from views.start_view import StartView
from database import init_dbs
import random


SCREEN_WIDTH, SCREEN_HEIGHT = arcade.window_commands.get_display_size()
SCREEN_TITLE = "Battle of the Square"
COUNT_MUSIC = 6


class MainWindow(arcade.Window):
    def __init__(self, width, height, title):
        super().__init__(width, height, title, fullscreen=True)
        self.is_fullscreen = True
        self.music = arcade.play_sound(arcade.load_sound(f"assets/music/sound{random.randint(1, COUNT_MUSIC)}.mp3"), 1, loop=True)
        self.music_counter = 0

    def on_key_press(self, key, modifiers):
        if arcade.key.ESCAPE == key:
            self.is_fullscreen = not (self.is_fullscreen)
            self.set_fullscreen(self.is_fullscreen)

    def on_update(self, delta_time):
        self.music_counter += delta_time
        if self.music_counter >= 120:
            self.music_counter = 0
            arcade.stop_sound(self.music)
            self.music = arcade.play_sound(arcade.load_sound(f"assets/music/sound{random.randint(1, COUNT_MUSIC)}.mp3"), 0.6, loop=True)


def setup_game(width=800, height=600, title="Battle of the Square"):
    window = MainWindow(width, height, title)
    start_view = StartView()
    window.show_view(start_view)
    return window


def main():
    init_dbs()
    setup_game(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    arcade.run()


if __name__ == "__main__":
    main()
