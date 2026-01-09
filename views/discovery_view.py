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
ZOOM_SPEED = 0.1
MIN_ZOOM = 0.3
MAX_ZOOM = 3.0


class TechTree:
    tech_tree_map = (
        (Mountain, GoldMountain),
        (Rider, Archer),
        (Fruits, Defender),
        (Animal, Forest),
        (Fish,),
    )

    techs = (
        Mountain, GoldMountain,
        Rider, Archer,
        Fruits, Defender,
        Animal, Forest,
        Fish,
    )

    def __init__(self, tech_map=None):
        self.__tech_map = tech_map or [False] * len(self.techs)
        self.tech_map = {cls: flag for cls, flag in zip(self.techs, self.__tech_map)}

    def set_tech_map(self, cls):
        self.tech_map[cls] = True
        self.__tech_map[self.techs.index(cls)] = True

    def __repr__(self):
        return f"TechTree({self.__tech_map})"


class DiscoveryView(arcade.View):
    def __init__(self, parent: arcade.View):
        super().__init__(background_color=parent.background_color)

        self.parent = parent

        self.completed = arcade.load_texture("assets/misc/bgComplete.png")
        self.open = arcade.load_texture("assets/misc/techbg.png")
        self.hidden = arcade.load_texture("assets/misc/bgUnavailable.png")

        self.batch = Batch()
        self.cost_labels: list[arcade.Text] = []

        self.zoom = 1.0
        self.offset_x = 0
        self.offset_y = 0

        self.tech_elements = []
        self.line_elements = []

        self.manager = UIManager()

    def on_show_view(self):
        self.parent.manager.disable()
        self.manager.enable()
        self.rebuild()

    def on_hide_view(self):
        self.manager.disable()


    def apply_transform(self, x, y):
        cx = self.window.width / 2
        cy = self.window.height / 2
        return (
            cx + (x - cx + self.offset_x) * self.zoom,
            cy + (y - cy + self.offset_y) * self.zoom,
        )

    def inverse_transform(self, x, y):
        cx = self.window.width / 2
        cy = self.window.height / 2
        return (
            (x - cx) / self.zoom + cx - self.offset_x,
            (y - cy) / self.zoom + cy - self.offset_y,
        )


    def rebuild(self):
        self.create_tech_elements()
        self.build_tech_buttons()

    def create_tech_elements(self):
        self.tech_elements.clear()
        self.line_elements.clear()

        tech_tree = self.parent.current_player.open_tech
        cx = self.window.width // 2
        cy = self.window.height // 2

        branches = TechTree.tech_tree_map

        for branch_index, branch in enumerate(branches):
            angle = 2 * math.pi * branch_index / len(branches)
            dx, dy = math.cos(angle), math.sin(angle)

            for depth, cls in enumerate(branch):
                state = get_tech_state(branch, depth, tech_tree)

                r = CENTER_RADIUS + depth * TECH_SPACING
                x = cx + dx * r
                y = cy + dy * r

                bg = (
                    self.completed if state == "completed"
                    else self.open if state == "open"
                    else self.hidden
                )

                self.tech_elements.append({
                    "x": x,
                    "y": y,
                    "cls": cls,
                    "depth": depth,
                    "state": state,
                    "texture": bg,
                })

                if depth > 0:
                    pr = CENTER_RADIUS + (depth - 1) * TECH_SPACING
                    self.line_elements.append({
                        "x1": cx + dx * pr,
                        "y1": cy + dy * pr,
                        "x2": x,
                        "y2": y,
                    })

    def build_tech_buttons(self):
        self.manager.clear()

        for element in self.tech_elements:
            if element["state"] == "hidden":
                continue

            x, y = self.apply_transform(element["x"], element["y"])
            size = TECH_SIZE * self.zoom
            cls = element["cls"]
            depth = element["depth"]
            texture = element["texture"]

            button = UITextureButton(
                texture=texture,
                x=int(x - size / 2),
                y=int(y - size / 2),
                width=int(size),
                height=int(size),
            )

            def make_handler(tech_cls=cls, tech_depth=depth):
                def on_click(event):
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

    def on_draw(self):
        self.clear()
        self.cost_labels.clear()
        self.manager.draw()

        for line in self.line_elements:
            x1, y1 = self.apply_transform(line["x1"], line["y1"])
            x2, y2 = self.apply_transform(line["x2"], line["y2"])
            arcade.draw_line(x1, y1, x2, y2, arcade.color.GRAY, 2)

        for element in self.tech_elements:
            x, y = self.apply_transform(element["x"], element["y"])
            size = TECH_SIZE * self.zoom

            draw_centered_texture(element["texture"], x, y, size, size)

            if element["state"] in ("open", "completed"):
                draw_tech_textures(
                    element["cls"],
                    x,
                    y,
                    size * ICON_SCALE
                )

                cost = 4 if element["depth"] == 0 else 5
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


    def on_key_press(self, key, modifiers):
        if key == arcade.key.ESCAPE:
            self.window.show_view(self.parent)


def get_tech_state(branch, index, tech_tree: TechTree):
    tech = branch[index]

    if tech_tree.tech_map.get(tech):
        return "completed"
    if index == 0:
        return "open"

    prev = branch[index - 1]
    if tech_tree.tech_map.get(prev):
        return "open"

    return "hidden"


def draw_centered_texture(texture, x, y, max_w, max_h):
    scale = min(max_w / texture.width, max_h / texture.height)
    w = texture.width * scale
    h = texture.height * scale
    rect = arcade.rect.LBWH(x - w / 2, y - h / 2, w, h)
    arcade.draw_texture_rect(texture, rect)


def draw_tech_textures(cls, x, y, size):
    """ Draws tech icon(s) depending on cls.textures structure. """
    if isinstance(cls.textures, tuple):
        count = len(cls.textures)
        offset = size * 0.15

        for i, tex_wrapper in enumerate(cls.textures):
            ox = (i - (count - 1) / 2) * offset
            draw_centered_texture(
                tex_wrapper.texture,
                x + ox,
                y,
                size,
                size
            )
    else:
        draw_centered_texture(
            cls.textures.ally,
            x,
            y,
            size,
            size
        )