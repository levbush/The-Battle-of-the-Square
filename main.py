import arcade
from views.start_view import StartView
from database import init_dbs


SCREEN_WIDTH, SCREEN_HEIGHT = arcade.window_commands.get_display_size()
SCREEN_TITLE = "Battle of the Square"


def setup_game(width=800, height=600, title="Battle of the Square"):
    window = arcade.Window(width, height, title)
    start_view = StartView()
    window.show_view(start_view)
    return window


def main():
    init_dbs()
    setup_game(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    arcade.run()


if __name__ == "__main__":
    main()
