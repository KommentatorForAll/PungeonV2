from typing import List, Tuple, Union
from uuid import uuid4

import numpy as np
import math
from arcade import SpriteList, PymunkPhysicsEngine, Sprite, Color, Texture
from pyglet.gl import GL_NEAREST

import util
from blocks import Floor, Wall


class Level:

    def __init__(self, size=64, min_room_count=3, max_room_count=5, min_room_size=5, max_room_size=20):
        self.rooms: List[Room] = []
        # Get 5-10 rooms per level
        room_cnt = util.get_random() * (max_room_count - min_room_count) + min_room_count
        i = 0
        while i < room_cnt:
            x = math.floor(util.get_random() * (size - max_room_size)) + 1
            y = math.floor(util.get_random() * (size - max_room_size)) + 1
            w = math.floor(util.get_random() * (max_room_size - min_room_size)) + min_room_size
            h = math.floor(util.get_random() * (max_room_size - min_room_size)) + min_room_size
            room = Room(x, y, w, h)
            if not any([room.intersects(r) for r in self.rooms]):
                self.rooms.append(Room(x, y, w, h))
                i += 1
        world = np.zeros((size + 1, size + 1))
        l1 = l2 = None
        for room in self.rooms:
            world[room.x:room.x2, room.y:room.y2] = True
            found_other = False
            while not found_other:
                other = util.choice([r for r in self.rooms if r is not room])
                sx = math.floor(util.get_random() * (room.x2 - room.x)) + room.x
                sy = math.floor(util.get_random() * (room.y2 - room.y)) + room.y
                ex = math.floor(util.get_random() * (other.x2 - other.x)) + other.x
                ey = math.floor(util.get_random() * (other.y2 - other.y)) + other.y
                l1 = (min(sx, ex), sy if sx < ex else ey), (max(sx, ex), (sy if sx < ex else ey) + 1)
                l2 = (l1[1][0], min(sy, ey)), (l1[1][0] + 1, max(sy, ey))
                intersections = False
                for r in self.rooms:
                    intersections = r.intersects(l1) or r.intersects(l2)
                    if intersections:
                        break
                if not intersections:
                    found_other = True
                    room.con = self.rooms.index(other)
            world[l1[0][0]:l1[1][0]+1, l1[0][1]:l1[1][1]] = True
            world[l2[0][0]:l2[1][0], l2[0][1]:l2[1][1]+1] = True
        cons = dict()
        for i, room in enumerate(self.rooms):
            if i not in cons:
                cons[i] = set()
            cons[i] = cons[i] or {room.con}
        old_set = set()
        while len(cons[0] - old_set) != 0:
            tmp = cons[0]
            for con in cons[0] - old_set:
                cons[0] = cons[0] or cons[con]
            old_set = tmp
        print(f'not connected: {cons[0] - set(range(math.floor(room_cnt)))}')
        for r in cons[0] - set(range(math.floor(room_cnt))):
            other = self.rooms[r]
            room = self.rooms[0]
            sx = math.floor(util.get_random() * (room.x2 - room.x)) + room.x
            sy = math.floor(util.get_random() * (room.y2 - room.y)) + room.y
            ex = math.floor(util.get_random() * (other.x2 - other.x)) + other.x
            ey = math.floor(util.get_random() * (other.y2 - other.y)) + other.y
            l1 = (min(sx, ex), sy if sx < ex else ey), (max(sx, ex), (sy if sx < ex else ey) + 1)
            l2 = (l1[1][0], min(sy, ey)), (l1[1][0] + 1, max(sy, ey))
            world[l1[0][0]:l1[1][0]+1, l1[0][1]:l1[1][1]] = True
            world[l2[0][0]:l2[1][0], l2[0][1]:l2[1][1]] = True
        self.map = world

    def load(self, wall_list: SpriteList, floor_list: SpriteList, physics_engine: PymunkPhysicsEngine) -> Tuple[int, int]:
        for x in range(len(self.map)):
            for y in range(len(self.map[0])):
                if self.map[x, y]:
                    ls = floor_list
                    tile = Floor('./assets/imgs/map/tiles/tile_ground1.png', scale=4)
                else:
                    ls = wall_list
                    tile = Wall('assets/imgs/map/wall/wall1.png', scale=4)
                tile.add_to_list(ls, physics_engine, (64*x), (64*y))
        spawn_room = self.rooms[util.choice(range(len(self.rooms)))]
        return ((spawn_room.x2 - spawn_room.x) / 2 + spawn_room.x)*64,\
               ((spawn_room.y2 - spawn_room.y) / 2 + spawn_room.y)*64

    def get_room(self, sprite: Sprite):
        for room in self.rooms:
            if sprite.position in room:
                return room
        return None


class Room:

    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.x2 = x + width
        self.y2 = y + height
        self.con = None

    def _get_pnt_intersections(self, other: "Room"):
        return (
            (other.x*64, other.y*64) in self,
            (other.x2*64, other.y*64) in self,
            (other.x*64, other.y2*64) in self,
            (other.x2*64, other.y2*64) in self
        )

    def intersects(self, other):
        if isinstance(other, Room):
            return any(self._get_pnt_intersections(other))
        return (
                       self.x <= other[0][0] <= self.x2 and self.y >= other[0][1] and self.y2 <= other[1][1]
               ) or (
                       self.y <= other[0][1] <= self.y2 and self.x >= other[0][0] and self.x2 <= other[1][0]
               )

    def __contains__(self, other):
        """
        Checks if the given point or Room is contained within itself. only true if the whole other room is within itself. for intersections use the intersects function
        :param other:
        :return:
        """
        if isinstance(other, Room):
            return all(self._get_pnt_intersections(other))
        return self.x <= other[0]/64 <= self.x2 and self.y <= other[1]/64 <= self.y2


class Minimap:

    def __init__(self, size: Tuple[int, int], background: Color, pos: Tuple[int, int]):
        self.size = size
        self.background = background
        self.sprite = None
        self.sprite_list = SpriteList()

        self.texture = Texture.create_empty(str(uuid4()), size)
        self.sprite = Sprite(center_x=pos[0],
                             center_y=pos[1],
                             texture=self.texture)

        self.sprite_list.append(self.sprite)

    def update(self, *sprite_lists: SpriteList):
        proj = 0, 64*64, 0, 64*64
        with self.sprite_list.atlas.render_into(self.texture, projection=proj) as fbo:
            fbo.clear(self.background)
            for sprite_list in sprite_lists:
                sprite_list.draw()

    def draw(self):
        self.sprite_list.draw(filter=GL_NEAREST)