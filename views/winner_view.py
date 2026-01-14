import arcade
from pyglet.graphics import Batch


class WinnerView(arcade.View):
    def __init__(self, winner=None, parent=None):
        super().__init__()
        self.winner = winner
        self.parent = parent

        self.batch = Batch()
        
        if self.winner is None:
            text = "Вы проиграли!"
        else:
            text = f"Победил игрок {self.winner}!"
        
        self.texts = [arcade.Text(
            text,
            self.window.width // 2,
            self.window.height // 2,
            arcade.color.WHITE,
            36,
            anchor_x="center",
            anchor_y="center",
            batch=self.batch
        ),

        arcade.Text(
            "ESC — меню",
            self.window.width // 2,
            self.window.height // 2 - 80,
            arcade.color.GRAY,
            18,
            anchor_x="center",
            anchor_y="center",
            batch=self.batch
        )]

    def on_show_view(self):
        arcade.set_background_color(arcade.color.BLACK)

    def on_draw(self):
        self.clear()
        self.batch.draw()

    def on_key_press(self, symbol, modifiers):
        if symbol == arcade.key.ESCAPE:
            self.window.to_menu()
