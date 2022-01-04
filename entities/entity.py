from arcade import Sprite, PymunkPhysicsEngine
from abc import ABC

from global_vars import dmg_multipliers


class Entity(Sprite, ABC):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.speed = 1
        self.hp = 1
        self.type = 'physical'

    def move(self, physics_engine: PymunkPhysicsEngine):
        raise NotImplementedError()

    def apply_dmg(self, dmg: int, dmg_type: str):
        self.hp -= dmg * dmg_multipliers(dmg_type, self.type)
        if self.hp <= 0:
            self.die()

    def die(self):
        self.kill()

