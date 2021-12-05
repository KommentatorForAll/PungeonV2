from typing import List

from arcade import SpriteList, PymunkPhysicsEngine

from blocks import Tile, Floor, Wall


class Room:
    def __init__(self):
        self.tiles: List[List[Tile]] = \
            [
                [
                    Floor('./assets/imgs/map/tiles/tile_ground1.png', scale=4)
                    if i != 0 and i != 9 and j != 0 and j != 9 else Wall('assets/imgs/map/wall/wall1.png', scale=4)
                    for i in range(10)
                ] for j in range(10)
            ]

    def load(self, x: int, y: int, map_list: SpriteList, physics_engine: PymunkPhysicsEngine):
        for offset_x in range(len(self.tiles)):
            for offset_y in range(len(self.tiles[0])):
                tile = self.tiles[offset_x][offset_y]
                tile.add_to_list(map_list, physics_engine, x+(64*offset_x), y+(64*offset_y))

