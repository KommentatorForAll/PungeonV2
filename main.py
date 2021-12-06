import arcade

import util
import world
from windows import GameWindow


def main():
    util.init_random("2")
    window = GameWindow()
    dungeon_view = world.DungeonWorld()
    window.show_view(dungeon_view)
    arcade.run()


if __name__ == '__main__':
    main()
