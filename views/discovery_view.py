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
ZOOM_SPEED = 0.1
MIN_ZOOM = 0.3
MAX_ZOOM = 3.0


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
        
        self.zoom = 1.0
        self.offset_x = 0
        self.offset_y = 0
        self.panning = False
        self.last_mouse_pos = (0, 0)
        
        self.tech_elements = []
        self.line_elements = []
        
        self.manager = UIManager()

    def on_show_view(self):
        self.parent.manager.disable()
        self.manager.enable()
        self.create_tech_elements()
        self.build_tech_buttons()
        
        self.zoom = 1.0
        self.offset_x = 0
        self.offset_y = 0

    def on_hide_view(self):
        self.manager.disable()

    def create_tech_elements(self):
        self.tech_elements.clear()
        self.line_elements.clear()
        
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
                    bg_texture = self.completed
                elif state == "open":
                    bg_texture = self.open
                else:
                    bg_texture = self.hidden
                
                self.tech_elements.append({
                    'x': x, 'y': y, 
                    'texture': bg_texture,
                    'size': TECH_SIZE,
                    'type': 'background',
                    'cls': cls,
                    'state': state,
                    'depth': depth
                })
                
                if depth > 0:
                    prev_r = CENTER_RADIUS + (depth - 1) * TECH_SPACING
                    px = cx + dx * prev_r
                    py = cy + dy * prev_r
                    self.line_elements.append({
                        'x1': px, 'y1': py,
                        'x2': x, 'y2': y
                    })
                
                if state in ("open", "completed"):
                    self.add_tech_icon(cls, x, y, depth)

    def add_tech_icon(self, cls, x, y, depth):
        if isinstance(cls.textures, tuple):
            count = len(cls.textures)
            offset = TECH_SIZE * ICON_SCALE * 0.15
            
            for i, tex_wrapper in enumerate(cls.textures):
                ox = (i - (count - 1) / 2) * offset
                self.tech_elements.append({
                    'x': x + ox, 'y': y,
                    'texture': tex_wrapper.texture,
                    'size': TECH_SIZE * ICON_SCALE,
                    'type': 'icon',
                    'depth': depth
                })
        else:
            self.tech_elements.append({
                'x': x, 'y': y,
                'texture': cls.textures.ally,
                'size': TECH_SIZE * ICON_SCALE,
                'type': 'icon',
                'depth': depth
            })

    def apply_transform(self, x, y):
        center_x = self.window.width / 2
        center_y = self.window.height / 2
        
        tx = center_x + (x - center_x + self.offset_x) * self.zoom
        ty = center_y + (y - center_y + self.offset_y) * self.zoom
        
        return tx, ty

    def inverse_transform(self, x, y):
        center_x = self.window.width / 2
        center_y = self.window.height / 2
        
        tx = (x - center_x) / self.zoom + center_x - self.offset_x
        ty = (y - center_y) / self.zoom + center_y - self.offset_y
        
        return tx, ty

    def on_draw(self):
        self.clear()
        
        for line in self.line_elements:
            x1, y1 = self.apply_transform(line['x1'], line['y1'])
            x2, y2 = self.apply_transform(line['x2'], line['y2'])
            arcade.draw_line(x1, y1, x2, y2, arcade.color.GRAY, 2)
        
        for element in self.tech_elements:
            x, y = self.apply_transform(element['x'], element['y'])
            texture = element['texture']
            size = element['size'] * self.zoom
            
            width = size
            height = size * texture.height / texture.width
            
            rect = arcade.rect.LBWH(
                x - width / 2,
                y - height / 2,
                width,
                height
            )
            arcade.draw_texture_rect(texture, rect)
        
        self.draw_cost_labels()
        self.manager.draw()

    def draw_cost_labels(self):
        self.cost_labels.clear()
        
        for element in self.tech_elements:
            if element['type'] == 'background' and element['state'] in ("open", "completed"):
                x, y = self.apply_transform(element['x'], element['y'])
                depth = element['depth']
                
                cost = 4 if depth == 0 else 5
                size = TECH_SIZE * self.zoom
                
                label = arcade.Text(
                    text=str(cost),
                    font_name='Arial',
                    font_size=14,
                    color=arcade.color.BLACK,
                    x=int(x),
                    y=int(y - size / 2 - 22),
                    anchor_x='center',
                    anchor_y='center',
                    batch=self.batch,
                )
                self.cost_labels.append(label)
        
        self.batch.draw()

    def build_tech_buttons(self):
        self.manager.clear()
        
        for element in self.tech_elements:
            if element['type'] == 'background':
                cls = element['cls']
                depth = element['depth']
                state = element['state']
                
                if state == 'hidden':
                    continue
                
                x, y = self.apply_transform(element['x'], element['y'])
                button_size = TECH_SIZE * self.zoom
                
                button = UITextureButton(
                    x=int(x - button_size / 2),
                    y=int(y - button_size / 2),
                    width=int(button_size),
                    height=int(button_size),
                    texture=arcade.load_texture(":resources:gui_basic_assets/transparent.png")
                )
                
                def make_handler(tech_cls=cls, tech_depth=depth):
                    def on_click(event):
                        cost = 4 if tech_depth == 0 else 5
                        if (self.parent.current_player.stars >= cost and 
                            not self.parent.current_player.open_tech.tech_map.get(tech_cls, False)):
                            self.parent.current_player.stars -= cost
                            self.parent.current_player.open_tech.set_tech_map(tech_cls)
                            self.create_tech_elements()
                            self.build_tech_buttons()
                            self.parent.update_sprites()
                    
                    return on_click
                
                button.on_click = make_handler()
                self.manager.add(button)

    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int):
        if button == arcade.MOUSE_BUTTON_RIGHT:
            self.panning = True
            self.last_mouse_pos = (x, y)

    def on_mouse_release(self, x: int, y: int, button: int, modifiers: int):
        if button == arcade.MOUSE_BUTTON_RIGHT:
            self.panning = False

    def on_mouse_drag(self, x: int, y: int, dx: int, dy: int, buttons: int, modifiers: int):
        if buttons & arcade.MOUSE_BUTTON_RIGHT:
            self.offset_x += dx / self.zoom
            self.offset_y += dy / self.zoom
            self.build_tech_buttons()
        elif buttons & arcade.MOUSE_BUTTON_LEFT:
            self.offset_x += dx / self.zoom
            self.offset_y += dy / self.zoom
            self.build_tech_buttons()

    def on_mouse_scroll(self, x: int, y: int, scroll_x: int, scroll_y: int):
        old_zoom = self.zoom
        
        if scroll_y > 0:
            self.zoom = min(self.zoom * 1.1, MAX_ZOOM)
        else:
            self.zoom = max(self.zoom / 1.1, MIN_ZOOM)
        
        if old_zoom != self.zoom:
            world_x, world_y = self.inverse_transform(x, y)
            center_x = self.window.width / 2
            center_y = self.window.height / 2
            
            self.offset_x = (world_x - center_x) * (1 - self.zoom / old_zoom) + self.offset_x * (self.zoom / old_zoom)
            self.offset_y = (world_y - center_y) * (1 - self.zoom / old_zoom) + self.offset_y * (self.zoom / old_zoom)
            
            self.build_tech_buttons()

    def on_key_press(self, key, modifiers):
        if key == arcade.key.ESCAPE or key == arcade.key.H:
            self.window.show_view(self.parent)
        elif key == arcade.key.R:
            self.zoom = 1.0
            self.offset_x = 0
            self.offset_y = 0
            self.build_tech_buttons()
        elif key == arcade.key.EQUAL or key == arcade.key.PLUS:
            self.zoom = min(self.zoom * 1.1, MAX_ZOOM)
            self.build_tech_buttons()
        elif key == arcade.key.MINUS:
            self.zoom = max(self.zoom / 1.1, MIN_ZOOM)
            self.build_tech_buttons()
        elif key == arcade.key.UP:
            self.offset_y -= 20 / self.zoom
            self.build_tech_buttons()
        elif key == arcade.key.DOWN:
            self.offset_y += 20 / self.zoom
            self.build_tech_buttons()
        elif key == arcade.key.LEFT:
            self.offset_x += 20 / self.zoom
            self.build_tech_buttons()
        elif key == arcade.key.RIGHT:
            self.offset_x -= 20 / self.zoom
            self.build_tech_buttons()

    def on_update(self, delta_time: float):
        pass


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
    if isinstance(cls.textures, tuple):
        count = len(cls.textures)
        offset = size * 0.15

        for i, tex_wrapper in enumerate(cls.textures):
            ox = (i - (count - 1) / 2) * offset
            draw_centered_texture(tex_wrapper.texture, x + ox, y, size, size)
    else:
        draw_centered_texture(cls.textures.ally, x, y, size, size)
