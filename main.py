import arcade
import random
import sqlite3
from views.start_view import StartView
from views.game_view import GameView, SettingsView, WinnerView, NextTurnView
from database import init_db, DB_PATH


SCREEN_WIDTH, SCREEN_HEIGHT = arcade.window_commands.get_display_size()
SCREEN_TITLE = "Battle of the Square"
COUNT_MUSIC = 6


class MainWindow(arcade.Window):
    """The window of the game."""

    def __init__(self, width, height, title):
        super().__init__(width, height, title, fullscreen=True)

        self.music_volume = 0.6
        self.sfx_volume = 1.0
        self.is_fullscreen = True

        self.music = None
        self.music_counter = 0

        self.load_settings()
        self.start_music()

    def start_music(self):
        """Start background music without stopping existing one."""
        if self.music:
            return

        sound = arcade.load_sound(
            f"assets/music/sound{random.randint(1, COUNT_MUSIC)}.mp3"
        )
        self.music = arcade.play_sound(sound, self.music_volume, loop=True)
        self.music_counter = 0

    def restart_music(self):
        """Force restart music."""
        if self.music:
            arcade.stop_sound(self.music)
            self.music = None
        self.start_music()

    def update_music_volume(self):
        """Apply volume change to currently playing music."""
        if self.music:
            self.music.volume = self.music_volume


    def on_key_press(self, key, modifiers):
        if key == arcade.key.F11:
            self.is_fullscreen = not self.is_fullscreen
            self.set_fullscreen(self.is_fullscreen)

        elif (
            key == arcade.key.ESCAPE
            and not isinstance(
                self.current_view,
                (GameView, SettingsView, WinnerView, NextTurnView),
            )
        ):
            self.on_key_press(arcade.key.F11, 0)

    def on_update(self, delta_time):
        self.music_counter += delta_time
        if self.music_counter >= 120:
            self.music_counter = 0
            self.restart_music()


    def set_settings(self, **kwargs):
        'Set settings'
        settings = ('music_volume', 'sfx_volume')
        changed = False
        for setting in settings:
            value = kwargs.get(setting)
            if value is not None:
                value /= 100
                if getattr(self, setting) != value:
                    setattr(self, setting, value)
                    changed = True

        if not changed:
            return

        self.update_music_volume()

        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.executemany(
            "INSERT OR REPLACE INTO settings VALUES (?, ?)",
            ((s, getattr(self, s) * 100) for s in settings),
        )
        conn.commit()
        conn.close()

    def load_settings(self):
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT key, value FROM settings")
        for key, value in c.fetchall():
            setattr(self, key, value / 100)
        conn.close()


    def to_menu(self):
        self.show_view(StartView())

    def on_close(self):
        if isinstance(self.current_view, GameView):
            self.current_view.save_map()
        return super().on_close()



def setup_game(width=800, height=600, title="Battle of the Square"):
    window = MainWindow(width, height, title)
    window.to_menu()
    return window


def main():
    init_db()
    setup_game(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    arcade.run()


if __name__ == "__main__":
    main()
