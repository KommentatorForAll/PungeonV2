from typing import Optional, TYPE_CHECKING

from arcade import Sprite, PymunkPhysicsEngine
from abc import ABC

from global_vars import dmg_multipliers

if TYPE_CHECKING:
    from weapon import Weapon


class Entity(Sprite, ABC):

    def __init__(self, *args, **kwargs):
        """
        Base class of all 'living' beings like players and enemies
        :param args: sprite args
        :param kwargs: sprite kwargs
        """
        super().__init__(*args, **kwargs)
        self.speed = 1
        self.hp = 1
        self.type = 'physical'
        self.weapon: Optional["Weapon"] = None

    def move(self, physics_engine: PymunkPhysicsEngine):
        """
        Function defines how the entity moves. This includes ai movement and player-determined movement.
        :param physics_engine:
        :return:
        """
        raise NotImplementedError()

    def apply_dmg(self, dmg: int, dmg_type: str):
        """
        Called when the entity takes damage
        :param dmg: the base amount of damage taken
        :param dmg_type: the type of damage dealt
        :return: None
        """
        self.hp -= dmg * dmg_multipliers[dmg_type][self.type]
        if self.hp <= 0:
            self.die()

    def die(self):
        """
        called when the entities health reaches 0.
        May be overwritten to show death animation drop loot or other stuff
        :return: None
        """
        self.kill()

