import random

WIDTH = 10
HEIGHT = 10
CHANCE_WATER = 20
CHANCE_MOUNTAINS = 10
CHANCE_LAND = 70

def create_map(width, height):
    map = []
    terrain_type = None
    """
    1 - суша
    2 - вода
    3 - гора
    """
    for x in range(width):
        map.append([])
        for y in range(height):
            random_number = random.randint(1, 100)
            
            if random_number <= CHANCE_WATER:
                terrain_type = 2
            elif random_number <= CHANCE_WATER + CHANCE_MOUNTAINS:
                terrain_type = 3
            else:
                terrain_type = 1
                
            map[x].append(terrain_type)
    return map


game_map = create_map(WIDTH, HEIGHT)

for x in range(WIDTH):
    for y in range(HEIGHT):
        if game_map[x][y] == 3:
            print("^", end=" ")
        elif game_map[x][y] == 2:
            print("~", end=" ")
        else:
            print(".", end=" ")
    print()