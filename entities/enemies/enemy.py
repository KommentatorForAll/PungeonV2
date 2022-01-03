from abc import ABC

from entities import Entity


class Enemy(Entity, ABC):

    def __init__(self, target, world, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.target = target
        self.world = world
