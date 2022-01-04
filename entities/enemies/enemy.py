from abc import ABC

from arcade import PymunkPhysicsEngine

from .. import Entity, Player
from level import Level


class Enemy(Entity, ABC):

    def __init__(self, target: Player, world: Level, *args, **kwargs):
        """
        Base class for all enemies.
        :param target: The Sprite, they are attacking
        :param world: the world they live in (required for their ai)
        :param args: sprite args
        :param kwargs: sprite kwargs
        """
        super().__init__(*args, **kwargs)
        self.target: Player = target
        self.world: Level = world

    def move(self, physics_engine: PymunkPhysicsEngine):
        raise NotImplementedError()
