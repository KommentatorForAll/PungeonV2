import math

import arcade
from arcade import Sprite
from pymunk import Vec2d

import level
from .enemy import Enemy


class Zombie(Enemy):

    def __init__(self, target: Sprite, world: level.Level, physics_engine: arcade.PymunkPhysicsEngine, *args, **kwargs):
        super().__init__(target, world, filename='./assets/imgs/player/slime_blue.png', *args, **kwargs)
        self.physics_engine = physics_engine
        self.speed = 16
        self.physics_engine.add_sprite(self, moment_of_inertia=math.inf)

    def on_update(self, delta_time: float = 1 / 60):
        self.move(self.physics_engine)
        super().update()

    def move(self, physics_engine: arcade.PymunkPhysicsEngine):
        if self.world.get_room(self) is self.target.room:
            dx, dy = (self.position[i] - self.target.position[i] for i in range(2))
            vec = Vec2d(1*self.speed, 0).rotated(Vec2d(-dx, -dy).angle)
            physics_engine.set_velocity(self, vec)
        else:
            physics_engine.set_velocity(self, (0, 0))
        #  print(arcade.astar_calculate_path(self.position, self.target.position, self.as_bl))
