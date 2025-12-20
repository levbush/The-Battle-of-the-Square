import arcade
import arcade.color


class MapView(arcade.View):
    def __init__(self, size, bot_amount, player_amount, bot_difficulty):
        super().__init__()
        arcade.set_background_color(arcade.color.SKY_BLUE)

    def setup(self):
        pass

    def on_draw(self):
        self.clear()
        pass

    def on_update(self, delta_time):
        pass

