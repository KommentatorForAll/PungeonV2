import math

import arcade
from arcade import PymunkPhysicsEngine, SpriteList, Camera
from pyglet.gl import GL_NEAREST
from pyglet.math import Vec2

import entities
from entities import Player
from map import Room, Level


class DungeonWorld(arcade.View):
    def __init__(self):
        super().__init__()
        self.player: Player = Player(scale=4)
        self.cam_player: Camera = Camera(800, 600)
        self.cam_ui: Camera = Camera(800, 600)
        self.wall_list: SpriteList = SpriteList()
        self.floor_list: SpriteList = SpriteList()
        self.entities: SpriteList = SpriteList()
        self.physics_engine = PymunkPhysicsEngine()
        self.physics_engine.add_sprite(
            self.player, moment_of_inertia=math.inf, elasticity=0, damping=0.01
        )
        self.room = Level()
        coords = self.room.load(self.wall_list, self.floor_list, self.physics_engine)
        self.physics_engine.get_physics_object(self.player).body.position = coords
        self.entities.append(self.player)

    def move_cam_to_player(self):
        x, y = self.player.position
        x -= self.window.width/2
        y -= self.window.height/2
        self.cam_player.move_to(Vec2(x, y), 0.1)

    def on_update(self, delta_time: float):
        self.physics_engine.step(delta_time)
        self.player.move(self.physics_engine)
        self.move_cam_to_player()

    def on_draw(self):
        arcade.start_render()
        self.cam_player.use()
        self.floor_list.draw(filter=GL_NEAREST)
        self.wall_list.draw(filter=GL_NEAREST)
        self.entities.draw(filter=GL_NEAREST)
        # self.cam_ui.use()
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
