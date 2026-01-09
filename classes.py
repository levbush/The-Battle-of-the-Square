import arcade.gui
from arcade.types import AnchorPoint
import arcade
from dataclasses import dataclass, field
from views.discovery_view import TechTree

if __name__ == '__main__':
    from terrain.terrain_classes import TileBase


class AnimatedButton(arcade.gui.UIFlatButton):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.scale_target = 1.0
        self.scale_current = 1.0

        self._base_rect = self.rect

    def update_animation(self, delta_time):
        if self.pressed:
            self.scale_target = 0.95
        elif self.hovered:
            self.scale_target = 1.05
        else:
            self.scale_target = 1.0

        diff = self.scale_target - self.scale_current
        self.scale_current += diff * min(delta_time * 10, 1)

        self.rect = self._base_rect.scale(new_scale=self.scale_current, anchor=AnchorPoint.CENTER)


class HorizontalRadioButtonGroup:
    def __init__(
        self,
        options: list[str],
        default_index: int = 0,
        on_change=None,
        font_size: int = 16,
        button_width: int = 100,
        button_height: int = 40,
        spacing: int = 20,
    ):
        self.options = options
        self.on_change = on_change
        self.font_size = font_size
        self._selected_index = None
        self.button_width = button_width
        self.button_height = button_height

        self.layout = arcade.gui.UIBoxLayout(vertical=False, space_between=spacing)

        self.buttons: list[arcade.gui.UIFlatButton] = []

        for i, label in enumerate(options):
            button = arcade.gui.UIFlatButton(text=str(label), width=button_width, height=button_height)
            button.on_click = self._make_handler(i)
            self.buttons.append(button)
            self.layout.add(button)

        if self.options:
            self.set_selected(default_index, False)

    def selected(self):
        if self._selected_index is None:
            return None
        return self._selected_index, (
            int(self.options[self._selected_index])
            if isinstance(self.options[self._selected_index], int) or self.options[self._selected_index].isdigit()
            else self.options[self._selected_index]
        )

    def set_selected(self, value, do_trigger=True):
        if isinstance(value, int):
            index = value
        elif isinstance(value, str):
            index = self.options.index(value)
        else:
            raise TypeError('selected must be int or str')

        if index == self._selected_index:
            return

        self._selected_index = index
        self._update_visuals()
        if self.on_change and do_trigger:
            self.on_change(index, self.options[index])

    def _make_handler(self, index):
        def handler(event):
            self.set_selected(index)

        return handler

    def set_options(self, options, default_index=0):
        self.layout.clear()
        self.buttons.clear()

        self.options = [str(o) for o in options]

        for i, label in enumerate(self.options):
            button = arcade.gui.UIFlatButton(text=label, width=self.button_width, height=self.button_height)
            button.on_click = self._make_handler(i)
            self.buttons.append(button)
            self.layout.add(button)

        if self.options and not self._selected_index:
            self.set_selected(min(default_index, len(self.options) - 1), False)
        elif self.options and self._selected_index:
            self.set_selected(min(self._selected_index, len(self.options) - 1))
        self._update_visuals()

    def _update_visuals(self):
        selected_style = {
            'normal': {
                'font_size': self.font_size,
                'bg_color': arcade.color.DARK_BLUE_GRAY,
                'font_color': arcade.color.WHITE,
                'border_color': arcade.color.WHITE,
                'border_width': 2,
            },
            'hover': {
                'font_size': self.font_size,
                'bg_color': arcade.color.BLUE_GRAY,
                'font_color': arcade.color.WHITE,
                'border_color': arcade.color.WHITE,
                'border_width': 2,
            },
            'press': {
                'font_size': self.font_size,
                'bg_color': arcade.color.DARK_BLUE,
                'font_color': arcade.color.WHITE,
                'border_color': arcade.color.WHITE,
                'border_width': 2,
            },
        }

        normal_style = {
            'normal': {
                'font_size': self.font_size,
                'bg_color': arcade.color.GRAY,
                'font_color': arcade.color.BLACK,
                'border_color': arcade.color.BLACK,
                'border_width': 1,
            },
            'hover': {
                'font_size': self.font_size,
                'bg_color': arcade.color.LIGHT_GRAY,
                'font_color': arcade.color.BLACK,
                'border_color': arcade.color.BLACK,
                'border_width': 1,
            },
            'press': {
                'font_size': self.font_size,
                'bg_color': arcade.color.DARK_GRAY,
                'font_color': arcade.color.BLACK,
                'border_color': arcade.color.BLACK,
                'border_width': 1,
            },
        }

        for i, button in enumerate(self.buttons):
            button.style = selected_style if i == self._selected_index else normal_style

    @property
    def widget(self):
        return self.layout


@dataclass(eq=False)
class Player:
    id: int
    is_bot: bool
    is_alive: bool = True
    cities: list["City"] = field(default_factory=list, repr=False)
    stars: int = 3
    open_tech: TechTree = TechTree()

    def __post_init__(self):
        for city in self.cities:
            if city.owner != self:
                city.owner = self

    def __eq__(self, value):
        if isinstance(value, Player):
            return self.id == value.id
        return NotImplemented


@dataclass
class City:
    owner: Player | int
    level: int = 0
    population: int = 0
    tile: 'TileBase' = field(init=False, repr=False)

    def __post_init__(self):
        if self not in self.owner.cities:
            self.owner.cities.append(self)
