from random import choices, randint
from terrain.terrain_classes import *
from classes import Player, City


def create_map(side: int, players: list[Player]):
    map: list[list[TileBase]] = []
    villages: list[tuple[int, int]] = []
    for x in range(side):
        map.append([])
        for y in range(side):
            if x == 0 or y == 0:
                map[x].append(Tile(Land, len(players)))
                continue
            terrain_type = choices(TERRAIN_TYPES, terrain_types_weights(), k=1)[0]
            if terrain_type == Land:
                modifier_type = choices(LAND_MODIFIERS, land_modifiers_weights(), k=1)[0]
                map[x].append(Tile(Land, len(players), modifier=modifier_type))
                if modifier_type == Village:
                    villages.append((x, y))
            elif terrain_type == Water:
                modifier_type = choices(WATER_MODIFIERS, water_modifiers_weights(), k=1)[0]
                map[x].append(Tile(Water, len(players), modifier=modifier_type))

    for player in players:
        while True:
            flag = True
            x, y = randint(2, side - 3), randint(2, side - 3)
            for i in range(x - 2, x + 3):
                for j in range(y - 2, y + 3):
                    if map[i][j].city:
                        flag = False
                        break
                    if map[i][j].modifier == Village:
                        map[i][j] = Tile(Land, len(players))
                if not flag:
                    break
            if not flag:
                continue
            map[x][y] = Tile(Land, len(players), city=City(player))
            print(x, y)
            break

    for x, y in villages:
        if map[x][y].modifier != Village or not (1 <= x <= side - 2 and 1 <= y <= side - 2):
            map[x][y].modifier = None
            continue
        flag = True
        for i in range(x - 2, x + 3):
            for j in range(y - 2, y + 3):
                if not 0 <= i < side or not 0 <= j < side or (i, j) == (x, y):
                    continue
                if map[i][j].city:
                    flag = False
                    break
                if map[i][j].modifier == Village:
                    map[i][j].modifier = None
            if not flag:
                break

    return map
