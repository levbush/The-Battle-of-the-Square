import arcade
import math
from arcade.gui import UIManager, UITextureButton
from helpers.unit_classes import Rider, Archer, Defender, UnitBase
from helpers.terrain.terrain_classes import Mountain, GoldMountain, Animal, Forest, Fish, Fruits, ModifierBase
from pyglet.graphics import Batch
from collections import namedtuple

if __name__ == '__main__':
    from views.game_view import GameView
    from helpers.classes import Player

CENTER_RADIUS = 90
TECH_SPACING = 120
TECH_SIZE = 72
ICON_SCALE = 0.7

ZOOM_SPEED = 0.1
MIN_ZOOM = 0.3
MAX_ZOOM = 3.0


TechElement = namedtuple('TechElement', ['x', 'y', 'cls', 'depth', 'state', 'texture'])

LineElement = namedtuple('LineElement', ['x1', 'y1', 'x2', 'y2'])


class TechTree:
    '''Defines the discoveries and stores the progress'''

    tech_tree_map: tuple[tuple[type[ModifierBase | UnitBase], ...], ...] = (
        (Mountain, GoldMountain),
        (Rider, Archer),
        (Fruits, Defender),
        (Animal, Forest),
        (Fish,),
    )

    techs: tuple[type[ModifierBase | UnitBase], ...] = (Mountain, GoldMountain, Rider, Archer, Fruits, Defender, Animal, Forest, Fish)

    def __init__(self, tech_map: list[bool] | None = None) -> None:
        self.__tech_map: list[bool] = tech_map or [False] * len(self.techs)
        self.tech_map: dict[type, bool] = {cls: flag for cls, flag in zip(self.techs, self.__tech_map)}

    def set_tech_map(self, cls: type) -> None:
        self.tech_map[cls] = True
        self.__tech_map[self.techs.index(cls)] = True

    def __repr__(self) -> str:
        return f'TechTree({self.__tech_map})'


class DiscoveryView(arcade.View):
    '''View for accessing the discoveries'''

    def __init__(self, parent: 'GameView') -> None:
        super().__init__(background_color=parent.background_color)

        self.parent = parent

        self.completed = arcade.load_texture('assets/misc/bgComplete.png')
        self.open = arcade.load_texture('assets/misc/techbg.png')
        self.hidden = arcade.load_texture('assets/misc/bgUnavailable.png')

        self.batch: Batch = Batch()
        self.cost_labels: list[arcade.Text] = []

        self.zoom: float = 1.0
        self.offset_x: float = 0.0
        self.offset_y: float = 0.0

        self.tech_elements: list[TechElement] = []
        self.line_elements: list[LineElement] = []

        self.manager: UIManager = UIManager()

    def apply_transform(self, x: float, y: float) -> tuple[float, float]:
        '''Apply zoom and offset to world coordinates'''
        cx = self.window.width / 2
        cy = self.window.height / 2
        return (cx + (x - cx + self.offset_x) * self.zoom, cy + (y - cy + self.offset_y) * self.zoom)

    def inverse_transform(self, x: float, y: float) -> tuple[float, float]:
        '''Inverse of apply_transform'''
        cx = self.window.width / 2
        cy = self.window.height / 2
        return ((x - cx) / self.zoom + cx - self.offset_x, (y - cy) / self.zoom + cy - self.offset_y)

    def rebuild(self) -> None:
        '''Rebuild visual elements'''
        self.create_tech_elements()
        self.build_tech_buttons()

    def create_tech_elements(self) -> None:
        '''Create tech and line elements'''
        self.tech_elements.clear()
        self.line_elements.clear()

        tech_tree: TechTree = self.parent.current_player.open_tech
        cx = self.window.width // 2
        cy = self.window.height // 2

        for branch_index, branch in enumerate(TechTree.tech_tree_map):
            angle = 2 * math.pi * branch_index / len(TechTree.tech_tree_map)
            dx, dy = math.cos(angle), math.sin(angle)

            for depth, cls in enumerate(branch):
                state = get_tech_state(branch, depth, tech_tree)
                r = CENTER_RADIUS + depth * TECH_SPACING
                x = cx + dx * r
                y = cy + dy * r

                bg = self.completed if state == 'completed' else self.open if state == 'open' else self.hidden

                self.tech_elements.append(TechElement(x, y, cls, depth, state, bg))

                if depth > 0:
                    pr = CENTER_RADIUS + (depth - 1) * TECH_SPACING
                    self.line_elements.append(LineElement(cx + dx * pr, cy + dy * pr, x, y))

    def build_tech_buttons(self) -> None:
        '''Create UI buttons'''
        self.manager.clear()

        for element in self.tech_elements:
            if element.state == 'hidden':
                continue

            x, y = self.apply_transform(element.x, element.y)
            size = TECH_SIZE * self.zoom

            button = UITextureButton(
                texture=element.texture, x=int(x - size / 2), y=int(y - size / 2), width=int(size), height=int(size)
            )

            def make_handler(tech_cls: type = element.cls, tech_depth: int = element.depth):
                def on_click(event) -> None:
                    cost = 4 if tech_depth == 0 else 5
                    player = self.parent.current_player

                    if player.stars < cost:
                        return
                    if player.open_tech.tech_map.get(tech_cls):
                        return

                    player.stars -= cost
                    player.open_tech.set_tech_map(tech_cls)
                    self.rebuild()
                    self.parent.update_sprites()

                return on_click

            button.on_click = make_handler()
            self.manager.add(button)

    def on_show_view(self):
        self.parent.manager.disable()
        self.manager.enable()
        self.rebuild()

    def on_hide_view(self):
        self.manager.disable()

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        old_zoom = self.zoom

        if scroll_y > 0:
            self.zoom = min(self.zoom * (1 + ZOOM_SPEED), MAX_ZOOM)
        elif scroll_y < 0:
            self.zoom = max(self.zoom * (1 - ZOOM_SPEED), MIN_ZOOM)

        if self.zoom == old_zoom:
            return

        world_x, world_y = self.inverse_transform(x, y)
        new_x, new_y = self.apply_transform(world_x, world_y)

        self.offset_x += (x - new_x) / self.zoom
        self.offset_y += (y - new_y) / self.zoom

        self.build_tech_buttons()

    def on_key_press(self, key, modifiers):
        if key == arcade.key.ESCAPE:
            self.window.show_view(self.parent)

        if key == arcade.key.H:
            self.window.show_view(self.parent)

    def on_draw(self):
        self.clear()
        self.cost_labels.clear()
        self.manager.draw()

        for line in self.line_elements:
            x1, y1 = self.apply_transform(line.x1, line.y1)
            x2, y2 = self.apply_transform(line.x2, line.y2)
            arcade.draw_line(x1, y1, x2, y2, arcade.color.GRAY, 2)

        for element in self.tech_elements:
            x, y = self.apply_transform(element.x, element.y)
            size = TECH_SIZE * self.zoom

            draw_centered_texture(element.texture, x, y, size, size)

            if element.state in ("open", "completed"):
                draw_tech_textures(
                    element.cls,
                    x,
                    y,
                    size * ICON_SCALE,
                    self.parent.current_player
                )

                cost = 4 if element.depth == 0 else 5
                label = arcade.Text(
                    text=str(cost),
                    font_size=14,
                    color=arcade.color.BLACK,
                    x=int(x),
                    y=int(y - size / 2 - 22),
                    anchor_x="center",
                    anchor_y="center",
                    batch=self.batch,
                )
                self.cost_labels.append(label)

        self.batch.draw()


def get_tech_state(branch: tuple[type, ...], index: int, tech_tree: TechTree) -> str:
    '''Return tech state: completed, open or hidden'''
    tech = branch[index]

    if tech_tree.tech_map.get(tech):
        return 'completed'
    if index == 0:
        return 'open'

    prev = branch[index - 1]
    if tech_tree.tech_map.get(prev):
        return 'open'

    return 'hidden'


def draw_centered_texture(texture: arcade.Texture, x: float, y: float, max_w: float, max_h: float) -> None:
    '''Draw a texture centered and scaled'''
    scale = min(max_w / texture.width, max_h / texture.height)
    w = texture.width * scale
    h = texture.height * scale
    rect = arcade.rect.LBWH(x - w / 2, y - h / 2, w, h)
    arcade.draw_texture_rect(texture, rect)


def draw_tech_textures(cls: type, x: float, y: float, size: float, player: 'Player') -> None:
    '''Draw tech icon depending on class type'''
    if issubclass(cls, ModifierBase):
        count = len(cls.textures)
        offset = size * 0.15

        for i, tex_wrapper in enumerate(cls.textures[::-1]):
            ox = (i - (count - 1) / 2) * offset
            if cls == GoldMountain and i == 1:
                draw_centered_texture(tex_wrapper.texture, x + ox - size / 7.5, y, size / 2.5, size / 2.5)
                continue
            draw_centered_texture(tex_wrapper.texture, x + ox, y, size, size)
        return

    if issubclass(cls, UnitBase):
        draw_centered_texture(cls(player, (-1, -1)).texture.texture, x, y, size * 2, size * 2)
        return

    raise TypeError(f'Accepts only ModifierBase and UnitBase subclasses, given: {cls}')
