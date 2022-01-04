from typing import List, Tuple, Union
from uuid import uuid4

import numpy as np
import math
from arcade import SpriteList, PymunkPhysicsEngine, Sprite, Color, Texture
from pyglet.gl import GL_NEAREST

import util
from blocks import Floor, Wall

from constants import GLOBAL_SCALE, TILE_SIZE, MAP_SIZE
from global_vars import generation_noise


class Level:

    def __init__(self, min_room_count=3, max_room_count=5, min_room_size=5, max_room_size=20):
        self.rooms: List[Room] = []
        # Get 5-10 rooms per level
        room_cnt = util.get_random() * (max_room_count - min_room_count) + min_room_count
        i = 0
        while i < room_cnt:
            x = math.floor(util.get_random() * (MAP_SIZE - max_room_size)) + 1
            y = math.floor(util.get_random() * (MAP_SIZE - max_room_size)) + 1
            w = math.floor(util.get_random() * (max_room_size - min_room_size)) + min_room_size
            h = math.floor(util.get_random() * (max_room_size - min_room_size)) + min_room_size
            room = Room(x, y, w, h)
            if not any([room.intersects(r) for r in self.rooms]):
                self.rooms.append(Room(x, y, w, h))
                i += 1
        world = np.zeros((MAP_SIZE + 1, MAP_SIZE + 1))
        l1 = l2 = None
        for i, room in enumerate(self.rooms):
            world[room.x:room.x2, room.y:room.y2] = True
            found_other = False
            unchecked_rooms = [r for r in self.rooms if r is not room]
            while not found_other and len(unchecked_rooms) != 0:
                other = util.choice(unchecked_rooms)
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
                    if other.con == i:
                        unchecked_rooms.remove(other)
                        continue
                    found_other = True
                    room.con = self.rooms.index(other)
            if found_other:
                world[l1[0][0]:l1[1][0]+1, l1[0][1]:l1[1][1]] = True
                world[l2[0][0]:l2[1][0], l2[0][1]:l2[1][1]+1] = True
            else:
                print(f'unable to find room for {i=}, {room=}')
        cons = dict()
        for i, room in enumerate(self.rooms):
            cons[i] = {room.con}
        print(f'{cons=} {room_cnt}')
        old_set = set()
        full_set = set(range(1, math.floor(room_cnt)+1))
        while len(cons[0] - old_set) != 0:
            tmp = cons[0]
            for new_con in cons[0] - old_set:
                cons[0] |= cons[new_con]
            for con in full_set - cons[0]:
                if cons[0] & cons[con]:
                    cons[0] |= {con}
            old_set = tmp
        print(f'not connected: {full_set - cons[0]}')
        for r in full_set - cons[0]:
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
                    keys, values = [list(x) for x in zip(*generation_noise['tile_ground'].items())]
                    keys.append('tile_ground')
                    values.append(1-sum(values))
                    tile = Floor(f'assets/imgs/map/tiles/{util.choices(population=keys, weights=values)[0]}.png', scale=GLOBAL_SCALE)
                else:
                    ls = wall_list
                    keys, values = [list(x) for x in zip(*generation_noise['wall_brick'].items())]
                    keys.append('wall_brick')
                    values.append(1-sum(values))
                    tile = Wall(f'assets/imgs/map/wall/{util.choices(population=keys, weights=values)[0]}.png', scale=GLOBAL_SCALE)
                tile.add_to_list(ls, physics_engine, (TILE_SIZE*x), (TILE_SIZE*y))
        spawn_room = self.rooms[util.choice(range(len(self.rooms)))]
        return ((spawn_room.x2 - spawn_room.x) / 2 + spawn_room.x)*TILE_SIZE,\
               ((spawn_room.y2 - spawn_room.y) / 2 + spawn_room.y)*TILE_SIZE

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
            (other.x*TILE_SIZE, other.y*TILE_SIZE) in self,
            (other.x2*TILE_SIZE, other.y*TILE_SIZE) in self,
            (other.x*TILE_SIZE, other.y2*TILE_SIZE) in self,
            (other.x2*TILE_SIZE, other.y2*TILE_SIZE) in self
        )

    def _get_lines(self):
        lines = []
        [[lines.append((a, b)) for b in ((self.x, self.y2), (self.x2, self.y))] for a in ((self.x, self.y), (self.x2, self.y2))]
        return lines

    def intersects(self, other):
        if isinstance(other, Room):
            return any(self._get_pnt_intersections(other)) or any([self.intersects(line) for line in other._get_lines()])
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
        return self.x <= other[0]/TILE_SIZE <= self.x2 and self.y <= other[1]/TILE_SIZE <= self.y2


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
        proj = 0, MAP_SIZE*TILE_SIZE, 0, MAP_SIZE*TILE_SIZE
        with self.sprite_list.atlas.render_into(self.texture, projection=proj) as fbo:
            fbo.clear(self.background)
            for sprite_list in sprite_lists:
                sprite_list.draw()

    def draw(self):
        self.sprite_list.draw(filter=GL_NEAREST)
