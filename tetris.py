import copy
import tkinter
import tkinter as tk
from PIL import Image, ImageTk
import random


class Cell:
    def __init__(self, falling_=False, mode=0):
        self.falling = falling_
        self.mode = mode

    def draw(self, width: int, height: int):
        colors = ["#000", "#2f96af", "#2f44af", "#af6d2f", "#afaf2f", "#3caf2f", "#962faf", "#af2f2f"]
        """
        stick
        blue bend
        orange bend
        square
        left up
        crossing
        right up
        """

        return Image.new("RGB", (width, height), color=colors[self.mode])


class Figure:
    def __init__(self, size: int, matrix: list, mode: int, x=0, y=0):
        self.x = x
        self.y = y
        self.real_y = y
        self.width = size
        self.height = size
        self.mode = mode

        self.soft_drop = 0

        self.grid = []
        for i, elem in enumerate(matrix):
            if i % self.width == 0:
                self.grid.append([])

            if bool(elem):
                self.grid[-1].append(Cell(falling_=True, mode=self.mode))
            else:
                self.grid[-1].append(None)

        self.update_y()

    def get_pieces(self):
        pieces = []

        for y, row in enumerate(self.grid):
            for x, cell in enumerate(row):
                if cell is None:
                    continue
                if y + self.y < 0:
                    continue

                pieces.append([x + self.x, y + self.y, cell])

        return pieces

    def randomize_rotation(self):
        for i in range(random.randint(0, 2)):
            self.rotate_right()

    def update_y(self):
        i = 0
        for i, row in enumerate(reversed(self.grid)):
            empty_row = False

            for cell in row:
                if cell is not None:
                    empty_row = True
                    break
            if empty_row:
                break
        self.y = -self.height + i

    def rotate_left(self):
        temp_grid = copy.deepcopy(self.grid)

        for i in range(self.height):
            for j in range(self.width):
                temp_grid[self.width - j - 1][i] = self.grid[i][j]

        self.grid = temp_grid

    def rotate_right(self):
        temp_grid = copy.deepcopy(self.grid)

        for i in range(self.height):
            for j in range(self.width):
                temp_grid[j][self.height - i - 1] = self.grid[i][j]

        self.grid = temp_grid


class Grid:
    def __init__(self, width: int, height: int):
        self.figures = []
        self.to_pop = []
        self.grid_width = width
        self.grid_height = height

        self.grid = []

        for i in range(height):
            row = []
            for j in range(width):
                row.append(Cell())
            self.grid.append(row)

    def game_over(self):
        print("game over")
        exit(666)

    def is_falling(self):
        for i in range(self.grid_height):
            for j in range(self.grid_width):
                if self.grid[i][j].falling:
                    return True

        return False

    def is_occupied(self, x: int, y: int):

        if y >= self.grid_height:
            return True

        if x >= self.grid_width or x < 0:
            return True

        if y < 0:
            return False

        if self.grid[y][x].mode != 0:
            return True

        return False

    def is_placeable(self, fig: Figure):
        f_x = fig.x
        f_y = fig.y

        for i, row in enumerate(fig.grid):
            for j, cell in enumerate(row):
                if cell is None:
                    continue

                if self.is_occupied(f_x + j, f_y + i):
                    return False

        return True

    def update(self, soft_drop=False):
        continuous_soft_drop = 0
        to_pop = []
        for i, figure in enumerate(self.figures):
            if soft_drop:
                figure.soft_drop += 1
            else:
                figure.soft_drop = 0
            figure.y += 1
            if not self.is_placeable(figure):
                print(f"{i} is not placeable")
                # append figure to grid and delete
                figure.y -= 1
                continuous_soft_drop += figure.soft_drop

                for piece in figure.get_pieces():
                    x, y, cell = piece
                    self.grid[y][x] = cell

                to_pop.append(i)

        for i in to_pop:
            self.figures.pop(i)

        # wenn in der obersten Zeile ein block ist, game over
        first_row = self.grid[0]
        for cell in first_row:
            if cell.mode != 0:
                self.game_over()
                break

        # Wenn eine Zeile voll ist, lösche diese
        number_of_full_row = 0
        for i, row in enumerate(self.grid):
            is_full = True
            for cell in row:
                if cell.mode == 0:
                    is_full = False

            if is_full:
                number_of_full_row += 1
                self.remove_row(i)

        return number_of_full_row, continuous_soft_drop

    def spawn_figure(self, figure: Figure):
        figure = copy.deepcopy(figure)
        figure.randomize_rotation()
        figure.x = random.randint(0, self.grid_width - figure.width)

        self.figures.append(figure)

    def remove_row(self, row_ind: int):
        self.grid.pop(row_ind)
        self.grid.insert(0, copy.deepcopy(self.grid[0]))

    def draw(self, width: int, height: int, spacing: int):
        temp_grid = copy.deepcopy(self.grid)

        for figure in self.figures:
            for x, y, cell in figure.get_pieces():
                temp_grid[y][x] = cell

        img_width = width * self.grid_width + spacing * (self.grid_width + 1)
        img_height = height * self.grid_height + spacing * (self.grid_height + 1)

        img = Image.new("RGB", (img_width, img_height), color="#666")

        y = spacing
        for i in range(self.grid_height):
            x = spacing
            for j in range(self.grid_width):
                Image.Image.paste(img, temp_grid[i][j].draw(width, height), (x, y))
                x += spacing + width
            y += spacing + height

        return img

    def right(self):
        for i, figure in enumerate(self.figures):
            figure.x += 1
            if not self.is_placeable(figure):
                figure.x -= 1

    def left(self):
        for i, figure in enumerate(self.figures):
            figure.x -= 1
            if not self.is_placeable(figure):
                figure.x += 1

    def move_in_bounds(self, index: int):
        while not self.is_placeable(self.figures[index]):
            if self.figures[index].x < 0:
                self.figures[index].x += 1
            else:
                self.figures[index].x -= 1

    def turn_right(self):
        for i in range(len(self.figures)):
            self.figures[i].rotate_right()
            self.move_in_bounds(i)

    def turn_left(self):
        for i in range(len(self.figures)):
            self.figures[i].rotate_left()
            self.move_in_bounds(i)

    def allow_spawn(self):
        return len(self.figures) == 0


class Game:
    def __init__(self, ui_frame, width=10, height=20, level=1, start_speed=800, start_score=0, level_cap=20):
        self.cycle = 0

        self.grid = Grid(width=width, height=height)

        self.ui_frame = ui_frame
        self.ui_frame.bind('<KeyPress>', self.on_key_press)

        self.img_label = tkinter.Label(self.ui_frame)
        self.img = None
        self.render()
        self.img_label.pack()

        self.score = start_score
        self.level = level
        self.level_cap = level_cap
        self.speed = start_speed

        self.prev_piece_ind = -1
        self.broken_lines = 0

    def set_speed(self):
        # https://gaming.stackexchange.com/questions/13057/tetris-difficulty#13129

        # from level, to level, drop speed
        # -1 means infinity
        SPEEDS = [
            [0, 0, 800],
            [1, 1, 720],
            [2, 2, 630],
            [3, 3, 550],
            [4, 4, 470],
            [5, 5, 380],
            [6, 6, 300],
            [7, 7, 220],
            [8, 8, 130],
            [9, 9, 100],
            [10, 12, 80],
            [13, 15, 70],
            [16, 18, 50],
            [19, 28, 30],
            [29, -1, 20]
        ]

        max_level = 0
        speed_ = 800
        for min_level, max_level, speed_ in SPEEDS:
            if min_level <= self.level <= max_level:
                self.speed = speed_
                break

        if max_level == -1:
            self.speed = speed_

    def get_score(self, broken_rows: int):
        # https://tetris.fandom.com/wiki/Scoring

        POINTS = [0, 40, 100, 300, 1200]

        return POINTS[broken_rows]*self.level

    def update_level(self):
        # https://gaming.stackexchange.com/questions/379636/how-does-the-leveling-system-on-tetris-work

        level = self.level
        if level > self.level_cap:
            level = self.level_cap
        required_lines = level * 10
        print(f"update level {required_lines}, {self.broken_lines}")

        if self.broken_lines >= required_lines:
            self.broken_lines -= required_lines
            self.level += 1
            self.set_speed()

    def get_next_piece(self):
        # https://gaming.stackexchange.com/questions/13057/tetris-difficulty#13129

        FIGURES = [
            Figure(4, [0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0], 1),
            Figure(3, [1, 0, 0, 1, 1, 1, 0, 0, 0], 2),
            Figure(3, [0, 0, 1, 1, 1, 1, 0, 0, 0], 3),
            Figure(2, [1, 1, 1, 1], 4),
            Figure(3, [0, 1, 1, 1, 1, 0, 0, 0, 0], 5),
            Figure(3, [0, 1, 0, 1, 1, 1, 0, 0, 0], 6),
            Figure(3, [1, 1, 0, 0, 1, 1, 0, 0, 0], 7),
        ]

        random_number = random.randint(0, 7)
        if random_number == self.prev_piece_ind or random_number == 7:
            random_number = random.randint(0, 6)

        self.prev_piece_ind = random_number
        return FIGURES[random_number]

    def on_key_press(self, e):
        if e.keycode == 68 or e.keycode == 39:
            self.grid.right()
            self.render()
            return

        if e.keycode == 65 or e.keycode == 37:
            self.grid.left()
            self.render()
            return

        if e.keycode == 81:
            self.grid.turn_left()
            self.render()
            return

        if e.keycode == 69 or e.keycode == 38 or e.keycode == 87:
            self.grid.turn_right()
            self.render()
            return

        if e.keycode == 40 or e.keycode == 83 or e.keycode == 32:
            self.update(soft_drop=True)
            self.render()
            return

    def render(self):
        self.img = ImageTk.PhotoImage(self.grid.draw(20, 20, 1))
        self.img_label.config(image=self.img)

    def update(self, soft_drop=False):
        full_rows, continuous_soft_drop = self.grid.update(soft_drop=soft_drop)
        self.render()

        if full_rows:
            self.broken_lines += full_rows
            self.update_level()

        self.score += self.get_score(full_rows) + continuous_soft_drop

        if self.grid.allow_spawn():
            self.grid.spawn_figure(self.get_next_piece())

        print(f"cycle: {self.cycle}; score: {self.score}; level: {self.level}; speed: {self.speed}")
        self.cycle += 1


root = tk.Tk()
root.title("Tetris")

game = Game(root)


def update():
    game.update()
    root.after(game.speed, update)


root.after(game.speed, update)
root.mainloop()
