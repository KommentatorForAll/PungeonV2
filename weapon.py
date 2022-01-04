from typing import List, Dict, Any, Union

from arcade import Sprite

from blocks import Tile
from entities import Entity


class Weapon(Sprite):

    def __init__(self,
                 dmg: int,
                 dmg_type: str,
                 cooldown: int,
                 sprite: str,
                 melee: bool,
                 sprite_args: Dict[str, Any],
                 proj_args: Dict[str, Any]
                 ):
        super().__init__(sprite, **sprite_args)
        self.dmg: int = dmg
        self.dmg_type: str = dmg_type
        self.cooldown: int = cooldown
        self.max_cd: int = cooldown
        self.melee: bool = melee
        self.proj_args: dict = proj_args

    def on_update(self, delta_time=1/60):
        self.cooldown -= 1

    def attack(self, owner: Sprite):
        if self.cooldown > 0:
            return None
        self.cooldown = self.max_cd
        if self.melee:
            return self
        else:
            proj_args = self.proj_args.copy()
            proj = Projectile(
                proj_args.pop('img'),
                self,
                proj_args.pop('lifetime'),
                self.angle,
                1,
                **proj_args
            )
            proj.position = self.position
            proj.hit_list.append(owner)
            return proj

    def collide(self, other: Entity):
        other.apply_dmg(self.dmg, self.dmg_type)


class Projectile(Sprite):

    def __init__(self, sprite, wpn, lifetime, vec, pierce=1, **kwargs):
        super().__init__(sprite, **kwargs)
        self.wpn = wpn
        self.lifetime = lifetime
        print(vec)
        self.vec = vec
        # self.change_x, self.change_y = vec
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
            self.wpn.collide(other)
            self.hit_list.append(other)
            self.pierce -= 1
            if self.pierce == 0:
                self.kill()
        elif isinstance(other, Tile):
            self.kill()
        else:
            print(f'collided with {other} of type {type(other)}')
