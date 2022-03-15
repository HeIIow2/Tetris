from itertools import cycle
import grid as gd

class Cycle:
    def __init__(self, level:int, score:int,grid:gd.Grid):
        self.level = level
        self.score = score
        self.grid = grid
