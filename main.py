import arcade
from views.start_view import StartView
from database import init_dbs


SCREEN_WIDTH, SCREEN_HEIGHT = arcade.window_commands.get_display_size()
SCREEN_TITLE = "Battle of the Square"


class MainWindow(arcade.Window):
    # для событий, клавиш, мыши и тд.
    def __init__(self, width, height, title):
        super().__init__(width, height, title, fullscreen=True)
        self.is_fullscreen = True
    
    def on_key_press(self, key, modifiers):
        if arcade.key.ESCAPE == key:
            self.is_fullscreen = not(self.is_fullscreen)
            self.set_fullscreen(self.is_fullscreen)


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
