from abc import ABC
from typing import Union, Optional, List, TYPE_CHECKING

from arcade import Sprite, SpriteList
from pymunk import Vec2d

from blocks import Tile
from constants import TILE_SIZE

if TYPE_CHECKING:
    from entities import Entity


class Weapon(Sprite):

    def __init__(self, att_spr, cooldown, name, description, **sprite_args):
        super().__init__(**sprite_args)
        self.att_spr: "AttackSprite" = att_spr
        self.max_cooldown: int = cooldown
        self.cooldown: int = cooldown
        self.name: str = name
        self.description: str = description

    @property
    def range(self):
        return self.att_spr.range

    def clone(self):
        return Weapon(self.att_spr, self.max_cooldown, self.name, self.description, texture=self.texture)

    def on_update(self, delta_time: float = 1 / 60):
        self.cooldown = (self.cooldown-1) or 1

    def attack(self, owner, vec, owner_speed):
        if self.cooldown == 1:
            self.cooldown = self.max_cooldown
            new_proj = self.att_spr.clone()
            new_proj.attack(owner, vec, owner_speed)


class AttackSprite(Sprite, ABC):

    def __init__(self, sprite, dmg, dmg_type, pierce, cloned=False, **kwargs):
        super().__init__(sprite, **kwargs)
        self.att_spr_list: Optional[SpriteList] = None
        self.dmg: int = dmg
        self.dmg_type: str = dmg_type
        self.cloned: bool = cloned
        self.pierce: int = pierce
        self.hit_list: List[Sprite] = []

    def clone(self) -> "AttackSprite":
        raise NotImplementedError()

    @property
    def range(self):
        raise NotImplementedError()

    def on_update(self, delta_time: float = 1 / 60):
        raise NotImplementedError()

    def attack(self, owner, vec, owner_speed):
        if not self.cloned:
            raise ValueError('Tried to attack with uncloned projectile. Please use .clone()')
        self.hit_list.append(owner)

    def collide(self, other: Union["Entity", Tile]):
        if other in self.hit_list:
            return
        if isinstance(other, Entity):
            other.apply_dmg(self.dmg, self.dmg_type)
            self.hit_list.append(other)
            self.pierce -= 1
            if self.pierce == 0:
                self.kill()
        elif isinstance(other, Tile):
            self.kill()
        else:
            print(f'collided with {other} of type {type(other)}')


class Projectile(AttackSprite):

    def __init__(self, sprite, lifetime, speed, dmg, dmg_type, pierce, cloned=False, **kwargs):
        super().__init__(sprite, dmg, dmg_type, pierce, cloned, **kwargs)
        self.lifetime = lifetime
        self.speed = speed

    @property
    def range(self):
        return self.speed * self.lifetime

    def clone(self):
        print(self.properties)
        return Projectile(None, self.att_spr_list, self.lifetime, self.pierce, self.speed, self.pierce, cloned=True, texture=self.texture, scale=4)

    def on_update(self, delta_time: float = 1/60):
        self.lifetime -= 1
        if self.lifetime == 0:
            self.kill()

    def attack(self, owner, vec, owner_speed):
        super().attack(owner, vec, owner_speed)
        self.change_x, self.change_y = Vec2d(self.speed, 0).rotated(vec.angle) + (owner_speed / TILE_SIZE)
