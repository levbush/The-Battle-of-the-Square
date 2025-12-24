import arcade
from arcade.gui import UIManager, UILabel, UIFlatButton
from arcade.gui.widgets.layout import UIAnchorLayout, UIBoxLayout
from classes import HorizontalRadioButtonGroup
from views.game_view import GameView


class CreateGameView(arcade.View):
    def __init__(self):
        super().__init__()
        self.back_img = arcade.load_texture('assets/menu_background.jpg')

        self.manager = UIManager()
        self.manager.enable()

        self.anchor_layout = UIAnchorLayout()
        self.vertical_layout = UIBoxLayout(vertical=True, space_between=15)

        self.setup_widgets()

        self.anchor_layout.add(self.vertical_layout)
        self.manager.add(self.anchor_layout)

    def setup_widgets(self):
        self.area_options = [121, 196, 256, 324, 400, 900]
        self.bot_difficulty_options = ['Easy', 'Hard']

        self.area_selector = HorizontalRadioButtonGroup(
            self.area_options, on_change=lambda *_: self.update_selectors('area')
        )

        self.bot_amount_selector = HorizontalRadioButtonGroup([], on_change=lambda *_: self.update_selectors('bot'))

        self.player_amount_selector = HorizontalRadioButtonGroup(
            [], on_change=lambda *_: self.update_selectors('player')
        )

        self.bot_difficulty_selector = HorizontalRadioButtonGroup(self.bot_difficulty_options)

        self.vertical_layout.add(UILabel(text='Размер карты'))
        self.vertical_layout.add(self.area_selector.widget)

        self.vertical_layout.add(UILabel(text='Количество ботов'))
        self.vertical_layout.add(self.bot_amount_selector.widget)

        self.vertical_layout.add(UILabel(text='Количество игроков'))
        self.vertical_layout.add(self.player_amount_selector.widget)

        self.bot_difficulty_label = UILabel(text='Уровень сложности')
        self.vertical_layout.add(self.bot_difficulty_label)
        self.vertical_layout.add(self.bot_difficulty_selector.widget)

        self.start_game_button = UIFlatButton(text='Начать игру')
        self.start_game_button.on_click = lambda *_: self.start_game()
        self.vertical_layout.add(self.start_game_button)

        self.update_selectors('')

    def update_selectors(self, sender):
        if self.area_selector._selected_index is None:
            return

        area_index, area_value = self.area_selector.selected()

        max_player_amount = (2 + area_index) * 2

        player_amount = (
            self.player_amount_selector.selected()[1] if self.player_amount_selector._selected_index is not None else 1
        )
        if sender != 'bot':
            bot_options = list(range(max(1, max_player_amount - player_amount + 1)))
            self.bot_amount_selector.set_options(bot_options)
        bot_amount = (
            self.bot_amount_selector.selected()[1] if self.bot_amount_selector._selected_index is not None else 0
        )
        if sender != 'player':
            player_options = list(range(1, max(2, max_player_amount - bot_amount + 1)))
            self.player_amount_selector.set_options(player_options)

        if bot_amount > 0:
            if self.bot_difficulty_selector.widget not in self.vertical_layout.children:
                self.vertical_layout.remove(self.start_game_button)
                self.vertical_layout.add(self.bot_difficulty_label)
                self.vertical_layout.add(self.bot_difficulty_selector.widget)
                self.vertical_layout.add(self.start_game_button)
        else:
            if self.bot_difficulty_selector.widget in self.vertical_layout.children:
                self.vertical_layout.remove(self.bot_difficulty_label)
                self.vertical_layout.remove(self.bot_difficulty_selector.widget)
                

    def on_draw(self):
        self.clear()
        arcade.draw_texture_rect(
            self.back_img, arcade.rect.XYWH(self.width // 2, self.height // 2, self.width, self.height), alpha=200
        )
        self.manager.draw()

    def start_game(self):
        area, bot_amount, player_amount, bot_difficulty = (
            self.area_selector.selected(),
            self.bot_amount_selector.selected(),
            self.player_amount_selector.selected(),
            self.bot_difficulty_selector.selected(),
        )
        if None in [area, bot_amount, player_amount] or bot_amount and bot_difficulty is None:
            return
        size = int(area[1] ** 0.5)
        bot_amount = bot_amount[1]
        player_amount = player_amount[1]
        if bot_amount:
            bot_difficulty = bot_difficulty[0]
        else:
            bot_difficulty = None

        view = GameView(size, bot_amount, player_amount, bot_difficulty)
        self.window.hide_view()
        self.window.show_view(view)
