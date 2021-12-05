import math

import arcade
from arcade import Sprite, SpriteList, PymunkPhysicsEngine


class Tile(Sprite):

    def add_to_list(self, sprite_list: SpriteList, physics_engine: PymunkPhysicsEngine, x: int, y: int):
        raise NotImplementedError('Tried to call function of an abstract class')


class Wall(Tile):

    def add_to_list(self, sprite_list: SpriteList, physics_engine: PymunkPhysicsEngine, x: int, y: int):
        self.set_position(x, y)
        physics_engine.add_sprite(self, body_type=PymunkPhysicsEngine.STATIC, elasticity=0)
        sprite_list.append(self)


class Floor(Tile):

    def add_to_list(self, sprite_list: SpriteList, physics_engine: PymunkPhysicsEngine, x: int, y: int):
        self.set_position(x, y)
        sprite_list.append(self)
