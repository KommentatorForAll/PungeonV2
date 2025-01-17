import math
from typing import Optional

import arcade
from arcade import PymunkPhysicsEngine, SpriteList, Camera
from pyglet.gl import GL_NEAREST
from pyglet.math import Vec2

from constants import GLOBAL_SCALE
from entities import Player, Entity
from entities.enemies import Zombie
from global_vars import weapons
from level import Level, Minimap
from weapon import Projectile


class DungeonWorld(arcade.View):
    def __init__(self):
        super().__init__()

        self.wall_list: SpriteList = SpriteList(use_spatial_hash=True)
        self.floor_list: SpriteList = SpriteList(use_spatial_hash=True)
        self.players: SpriteList = SpriteList()
        self.enemies: SpriteList = SpriteList()
        self.weapons: SpriteList = SpriteList()
        self.attack_sprite_list: SpriteList = SpriteList()

        self.cam_player: Camera = Camera(800, 600)
        self.cam_ui: Camera = Camera(800, 600)

        self.physics_engine = PymunkPhysicsEngine()
        self.player: Player = Player(self, scale=GLOBAL_SCALE)

        self.room: Optional[Level] = None

        self.current_level: int = 0

        self.minimap = Minimap((256, 256), (0, 0, 0, 128), (128, 128))

        coords = self.load_level(Level())
        self.player.position = coords

        self.physics_engine.add_sprite(
            self.player, moment_of_inertia=math.inf, elasticity=0, damping=0.01
        )
        self.players.append(self.player)
        z = Zombie(self.player, self.room, self.physics_engine, (coords[0], coords[1] + 128), scale=GLOBAL_SCALE)
        self.enemies.append(z)

    def load_level(self, level: Level):
        self.wall_list = SpriteList()
        self.floor_list = SpriteList()
        for spr in self.physics_engine.sprites.copy():
            if spr is self.player:
                continue
            self.physics_engine.remove_sprite(spr)
        coords = level.load(self.wall_list, self.floor_list, self.physics_engine)
        self.room = level
        return coords

    def weaponize(self, entity: Entity, wpn: str):
        build_wpn = weapons[wpn].clone()
        build_wpn.att_spr_list = self.attack_sprite_list
        self.weapons.append(build_wpn)
        entity.weapon = build_wpn

    def move_cam_to_player(self):
        x, y = self.player.position
        x -= self.window.width/2
        y -= self.window.height/2
        self.cam_player.move_to(Vec2(x, y), 0.1)

    def on_update(self, delta_time: float):
        self.physics_engine.step(delta_time)
        # self.player.move(self.physics_engine)
        self.players.on_update()
        self.weapons.on_update()
        self.enemies.on_update()
        self.move_cam_to_player()

    def on_draw(self):
        arcade.start_render()
        self.cam_player.use()
        self.floor_list.draw(filter=GL_NEAREST)
        self.wall_list.draw(filter=GL_NEAREST)
        self.players.draw(filter=GL_NEAREST)
        self.enemies.draw(filter=GL_NEAREST)
        self.weapons.draw(pixelated=True)
        self.attack_sprite_list.draw(pixelated=True)

        self.cam_ui.use()
        self.minimap.update(self.floor_list, self.players)
        self.minimap.draw()

        y = 600 // 2 - 200
        arcade.draw_text(f'x:{self.player.joystick.x}', 300, y)
        y += 20
        arcade.draw_text(f'y:{self.player.joystick.y}', 300, y)
        y += 20
        arcade.draw_text(f'z:{self.player.joystick.z}', 300, y)
        y += 20
        arcade.draw_text(f'rx:{self.player.joystick.rx}', 300, y)
        y += 20
        arcade.draw_text(f'ry:{self.player.joystick.ry}', 300, y)
        y += 20
        arcade.draw_text(f'rz:{self.player.joystick.rz}', 300, y)
        y += 20
        arcade.draw_text(f'{self.player.position=}', 300, y)
