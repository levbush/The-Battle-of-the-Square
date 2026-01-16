from helpers.classes import Player
from helpers.terrain.terrain_classes import TileBase
from helpers.unit_classes import UnitBase, Unit, UNIT_TYPES
from typing import Literal
from random import choices, randint
from math import dist


class BotLogic:
    def __init__(self, map: list[list[TileBase]], current_player: Player, difficulty: Literal[0, 1]):
        self.map = map
        self.current_player = current_player
        self.difficulty = difficulty
    
    def move(self):
        visible_cities: list[TileBase] = []
        visible_units: list[TileBase] = []
        subordinate_units: list[TileBase] = []
        fog: list[TileBase] = []

        for row in self.map:
            for tile in row:
                if not tile.visible_mapping[self.current_player.id]:
                    fog.append(tile)
                    continue
                if tile.city and tile.city.owner != self.current_player:
                    visible_cities.append(tile)
                if tile.unit:
                    if tile.unit.owner != self.current_player:
                        visible_units.append(tile)
                    else:
                        subordinate_units.append(tile)
        
        for tile in subordinate_units:
            unit = tile.unit
            target = self.get_priority_target(unit, visible_cities, visible_units, fog)
            if (target.row, target.col) == unit.pos:
                # capture
                continue
            if target.unit and target.unit.owner != self.current_player:
                if self.is_in_unit_range(unit, target):
                    # attack
                    print('attack', target.unit)
                    continue
            self.move_towards(unit, target)

        for city in self.current_player.cities:
            if choices([0, 1], [50, 50 + 30 * self.difficulty], k=1)[0]:
                if not city.tile.unit:
                    city.tile.unit = Unit(randint(0, len(UNIT_TYPES) - 1), self.current_player, city.tile.row, city.tile.col)

            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    if (modifier := self.map[city.tile.row + dx][city.tile.col + dy].modifier) and modifier.cost and not modifier.is_collected:
                        if choices([0, 1], [20, 10 + 15 * self.difficulty], k=1)[0]:
                            modifier.collect()
                            city.tile.add_population_to_city(modifier.population)

    def move_towards(self, unit: UnitBase, target: TileBase):
        x1, y1, x2, y2 = *unit.pos, target.row, target.col
        dx, dy = (x2 - x1) / abs(x2 - x1) if x2 != x1 else 0, (y2 - y1) / abs(y2 - y1) if y2 != y1 else 0
        dx, dy = int(dx), int(dy)
        # TODO: implement correct movement
        if choices([0, 1], [50 - 50 * self.difficulty, 100], k=1)[0]:
            unit.move((x1 + dx, y1 + dy))
            self.map[x1][y1].unit = None
            self.map[x1 + dx][y1 + dy].unit = unit

    def get_priority_target(self, unit: UnitBase, visible_cities: list[TileBase], visible_units: list[TileBase], fog: list[TileBase]):
        for city in self.current_player.cities:
            if city.tile in visible_units:
                if self.is_in_unit_range(unit, city.tile):
                    return city.tile
                
        if visible_cities or visible_units:
            return min(visible_cities + visible_units, key=lambda x: dist(unit.pos, (x.row, x.col)))
        fog_target =  min(fog, key=lambda x: dist(unit.pos, (x.row, x.col)))
        # visible_neighbors: list[TileBase] = []
        # for dx in (-1, 0, 1):
        #     for dy in (-1, 0, 1):
        #         if (tile := self.map[fog_target.row + dx][fog_target.col + dy]).visible_mapping[self.current_player.id]: visible_neighbors.append(tile)
        # return min(visible_neighbors, key=lambda x: dist(unit.pos, (x.row, x.col)))
        return fog_target

    def is_in_unit_range(self, unit: UnitBase, tile: TileBase):
        return abs(tile.row - unit.pos[0]) <= unit.range and abs(tile.row - unit.pos[1]) <= unit.range