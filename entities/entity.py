from arcade import Sprite, PymunkPhysicsEngine
from abc import ABC


class Entity(Sprite, ABC):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.speed = 1

    def move(self, physics_engine: PymunkPhysicsEngine):
        raise NotImplementedError()
