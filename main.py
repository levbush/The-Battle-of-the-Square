import arcade
import arcade.gui
import tkinter as tk


root = tk.Tk()
SCREEN_WIDTH = root.winfo_screenwidth()
SCREEN_HEIGHT = root.winfo_screenheight()

SCREEN_TITLE = "Our game"

class MainWindow(arcade.Window):
    def __init__(self, width, height, title):
        super().__init__(width, height, title, fullscreen=True)
        self.back_img = arcade.load_texture("images/back_images_in_menu.jpg")

    def setup(self):
        pass

    def on_draw(self):
        self.clear()
        arcade.draw_texture_rect(self.back_img, arcade.rect.XYWH(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, SCREEN_WIDTH, SCREEN_HEIGHT), alpha=150)

    def on_update(self, delta_time):
        pass


def setup_game(width=800, height=600, title="Battle of the Square"):
    game = MainWindow(width, height, title)
    game.setup()
    return game


def main():
    setup_game(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    arcade.run()


if __name__ == "__main__":
    main()
