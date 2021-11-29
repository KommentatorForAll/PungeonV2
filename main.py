import arcade

import world
from windows import GameWindow


def main():
    window = GameWindow()
    dungeon_view = world.DungeonWorld()
    window.show_view(dungeon_view)
    arcade.run()


if __name__ == '__main__':
    main()
