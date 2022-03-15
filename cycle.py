from itertools import cycle
import game as gm

BYTES_PER_INT = 5

class Cycle:
    def __init__(self, game: gm.Game):
        self.game = game

    def get_cycle(self):
        # speed int; level int; score int; width int; height int; grid ints
        return self.game.get_binary(BYTES_PER_INT=BYTES_PER_INT)
