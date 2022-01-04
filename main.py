import arcade

import global_vars
import util
import world
from windows import GameWindow


def main():
    util.init_random("3.1415926535")
    global_vars.load_all()
    window = GameWindow()
    dungeon_view = world.DungeonWorld()
    window.show_view(dungeon_view)
    arcade.run()


if __name__ == '__main__':
    main()
