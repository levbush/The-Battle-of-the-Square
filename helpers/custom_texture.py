from arcade import load_texture


class CustomTexture:
    'Class for storing textures and simultaneously having the property `eval(repr(self)) == self` for storing'

    def __init__(self, path):
        self.path = path
        self.texture = load_texture(path)

    def __repr__(self):
        return f'CustomTexture("{self.path}")'