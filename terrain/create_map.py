from random import choices, randint
from terrain.terrain_classes import Tile, TERRAIN_TYPES, TileBase
from classes import Player, City


def create_map(side: int, players: list[Player]):
    print(players)
    map: list[list[TileBase]] = []
    for x in range(side):
        map.append([])
        for y in range(side):
            if x == 0 or y == 0:
                map[x].append(Tile(0, len(players)))
                continue
            map[x].append(Tile(choices(list(TERRAIN_TYPES.keys()), (el.weight for el in TERRAIN_TYPES.values()), k=1)[0], len(players)))
    
    for player in players:
        while True:
            x, y = randint(2, side - 3), randint(2, side - 3)
            if any(map[i][j].city for j in range(y - 2, y + 3) for i in range(x - 2, x + 3)):
                continue
            map[x][y] = Tile(0, len(players), modifier=False)
            map[x][y].city = City(player)
            print(x, y)
            break
    return map