import arcade
from arcade.gui import UIManager, UITextureButton
from unitclasses import Rider, Archer, Defender
from terrain.terrain_classes import Mountain, GoldMountain, Animal, Forest, Fish, Fruits
import math
from pyglet.graphics import Batch


CENTER_RADIUS = 90
TECH_SPACING = 120
TECH_SIZE = 72
ICON_SCALE = 0.7
RESOURCE_SIZE = 20
RESOURCE_SPACING = 6


class TechTree:
    tech_tree_map = ((Mountain, GoldMountain), (Rider, Archer), (Fruits, Defender), (Animal, Forest), (Fish,))
    techs = (Mountain, GoldMountain, Rider, Archer, Fruits, Defender, Animal, Forest, Fish)

    def __init__(self, tech_map=None):
        self.__tech_map = tech_map or [False, False, False, False, False, False, False, False, False]
        self.tech_map = {cls: flag for cls, flag in zip(self.techs, self.__tech_map)}

    def set_tech_map(self, cls):
        self.tech_map[cls] = True
        self.__tech_map[self.techs.index(cls)] = True

    def __repr__(self):
        return f'TechTree({self.__tech_map})'


class DiscoveryView(arcade.View):
    def __init__(self, parent: arcade.View):
        super().__init__(background_color=parent.background_color)

        self.parent = parent
        self.completed = arcade.load_texture('assets/misc/bgComplete.png')
        self.open = arcade.load_texture('assets/misc/techbg.png')
        self.hidden = arcade.load_texture('assets/misc/bgUnavailable.png')
        self.resource = arcade.load_texture("assets/misc/resource.png")
        self.batch = Batch()
        self.cost_labels: list[arcade.Text] = []

        self.manager = UIManager()

    def on_show_view(self):
        self.parent.manager.disable()
        self.manager.enable()
        self.build_tech_buttons()

    def on_hide_view(self):
        self.manager.disable()

    def on_draw(self):
        self.clear()
        self.cost_labels.clear()
        self.window.default_camera.use()

        tech_tree = self.parent.current_player.open_tech

        cx = self.window.width // 2
        cy = self.window.height // 2

        branches = TechTree.tech_tree_map
        branch_count = len(branches)

        for branch_index, branch in enumerate(branches):
            angle = 2 * math.pi * branch_index / branch_count
            dx = math.cos(angle)
            dy = math.sin(angle)

            for depth, cls in enumerate(branch):
                state = get_tech_state(branch, depth, tech_tree)

                r = CENTER_RADIUS + depth * TECH_SPACING
                x = cx + dx * r
                y = cy + dy * r

                if state == "completed":
                    bg = self.completed
                elif state == "open":
                    bg = self.open
                else:
                    bg = self.hidden

                draw_centered_texture(bg, x, y, TECH_SIZE, TECH_SIZE)

                if depth > 0:
                    prev_r = CENTER_RADIUS + (depth - 1) * TECH_SPACING
                    px = cx + dx * prev_r
                    py = cy + dy * prev_r
                    arcade.draw_line(px, py, x, y, arcade.color.GRAY, 2)

                if state in ("open", "completed"):
                    draw_tech_textures(cls, x, y, TECH_SIZE * ICON_SCALE)

                    cost = 4 if depth == 0 else 5

                    label = arcade.Text(
                        text=str(cost),
                        font_name='Arial',
                        font_size=14,
                        color=arcade.color.BLACK,
                        x=int(x),
                        y=int(y - TECH_SIZE / 2 - 22),
                        anchor_x='center',
                        anchor_y='center',
                        batch=self.batch,
                    )

                    self.cost_labels.append(label)

        self.batch.draw()

    def build_tech_buttons(self):
        self.manager.clear()

        tech_tree = self.parent.current_player.open_tech
        cx = self.window.width // 2
        cy = self.window.height // 2

        branches = TechTree.tech_tree_map
        branch_count = len(branches)

        for branch_index, branch in enumerate(branches):
            angle = 2 * math.pi * branch_index / branch_count
            dx = math.cos(angle)
            dy = math.sin(angle)

            for depth, cls in enumerate(branch):
                state = get_tech_state(branch, depth, tech_tree)

                r = CENTER_RADIUS + depth * TECH_SPACING
                x = cx + dx * r
                y = cy + dy * r

                if state == "completed":
                    tex = self.completed
                elif state == "open":
                    tex = self.open
                else:
                    tex = self.hidden

                button = UITextureButton(
                    texture=tex, x=int(x - TECH_SIZE / 2), y=int(y - TECH_SIZE / 2), width=TECH_SIZE, height=TECH_SIZE
                )
                def make_handler(tech_cls=cls):
                    def on_click(event):
                        print(tech_cls)
                        cost = 4 if depth == 0 else 5
                        if self.parent.current_player.stars < cost or self.parent.current_player.open_tech.tech_map[tech_cls]:
                            return
                        self.parent.current_player.stars -= cost
                        self.parent.current_player.open_tech.set_tech_map(tech_cls)
                        self.build_tech_buttons()
                        self.parent.update_sprites()

                    return on_click

                button.on_click = make_handler()
                self.manager.add(button)

    def on_key_press(self, key, modifiers):
        if key == arcade.key.ESCAPE:
            self.window.show_view(self.parent)


def get_tech_state(branch, index, tech_tree: TechTree):
    tech = branch[index]

    if tech_tree.tech_map.get(tech, False):
        return "completed"

    if index == 0:
        return "open"

    prev = branch[index - 1]
    if tech_tree.tech_map.get(prev, False):
        return "open"

    return "hidden"


def draw_centered_texture(texture, x, y, max_w, max_h):
    tw, th = texture.width, texture.height
    scale = min(max_w / tw, max_h / th)

    w = tw * scale
    h = th * scale

    rect = arcade.rect.LBWH(x - w / 2, y - h / 2, w, h)
    arcade.draw_texture_rect(texture, rect)


def draw_tech_textures(cls, x, y, size):
    """
    Draws tech icon(s) depending on cls.textures structure.
    """
    if isinstance(cls.textures, tuple):
        count = len(cls.textures)
        offset = size * 0.15

        for i, tex_wrapper in enumerate(cls.textures):
            ox = (i - (count - 1) / 2) * offset
            draw_centered_texture(tex_wrapper.texture, x + ox, y, size, size)
    else:
        draw_centered_texture(cls.textures.ally, x, y, size, size)
