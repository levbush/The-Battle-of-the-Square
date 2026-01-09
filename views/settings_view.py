import arcade
import arcade.gui
import sqlite3
from database import DB_PATH


class SettingsView(arcade.View):
    def __init__(self, parent=None):
        super().__init__()

        self.parent = parent
        self.music_volume = int(self.window.music_volume * 100)
        self.sfx_volume = int(self.window.sfx_volume * 100)

        self.manager = arcade.gui.UIManager()
        self.manager.enable()

        self.v_box = arcade.gui.UIBoxLayout(vertical=True, space_between=20)

        BUTTON_STYLE = {
            "normal": {
                "font_size": 28,
                "font_color": arcade.color.WHITE,
                "bg_color": arcade.color.DARK_GRAY,
                "border_color": arcade.color.WHITE,
                "border_width": 2,
            },
            "hover": {
                "font_size": 28,
                "font_color": arcade.color.BLACK,
                "bg_color": arcade.color.GOLD,
                "border_color": arcade.color.GOLD,
                "border_width": 2,
            },
            "press": {
                "font_size": 28,
                "font_color": arcade.color.WHITE,
                "bg_color": arcade.color.GRAY,
                "border_color": arcade.color.GOLD,
                "border_width": 2,
            },
            "disabled": {
                "font_size": 28,
                "font_color": arcade.color.GRAY,
                "bg_color": arcade.color.DARK_GRAY,
                "border_color": arcade.color.GRAY,
                "border_width": 2,
            },
        }

        title = arcade.gui.UILabel(
            text="НАСТРОЙКИ", text_color=arcade.color.GOLD, font_size=48, width=600, align="center"
        )
        self.v_box.add(title.with_padding(top=40, bottom=40))

        self.music_label = arcade.gui.UILabel(
            text=f"Громкость музыки: {self.music_volume}%",
            font_size=22,
            width=600,
            text_color=arcade.color.LIGHT_GRAY,
            align="center",
        )
        self.v_box.add(self.music_label)

        self.music_slider = arcade.gui.UISlider(
            value=self.music_volume, min_value=0, max_value=100, width=400, height=20
        )
        self.music_slider.on_change = self.on_music_change
        self.v_box.add(self.music_slider)

        self.sfx_label = arcade.gui.UILabel(
            text=f"Громкость звуков: {self.sfx_volume}%",
            font_size=22,
            width=600,
            text_color=arcade.color.LIGHT_GRAY,
            align="center",
        )
        self.v_box.add(self.sfx_label.with_padding(top=20))

        self.sfx_slider = arcade.gui.UISlider(value=self.sfx_volume, min_value=0, max_value=100, width=400, height=20)
        self.sfx_slider.on_change = self.on_sfx_change
        self.v_box.add(self.sfx_slider)

        exit_button = arcade.gui.UIFlatButton(text="Выход из игры", width=350, style=BUTTON_STYLE)
        exit_button.on_click = self.on_exit
        self.v_box.add(exit_button)

        to_menu_button = arcade.gui.UIFlatButton(text="Назад в меню", width=350, style=BUTTON_STYLE)
        to_menu_button.on_click = self.on_back
        self.v_box.add(to_menu_button)

        resign_button = arcade.gui.UIFlatButton(text="Сдаться", width=350, style=BUTTON_STYLE)
        resign_button.on_click = self.resign
        self.v_box.add(resign_button)

        self.container = arcade.gui.UIAnchorLayout(x=0, y=0, width=self.window.width, height=self.window.height)

        self.container.add(child=self.v_box, anchor_x="center", anchor_y="center")

        self.manager.add(self.container)

    def on_resize(self, width, height):
        self.container.width = width
        self.container.height = height

    def on_music_change(self, event: arcade.gui.UIOnChangeEvent):
        self.music_volume = int(event.source.value)
        self.music_label.text = f"Громкость музыки: {self.music_volume}%"

    def on_sfx_change(self, event: arcade.gui.UIOnChangeEvent):
        self.sfx_volume = int(event.source.value)
        self.sfx_label.text = f"Громкость звуков: {self.sfx_volume}%"

    def on_exit(self, event):
        self.save()
        arcade.close_window()

    def on_back(self, event):
        self.save()
        self.window.to_menu()

    def on_key_press(self, key, _mod):
        if key == arcade.key.ESCAPE:
            self.save()
            if self.parent:
                self.window.show_view(self.parent)

    def on_draw(self):
        self.clear(arcade.color.DARK_BLUE_GRAY)
        self.manager.draw()

    def save(self):
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()

        ...

        self.window.set_settings(music_volume=self.music_volume, sfx_volume=self.sfx_volume)

    def resign(self, _):
        self.on_key_press(arcade.key.ESCAPE, 0)
        self.parent.current_player.is_bot = True
        self.parent.change_POV()

    def on_show_view(self):
        self.parent.manager.disable()

    def on_hide_view(self):
        self.manager.disable()
