import arcade


SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Red Hat collects berries"

class BerryGame(arcade.Window):
    def __init__(self, width, height, title):
        super().__init__(width, height, title)
        pass

    def setup(self):
        pass

    def on_draw(self):
        self.clear()
        pass

    def on_update(self, delta_time):
        pass


def setup_game(width=800, height=600, title="Red Hat collects berries"):
    game = BerryGame(width, height, title)
    game.setup()
    return game


def main():
    setup_game(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    arcade.run()


if __name__ == "__main__":
    main()
