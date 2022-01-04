import arcade

import global_vars
import util
import world
from windows import GameWindow


def main():
    # initialize random with a custom seed (used to make the game deterministic)
    util.init_random("3.141592653")
    # load all variables
    global_vars.load_all()
    # create a window for the game
    window = GameWindow()
    # create a world
    dungeon_view = world.DungeonWorld()
    window.show_view(dungeon_view)
    arcade.run()


if __name__ == '__main__':
    main()
