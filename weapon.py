from typing import List, Dict, Any, Union

from arcade import Sprite
from pymunk import Vec2d

from blocks import Tile
from constants import TILE_SIZE
from entities import Entity


class Weapon(Sprite):

    def __init__(self,
                 dmg: int,
                 dmg_type: str,
                 cooldown: int,
                 sprite: str,
                 melee: bool,
                 owner: Sprite,
                 sprite_args: Dict[str, Any],
                 proj_args: Dict[str, Any]
                 ):
        """
        A weapon to deal damage with
        :param dmg: the amount of damage it deals
        :param dmg_type: the damage type (physical, electric, water etc)
        :param cooldown: the cooldown it has after using
        :param sprite: the sprite path
        :param melee: if it is a melee weapon
        :param owner: who currently owns the weapon
        :param sprite_args: additional arguments for the sprite
        :param proj_args: arguments for the weapons projectile
        """
        super().__init__(sprite, **sprite_args)
        self.dmg: int = dmg
        self.dmg_type: str = dmg_type
        self.cooldown: int = cooldown
        self.max_cd: int = cooldown
        self.melee: bool = melee
        self.owner: Sprite = owner
        self.proj_args: dict = proj_args

    def on_update(self, delta_time=1/60):
        self.cooldown -= 1

    def attack(self, owner: Sprite):
        """
        uses the weapon
        :param owner: who uses it
        :return:
        """
        # check if the weapon still has cooldown
        if self.cooldown > 0:
            return None
        # reset cooldown
        self.cooldown = self.max_cd
        if self.melee:
            return self
        else:
            # clone the projectile args, to be able to pop some off
            proj_args = self.proj_args.copy()
            # create a new projectile
            proj = Projectile(
                proj_args.pop('img'),
                self,
                proj_args.pop('lifetime'),
                self.angle,
                owner.world.physics_engine.get_physics_object(self.owner).body.velocity,
                1,
                proj_args.pop('speed'),
                **proj_args
            )
            # set its position properly
            proj.position = self.position
            # avoid the owner getting hurt by their own attack
            proj.hit_list.append(owner)
            return proj

    def collide(self, other: Entity, by_projectile=False):
        if (not by_projectile and not self.melee) or other is self.owner:
            return
        other.apply_dmg(self.dmg, self.dmg_type)


class Projectile(Sprite):

    def __init__(self, sprite, wpn, lifetime, vec, owner_speed, pierce=1, speed=5, **kwargs):
        super().__init__(sprite, **kwargs)
        self.wpn = wpn
        self.lifetime = lifetime
        self.vec = vec
        print(owner_speed / TILE_SIZE)
        self.change_x, self.change_y = Vec2d(speed, 0).rotated_degrees(vec) + (owner_speed / TILE_SIZE)
        self.hit_list: List[Sprite] = []
        self.pierce = pierce

    def on_update(self, delta_time=1/60):
        self.lifetime -= 1
        if self.lifetime == 0:
            self.kill()

    def collide(self, other: Union[Entity, Tile]):
        if other in self.hit_list:
            return
        if isinstance(other, Entity):
            self.wpn.collide(other, True)
            self.hit_list.append(other)
            self.pierce -= 1
            if self.pierce == 0:
                self.kill()
        elif isinstance(other, Tile):
            self.kill()
        else:
            print(f'collided with {other} of type {type(other)}')
