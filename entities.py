import arcade
from arcade import Sprite
from pyglet.input import Joystick
from pymunk import Vec2d

DEAD_ZONE = 0.1


class Entity(Sprite):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class Player(Entity):
    def __init__(self, *args, **kwargs):
        super().__init__('./assets/imgs/player/player_f.png', *args, **kwargs)
        self.speed = 100
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
        x = 0 if -DEAD_ZONE < self.joystick.x < DEAD_ZONE else self.joystick.x
        y = 0 if -DEAD_ZONE < self.joystick.y < DEAD_ZONE else -self.joystick.y
        vec = Vec2d(x, y)
        movement = vec * self.speed * (self.running + 1)
        physics_engine.set_velocity(self, movement)

    # noinspection PyMethodMayBeStatic
    def on_joybutton_press(self, _joystick, button):
        """ Handle button-down event for the joystick """
        print("Button {} down".format(button))
        if button == 2:
            self.running = True

    # noinspection PyMethodMayBeStatic
    def on_joybutton_release(self, _joystick, button):
        """ Handle button-up event for the joystick """
        print("Button {} up".format(button))
        if button == 2:
            self.running = False

    # noinspection PyMethodMayBeStatic
    def on_joyaxis_motion(self, joystick, axis, value):
        if value < -DEAD_ZONE or DEAD_ZONE < value:
            # print(f"axis: {axis}; value: {value}")
            pass
