from random import choices
# from terrain.terrain_classes import Tile, TERRAIN_TYPES, TileBase
from terrain.terrain_classes import Tile, TERRAIN_TYPES, TileBase


WIDTH = 10
HEIGHT = 10



def create_map(width, height):
    map: list[list[TileBase]] = []
    for x in range(width):
        map.append([])
        for _ in range(height):
            map[x].append(Tile(choices(list(TERRAIN_TYPES.keys()), (el.weight for el in TERRAIN_TYPES.values()), k=1)[0]))
    return map


game_map = create_map(WIDTH, HEIGHT)

for x in range(WIDTH):
    for y in range(HEIGHT):
        print(game_map[x][y], end=' ')
    print()