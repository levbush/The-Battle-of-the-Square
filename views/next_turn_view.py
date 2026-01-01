import arcade
from arcade.gui import UIManager, UIFlatButton, UILabel
from arcade.gui.widgets.layout import UIAnchorLayout, UIBoxLayout
from classes import Player


class NextTurnView(arcade.View):
    def __init__(self, player: Player, parent: arcade.View):
        super().__init__(background_color=parent.background_color)

        self.parent = parent
        self.player = player

        self.overlay_alpha = 0
        self.fade_in = True
        self.fade_out = False
        self.fade_speed = 300

        self.manager = UIManager()
        self.manager.enable()

        anchor = UIAnchorLayout()
        box = UIBoxLayout(vertical=True, space_between=15)

        label = UILabel(
            text=f"Игрок {player.id + 1}",
            font_size=18,
            text_color=arcade.color.WHITE,
        )

        button_style = {
            "normal": UIFlatButton.UIStyle(
                font_size=14,
                font_color=arcade.color.WHITE,
                bg=arcade.color.BLUE,
            ),
            "hover": UIFlatButton.UIStyle(
                font_size=14,
                font_color=arcade.color.WHITE,
                bg=arcade.color.SAPPHIRE_BLUE,
            ),
            "press": UIFlatButton.UIStyle(
                font_size=14,
                font_color=arcade.color.BLACK,
                bg=arcade.color.BLUE_BELL,
            ),
        }

        btn = UIFlatButton(
            text="Продолжить",
            width=150,
            height=30,
            style=button_style,
        )

        def on_click(_):
            self.fade_out = True
            self.fade_in = False

        btn.on_click = on_click

        box.add(label)
        box.add(btn)

        anchor.add(box, anchor_x="center", anchor_y="center")
        self.manager.add(anchor)

    def on_update(self, delta_time: float):
        if self.fade_in:
            self.overlay_alpha += self.fade_speed * delta_time
            if self.overlay_alpha >= 180:
                self.overlay_alpha = 180
                self.fade_in = False

        elif self.fade_out:
            self.overlay_alpha -= self.fade_speed * delta_time
            if self.overlay_alpha <= 0:
                self.overlay_alpha = 0
                self.parent.next_turn()

    def on_draw(self):
        self.clear()

        arcade.draw_lrbt_rectangle_filled(
            0,
            self.window.width,
            0,
            self.window.height,
            (0, 0, 0, int(self.overlay_alpha)),
        )

        self.manager.draw()

    def on_hide_view(self):
        self.manager.disable()
