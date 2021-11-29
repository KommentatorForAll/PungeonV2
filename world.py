import math

import arcade
from arcade import PymunkPhysicsEngine, SpriteList
from pyglet.gl import GL_NEAREST

from entities import Player


class DungeonWorld(arcade.View):
    def __init__(self):
        super().__init__()
        self.player: Player = Player(scale=4)
        self.sprites: SpriteList = SpriteList()
        self.sprites.append(self.player)
        self.physics_engine = PymunkPhysicsEngine()
        self.physics_engine.add_sprite(
            self.player, moment_of_inertia=math.inf
        )

    def on_update(self, delta_time: float):
        self.physics_engine.step(delta_time)
        self.player.move(self.physics_engine)

    def on_draw(self):
        arcade.start_render()
        self.sprites.draw(filter=GL_NEAREST)
        y = 600 // 2 - 200
        arcade.draw_text(f'x:{self.player.joystick.x}', 200, y)
        y += 20
        arcade.draw_text(f'y:{self.player.joystick.y}', 200, y)
        y += 20
        arcade.draw_text(f'z:{self.player.joystick.z}', 200, y)
        y += 20
        arcade.draw_text(f'rx:{self.player.joystick.rx}', 200, y)
        y += 20
        arcade.draw_text(f'ry:{self.player.joystick.ry}', 200, y)
        y += 20
        arcade.draw_text(f'rz:{self.player.joystick.rz}', 200, y)
        y += 20
