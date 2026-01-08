from random import choices, randint
from terrain.terrain_classes import *
from classes import Player, City
from unitclasses import Unit


def create_map(side: int, players: list[Player]):
    map: list[list[TileBase]] = []
    villages: list[tuple[int, int]] = []
    for x in range(side):
        map.append([])
        for y in range(side):
            if x == 0 or y == 0:
                map[x].append(Tile(x, y, Land, [False] * len(players)))
                continue
            terrain_type = choices(TERRAIN_TYPES, terrain_types_weights(), k=1)[0]
            if terrain_type == Land:
                modifier_type = choices(LAND_MODIFIERS, land_modifiers_weights(), k=1)[0]()
                map[x].append(Tile(x, y, Land, [False] * len(players), modifier=modifier_type))
                if modifier_type.__class__ == Village:
                    villages.append((x, y))
            elif terrain_type == Water:
                modifier_type = choices(WATER_MODIFIERS, water_modifiers_weights(), k=1)[0]()
                map[x].append(Tile(x, y, Water, [False] * len(players), modifier=modifier_type))
    
    for player in players:
        visible_tiles: list[tuple[int]] = []
        while True:
            flag = True
            x, y = randint(2, side - 3), randint(2, side - 3)
            for i in range(x - 2, x + 3):
                for j in range(y - 2, y + 3):
                    if x - 2 <= i <= x + 2 and y - 2 <= j <= y + 2: visible_tiles.append((i, j))
                    if map[i][j].city:
                        flag = False
                        visible_tiles.clear()
                        break
                    if map[i][j].modifier.__class__ == Village:
                        map[i][j] = Tile(i, j, Land, [False] * len(players))
                if not flag:
                    break
            if not flag:
                continue
            for (i, j) in visible_tiles:
                j: int
                map[i][j].visible_mapping[player.id] = True
            vm = map[x][y].visible_mapping[:]
            vm[player.id] = True
            city = City(player)
            map[x][y] = Tile(x, y, Land, vm, city=city, unit=Unit(0, player, x, y))
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    map[x + dx][y + dy].owner = city
            break

    for x, y in villages:
        if map[x][y].modifier.__class__ != Village or not (1 <= x <= side - 2 and 1 <= y <= side - 2):
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
                if map[i][j].modifier.__class__ == Village:
                    map[i][j].modifier = None
            if not flag:
                break

    return map
