import math
from typing import Tuple

import arcade
from pymunk import Vec2d

import level
from weapon import Weapon
from .enemy import Enemy
from .. import Player


class Zombie(Enemy):

    def __init__(self,
                 target: Player,
                 world: level.Level,
                 physics_engine: arcade.PymunkPhysicsEngine,
                 position: Tuple[float, float] = (0, 0),
                 *args,
                 **kwargs):
        """
        Enemy with an simple ai.
        :param target: the thing to attack
        :param world: the world it lives in (requried for ai)
        :param physics_engine: physics of the game
        :param position: its initial position
        :param args: sprite args
        :param kwargs: sprite kwargs
        """
        super().__init__(target, world, filename='./assets/imgs/player/slime_blue.png', *args, **kwargs)
        self.physics_engine = physics_engine
        self.speed = 64
        self.position = position
        self.physics_engine.add_sprite(self, moment_of_inertia=math.inf)

        # self.weapon = Weapon(5, 'ice', 100, './assets/imgs/Invis.png', False, self, {}, {'img': './assets/imgs/weapons/projectiles/Slime_blob.png', 'scale': 4, 'lifetime': 60, 'speed': 10})

    def on_update(self, delta_time: float = 1 / 60):
        self.move(self.physics_engine)
        # proj = self.weapon.attack(self)
        super().update()

    def move(self, physics_engine: arcade.PymunkPhysicsEngine):
        """
        moves the zombie towards the target
        :param physics_engine: Physics engine to move
        """
        # only moves when the player and the enemy are in the same room
        if self.world.get_room(self) is self.target.room:
            dx, dy = (self.position[i] - self.target.position[i] for i in range(2))
            # rotates speed vector to the target
            vec = Vec2d(1*self.speed, 0).rotated(Vec2d(-dx, -dy).angle)
            # self.weapon.rotation = vec.angle_degrees
            physics_engine.set_velocity(self, vec)
        else:
            # stops moving, once they the enemy and the target don't share a room anymore
            physics_engine.set_velocity(self, (0, 0))
