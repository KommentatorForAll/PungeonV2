import arcade
from pyglet.input import Joystick
from pymunk import Vec2d

import level
from weapon import Weapon
from .entity import Entity

from constants import CONTROLLER_DEAD_ZONE as DEAD_ZONE, GLOBAL_SCALE


class Player(Entity):
    def __init__(self, world: "world.DungeonWorld", *args, **kwargs):
        """
        The player. Controlled by a phenomena called 'user' (scary, i know)
        :param world: the current level
        :param args: sprite args
        :param kwargs: sprite kwargs
        """
        super().__init__('./assets/imgs/player/player_f.png', *args, **kwargs)

        self.world = world
        # the current room the player is in, determined by their position in the world
        self.room = None

        self.speed = 1000
        self.running = False

        # The last known rotation of the weapon, before the controller entered the DEAD_ZONE
        self.old_rot = (0, 0)

        # The players current weapon.
        self.weapon = Weapon(6, 'physical', 0, './assets/imgs/weapons/bow_basic.png', False, self, {'scale': GLOBAL_SCALE},
                             {'img': './assets/imgs/weapons/projectiles/slingstone.png', 'scale': GLOBAL_SCALE, 'lifetime':60, 'speed': 5})

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
            self.joystick = None
            raise ValueError("There are no joysticks, plug in a joystick and run again.")

    def move(self, physics_engine: arcade.PymunkPhysicsEngine):
        """
        Moves the player by their joystick aka gamepad
        :param physics_engine:
        :return:
        """
        # Check if left stick is inside the DEAD_ZONE
        x = 0 if -DEAD_ZONE < self.joystick.x < DEAD_ZONE else self.joystick.x
        y = 0 if -DEAD_ZONE < self.joystick.y < DEAD_ZONE else -self.joystick.y

        # force vector
        vec = Vec2d(x, y)
        movement = vec * self.speed * (self.running + 1)
        physics_engine.apply_force(self, movement)

        # updates the weapons sprite position to the players position
        self.weapon.position = self.position

        # right stick position including DEAD_ZONE
        x = self.old_rot[0] if -DEAD_ZONE < self.joystick.rx < DEAD_ZONE else self.joystick.rx
        y = self.old_rot[1] if -DEAD_ZONE < self.joystick.ry < DEAD_ZONE else -self.joystick.ry

        vec = Vec2d(x, y)
        self.old_rot = (x, y)
        self.weapon.angle = vec.angle_degrees

        # update current room
        self.room = self.world.room.get_room(self)

    def on_joybutton_press(self, _joystick, button):
        """ Handle button-down event for the joystick """
        print("Button {} down".format(button))
        # using X (left action button) to run
        if button == 2:
            self.running = True
        # using 'start' button to generate new level (dev cheats)
        elif button == 7:
            self.physics_engines[0].get_physics_object(self).body.position = self.world.load_level(level.Level())
        # using rb to attack
        elif button == 5:
            proj = self.weapon.attack(self)
            if proj is not None:
                self.world.weapons.append(proj)

    def on_joybutton_release(self, _joystick, button):
        """ Handle button-up event for the joystick """
        print("Button {} up".format(button))
        # resetting run after we stopped pressing the button
        if button == 2:
            self.running = False
