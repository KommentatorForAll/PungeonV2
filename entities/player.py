import arcade
from pyglet.input import Joystick
from pymunk import Vec2d

import level
from .entity import Entity


class Player(Entity):
    def __init__(self, world, *args, **kwargs):
        super().__init__('./assets/imgs/player/player_f.png', *args, **kwargs)

        self.room = None
        self.world = world

        self.speed = 1000
        self.running = False
        # Get list of game controllers that are available
        joysticks = arcade.get_joysticks()

        # If we have any...
        if joysticks:
            # Grab the first one in  the list
            self.joystick: Joystick = joysticks[0]

            # Open it for input
            self.joystick.open()

            # Push this object as a handler for joystick events.
            # Required for the on_joy* events to be called.
            self.joystick.push_handlers(self)
        else:
            # Handle if there are no joysticks.
            print("There are no joysticks, plug in a joystick and run again.")
            self.joystick = None

    def move(self, physics_engine: arcade.PymunkPhysicsEngine):
        from . import DEAD_ZONE
        x = 0 if -DEAD_ZONE < self.joystick.x < DEAD_ZONE else self.joystick.x
        y = 0 if -DEAD_ZONE < self.joystick.y < DEAD_ZONE else -self.joystick.y
        vec = Vec2d(x, y)
        movement = vec * self.speed * (self.running + 1)
        physics_engine.apply_force(self, movement)

        self.room = self.world.room.get_room(self)

    def on_joybutton_press(self, _joystick, button):
        """ Handle button-down event for the joystick """
        print("Button {} down".format(button))
        if button == 2:
            self.running = True
        elif button == 7:
            self.physics_engines[0].get_physics_object(self).body.position = self.world.load_level(level.Level())

    def on_joybutton_release(self, _joystick, button):
        """ Handle button-up event for the joystick """
        print("Button {} up".format(button))
        if button == 2:
            self.running = False
