from random import choices
from terrain.terrain_classes import Tile, TERRAIN_TYPES, TileBase


def create_map(width: int, height: int, player_count: int):
    map: list[list[TileBase]] = []
    for x in range(width):
        map.append([])
        for _ in range(height):
            map[x].append(Tile(choices(list(TERRAIN_TYPES.keys()), (el.weight for el in TERRAIN_TYPES.values()), k=1)[0], player_count))
    return map


game_map = create_map(10, 10, 2)

for row in game_map:
    for tile in row:
        # print(tile, end=' ')
        print(repr(tile), end=' ')
    print()