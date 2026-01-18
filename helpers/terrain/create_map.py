from random import choices, randint
from helpers.terrain.terrain_classes import *
from helpers.classes import Player, City
from helpers.unit_classes import Unit, UnitType


def create_map(side: int, players: list[Player]):
    '''Create randomly filled game map'''

    map: list[list[TileBase]] = []
    villages: list[tuple[int, int]] = []
    for x in range(side):
        map.append([])
        for y in range(side):
            if x == 0 or y == 0:
                map[x].append(Tile(x, y, TerrainType.LAND, [False] * len(players)))
                continue
            terrain_type = choices(list(TERRAIN_TYPES.keys()), terrain_types_weights(), k=1)[0]

            if terrain_type == TerrainType.LAND:
                modifier_type = choices(LAND_MODIFIERS, land_modifiers_weights(), k=1)[0]()
                map[x].append(Tile(x, y, TerrainType.LAND, [False] * len(players), modifier=modifier_type))
                if modifier_type and modifier_type.type == ModifierType.VILLAGE:  # We need to take into account that villages and towns can't intersect with each other.
                    villages.append((x, y))
            
            elif terrain_type == TerrainType.WATER:
                modifier_type = choices(WATER_MODIFIERS, water_modifiers_weights(), k=1)[0]()
                map[x].append(Tile(x, y, TerrainType.WATER, [False] * len(players), modifier=modifier_type))

            else:
                raise ValueError(f'Invalid terrain type: {terrain_type}')

    for player in players:
        visible_tiles: list[tuple[int, ...]] = []
        while True:  # Creating a capital for each player
            flag = True
            x, y = randint(2, side - 3), randint(2, side - 3)
            for i in range(x - 2, x + 3):
                for j in range(y - 2, y + 3):
                    if x - 2 <= i <= x + 2 and y - 2 <= j <= y + 2:
                        visible_tiles.append((i, j))
                    if map[i][j].city:
                        flag = False
                        visible_tiles.clear()
                        break
                    if map[i][j].modifier and map[i][j].modifier.type == ModifierType.VILLAGE:
                        map[i][j] = Tile(i, j, TerrainType.LAND, [False] * len(players))
                if not flag:
                    break
            if not flag:
                continue
            for i, j in visible_tiles:
                map[i][j].visible_mapping[player.id] = True
            vm = map[x][y].visible_mapping[:]
            vm[player.id] = True
            city = City(player)
            map[x][y] = Tile(x, y, TerrainType.LAND, vm, city=city, unit=Unit(UnitType.ARCHER, player, x, y))
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    map[x + dx][y + dy].owner = city
            break

    for x, y in villages:  # Deleting overlapping villages
        if map[x][y].modifier and map[x][y].modifier.type != ModifierType.VILLAGE or not (1 <= x <= side - 2 and 1 <= y <= side - 2):
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
                if map[i][j].modifier and map[i][j].modifier.type == ModifierType.VILLAGE:
                    map[i][j].modifier = None
            if not flag:
                break

    return map
