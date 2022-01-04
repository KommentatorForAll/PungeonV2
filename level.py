import math
from typing import List, Tuple, Optional
from uuid import uuid4

import numpy as np
from arcade import SpriteList, PymunkPhysicsEngine, Sprite, Color, Texture
from pyglet.gl import GL_NEAREST

import util
from blocks import Floor, Wall
from constants import GLOBAL_SCALE, TILE_SIZE, MAP_SIZE
from global_vars import generation_noise


class Level:

    def __init__(self, min_room_count=3, max_room_count=5, min_room_size=5, max_room_size=20):
        """
        A games level. Contains multiple rooms, all of them connected.
        :param min_room_count: the minimum room count to generate
        :param max_room_count: the maximum room count to generate
        :param min_room_size: The smallest size of a room
        :param max_room_size: the biggest size a room dimension can get
        """
        self.rooms: List[Room] = []
        # calculates the amount of rooms to generate
        room_cnt = math.floor(util.get_random() * (max_room_count - min_room_count) + min_room_count)

        i = 0
        while i < room_cnt:
            # generating the rooms position and dimensions
            x = math.floor(util.get_random() * (MAP_SIZE - max_room_size)) + 1
            y = math.floor(util.get_random() * (MAP_SIZE - max_room_size)) + 1
            w = math.floor(util.get_random() * (max_room_size - min_room_size)) + min_room_size
            h = math.floor(util.get_random() * (max_room_size - min_room_size)) + min_room_size

            room = Room(x, y, w, h)

            # checks if it intersects with any other room
            if not any([room.intersects(r) for r in self.rooms]):
                # only adds it if it does not collide with other rooms
                self.rooms.append(Room(x, y, w, h))
                i += 1
        # generates a binary map of the level
        world = np.zeros((MAP_SIZE + 1, MAP_SIZE + 1), dtype='bool')

        # connection lines are allocated
        l1 = l2 = None
        # adds the rooms to the binary map
        for i, room in enumerate(self.rooms):

            # set the room to floor
            world[room.x:room.x2, room.y:room.y2] = True

            # find another room to connect to
            found_other = False
            # list of all rooms available to connect
            unchecked_rooms = [r for r in self.rooms if r is not room]
            while not found_other and len(unchecked_rooms) != 0:
                # pick out a random room
                other = util.choice(unchecked_rooms)
                if other.con == i:
                    unchecked_rooms.remove(other)
                    continue
                # calculate lines to connect the rooms
                sx = math.floor(util.get_random() * (room.x2 - room.x)) + room.x
                sy = math.floor(util.get_random() * (room.y2 - room.y)) + room.y
                ex = math.floor(util.get_random() * (other.x2 - other.x)) + other.x
                ey = math.floor(util.get_random() * (other.y2 - other.y)) + other.y

                l1 = (min(sx, ex), sy if sx < ex else ey), (max(sx, ex), (sy if sx < ex else ey) + 1)
                l2 = (l1[1][0], min(sy, ey)), (l1[1][0] + 1, max(sy, ey))

                # check for intersections with other rooms
                intersections = False
                for r in self.rooms:
                    intersections = r.intersects(l1) or r.intersects(l2)
                    if intersections:
                        # mark room as checked
                        unchecked_rooms.remove(other)
                        break
                if not intersections:
                    found_other = True
                    room.con = self.rooms.index(other)

            # draw in the lines, if a room was found
            if found_other:
                world[l1[0][0]:l1[1][0]+1, l1[0][1]:l1[1][1]] = True
                world[l2[0][0]:l2[1][0], l2[0][1]:l2[1][1]+1] = True
            else:
                # print a warning otherwise
                print(f'unable to find room for {i=}, {room=}')

        # Check if all rooms are reachable
        cons = dict()
        for i, room in enumerate(self.rooms):
            cons[i] = {room.con}

        # set of connections already checked
        old_set = set()
        # set of all rooms
        full_set = set(range(1, room_cnt))

        # run if there are new additions
        while len(cons[0] - old_set) != 0:
            # store current to move to old set afterwards
            tmp = cons[0]

            # add connections of newly connected rooms to current connections
            for new_con in cons[0] - old_set:
                cons[0] |= cons[new_con]
            # check for reverse connections
            for con in full_set - cons[0]:
                if cons[0] & cons.get(con, set()):
                    cons[0] |= {con}
            old_set = tmp
        print(full_set)
        print(room_cnt)
        # check if any rooms are unconnected
        unconnected_rooms = full_set - cons[0]
        if unconnected_rooms:
            print(f'not connected: {full_set - cons[0]}')
            for r in unconnected_rooms:
                # just connect to the first room no matter what
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
        # save binary map to self object
        self.map = world

    def load(self, wall_list: SpriteList, floor_list: SpriteList, physics_engine: PymunkPhysicsEngine) -> Tuple[int, int]:
        """
        load a level into the game
        :param wall_list: the list to append walls to
        :param floor_list: the list to append floor tiles to
        :param physics_engine: physics engine of the game
        :return:
        """
        # pad the binary map, to check where to place walls (as only for direct neighbors to improve performance)
        padded = np.zeros((self.map.shape[0]+2, self.map.shape[1]+2))
        padded[1:-1, 1:-1] = self.map

        for x in range(len(self.map)):
            for y in range(len(self.map[0])):
                # check if current block is a floor tile
                if self.map[x, y]:
                    ls = floor_list
                    # apply generation noise
                    tile = Floor(f'assets/imgs/map/tiles/{apply_generation_noise("tile_ground")}.png', scale=GLOBAL_SCALE)
                else:
                    # check if it is neighboring a floor tile
                    if padded[x:x+3, y:y+3].sum() == 0:
                        continue
                    ls = wall_list
                    tile = Wall(f'assets/imgs/map/wall/{apply_generation_noise("wall_brick")}.png', scale=GLOBAL_SCALE)
                tile.add_to_list(ls, physics_engine, (TILE_SIZE*x), (TILE_SIZE*y))

        # randomly select a spawn room
        spawn_room = self.rooms[util.choice(range(len(self.rooms)))]

        # return center of the room as spawn point
        return ((spawn_room.x2 - spawn_room.x) / 2 + spawn_room.x)*TILE_SIZE,\
               ((spawn_room.y2 - spawn_room.y) / 2 + spawn_room.y)*TILE_SIZE

    def get_room(self, sprite: Sprite):
        """
        Returns the room the sprite is currently in
        :param sprite: the sprite to get the room for
        :return: the room the sprite is in or None if not in any
        """
        for room in self.rooms:
            if sprite.position in room:
                return room
        return None


def apply_generation_noise(tile: str):
    """
    Applies generation noise to the given tile.
    :param tile: tile to apply generation noise to. Noise must be defined in the data.nbt
    :return:
    """
    # get all noise data from the tag
    keys, values = [list(x) for x in zip(*generation_noise[tile].items())]
    # add the default with the left over variance
    keys.append(tile)
    values.append(1-sum(values))
    # make a weighted choice
    return util.choices(population=keys, weights=values)[0]


class Room:

    def __init__(self, x: int, y: int, width: int, height: int):
        """
        A room in a level. All parameters are given in tiles
        :param x: position of the room
        :param y:
        :param width: dimensions of the room
        :param height:
        """
        self.x: int = x
        self.y: int = y
        self.x2: int = x + width
        self.y2: int = y + height
        # the room it is connected to.
        self.con: Optional[int] = None

    def _get_pnt_intersections(self, other: "Room"):
        """
        returns colliding points of another room
        :param other: the room to check collision for
        :return: tuple of booleans if the others edge points are inside our room
        """
        return (
            (other.x*TILE_SIZE, other.y*TILE_SIZE) in self,
            (other.x2*TILE_SIZE, other.y*TILE_SIZE) in self,
            (other.x*TILE_SIZE, other.y2*TILE_SIZE) in self,
            (other.x2*TILE_SIZE, other.y2*TILE_SIZE) in self
        )

    def _get_lines(self):
        """
        returns the four outer lines of this room
        :return: a list of four lines
        """
        lines = []
        [[lines.append((a, b)) for b in ((self.x, self.y2), (self.x2, self.y))] for a in ((self.x, self.y), (self.x2, self.y2))]
        return lines

    def intersects(self, other):
        """
        Checks if This room intersects the given room or line.
        :param other:
        :return:
        """
        if isinstance(other, Room):
            # in case the other is a room, checks if any of the edge points are inside each other,
            # if not, continues by checking the edges (in case rooms reach over each other)
            return \
                any(self._get_pnt_intersections(other)) or\
                any([self.intersects(line) for line in other._get_lines()])
        return (
                       self.x <= other[0][0] <= self.x2 and self.y >= other[0][1] and self.y2 <= other[1][1]
               ) or (
                       self.y <= other[0][1] <= self.y2 and self.x >= other[0][0] and self.x2 <= other[1][0]
               )

    def __contains__(self, other):
        """
        Checks if the given point or Room is contained within itself. only true if the whole other room is within itself.
        For intersections, please use the intersects function
        :param other:
        :return:
        """
        if isinstance(other, Room):
            return all(self._get_pnt_intersections(other))
        return self.x <= other[0]/TILE_SIZE <= self.x2 and self.y <= other[1]/TILE_SIZE <= self.y2


class Minimap:

    def __init__(self, size: Tuple[int, int], background: Color, pos: Tuple[int, int]):
        """
        A small version of the big map.
        :param size: the size of the minimap
        :param background: its background color
        :param pos: where it is supposed to sit on the screen
        """
        self.size = size
        self.background = background
        self.sprite_list = SpriteList()

        # the texture, the map is drawn onto
        self.texture = Texture.create_empty(str(uuid4()), size)
        # creating a sprite using said texture
        self.sprite = Sprite(center_x=pos[0],
                             center_y=pos[1],
                             texture=self.texture)

        self.sprite_list.append(self.sprite)

    def update(self, *sprite_lists: SpriteList):
        """
        updates the maps texture
        :param sprite_lists: all spritelists drawn onto the map. last list on top.
        :return:
        """
        # create a projection, size of the whole map. (IMPORTANT: whole map and not the sprites size)
        proj = 0, MAP_SIZE*TILE_SIZE, 0, MAP_SIZE*TILE_SIZE
        # create a framebuffer via the spritelists atlas
        with self.sprite_list.atlas.render_into(self.texture, projection=proj) as fbo:
            # clear it using the background color
            fbo.clear(self.background)
            # draw all spritelists into the map
            for sprite_list in sprite_lists:
                sprite_list.draw()

    def draw(self):
        """
        draw this map
        :return:
        """
        self.sprite_list.draw(filter=GL_NEAREST)
