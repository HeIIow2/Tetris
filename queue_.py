import figure as fg
import cell as cl
import random
from PIL import Image

class Queue:
    def __init__(self, figures: list, length: int, height: int, width: int):
        self.grid = []
        self.FIGURES = []
        for i, figure in enumerate(figures):
            self.FIGURES.append(fg.Figure(figure[0], figure[1:], mode=i+1))

        self.grid_height = height
        self.grid_width = width

        self.empty_cell = cl.Cell()

        for i in range(height):
            row = []
            for j in range(width):
                row.append(self.empty_cell)
            self.grid.append(row)

        self.prev_piece_ind = -1

        self.queue = []
        for i in range(length):
            self.queue.append(self.get_random_piece())

    def get_random_piece(self):
        # https://gaming.stackexchange.com/questions/13057/tetris-difficulty#13129
        
        """
        FIGURES = [
            Figure(4, [0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0], 1),
            Figure(3, [1, 0, 0, 1, 1, 1, 0, 0, 0], 2),
            Figure(3, [0, 0, 1, 1, 1, 1, 0, 0, 0], 3),
            Figure(2, [1, 1, 1, 1], 4),
            Figure(3, [0, 1, 1, 1, 1, 0, 0, 0, 0], 5),
            Figure(3, [0, 1, 0, 1, 1, 1, 0, 0, 0], 6),
            Figure(3, [1, 1, 0, 0, 1, 1, 0, 0, 0], 7),
        ]"""

        random_number = random.randint(0, len(self.FIGURES))
        if random_number == self.prev_piece_ind or random_number == len(self.FIGURES):
            random_number = random.randint(0, len(self.FIGURES)-1)

        self.prev_piece_ind = random_number
        return self.FIGURES[random_number]

    def next_piece(self):
        next_piece_ = self.queue[0]
        self.queue.pop(0)

        self.queue.append(self.get_random_piece())
        return next_piece_

    def draw(self, width: int, height: int, spacing: int):
        img_height = 0
        figure_images = []
        for figure in self.queue:
            figure_images.append(figure.draw(grid_width=self.grid_width, width=width, height=height, spacing=spacing))
            img_height += figure_images[-1].height

        img_width = width * self.grid_width + spacing * (self.grid_width + 1)

        img = Image.new("RGB", (img_width, img_height), color="#666")
        current_height = 0
        for image in figure_images:
            img.paste(image, (0, current_height))

            current_height += image.height

        return img
