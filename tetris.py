import copy
import tkinter as tk
from PIL import Image, ImageDraw, ImageTk
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

        self.grid = []
        for i, elem in enumerate(matrix):
            if i % self.width == 0:
                self.grid.append([])

            if bool(elem):
                self.grid[-1].append(Cell(falling_=True, mode=self.mode))
            else:
                self.grid[-1].append(None)

        self.update_y()

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

    def output(self):
        for row in self.grid:
            print(row)
        print()


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

    def update(self):
        for i, figure in enumerate(self.figures):
            figure.y += 1
            if not self.is_placeable(figure):
                figure.y -= 1
                self.to_pop.append(i)

    def spawn_figure(self, figure: Figure):
        figure = copy.deepcopy(figure)
        figure.randomize_rotation()
        figure.x = random.randint(0, self.grid_width - figure.width)

        self.figures.append(figure)

    def draw(self, width: int, height: int, spacing: int):
        temp_grid = copy.deepcopy(self.grid)
        for n, fig in enumerate(self.figures):
            x = fig.x
            y = fig.y

            f_x = fig.x
            f_y = fig.y

            for i, row in enumerate(fig.grid):
                for j, cell in enumerate(row):
                    if cell is None:
                        continue
                    if f_y + i < 0:
                        continue

                    if n in self.to_pop:
                        cell.falling = False
                        self.grid[f_y + i][f_x + j] = cell
                        temp_grid[f_y + i][f_x + j] = cell
                    else:
                        temp_grid[f_y + i][f_x + j] = cell

            if n in self.to_pop:
                self.figures.pop(n)

        self.to_pop = []

        # wenn in der obersten Zeile ein block ist, game over
        first_row = self.grid[0]
        for cell in first_row:
            if cell.mode != 0:
                self.game_over()
                break

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


speed = 500

FIGURES = [
    Figure(4, [0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0], 1),
    Figure(3, [1, 0, 0, 1, 1, 1, 0, 0, 0], 2),
    Figure(3, [0, 0, 1, 1, 1, 1, 0, 0, 0], 3),
    Figure(2, [1, 1, 1, 1], 4),
    Figure(3, [0, 1, 1, 1, 1, 0, 0, 0, 0], 5),
    Figure(3, [0, 1, 0, 1, 1, 1, 0, 0, 0], 6),
    Figure(3, [1, 1, 0, 0, 1, 1, 0, 0, 0], 7),
]

root = tk.Tk()
root.title("Tetris")
label = tk.Label(root)
img = None

grid = Grid(14, 20)


def refresh_image():
    global img
    img = ImageTk.PhotoImage(grid.draw(20, 20, 1))
    label.config(image=img)


refresh_image()
label.pack()

cycle = 0


def update():
    global speed
    global cycle

    print(f"update {cycle}")
    grid.update()
    refresh_image()
    root.after(speed, update)

    if grid.allow_spawn():
        grid.spawn_figure(FIGURES[random.randrange(len(FIGURES))])

    cycle += 1


def on_key_press(e):
    if e.keycode == 68 or e.keycode == 39:
        grid.right()
        refresh_image()
        return

    if e.keycode == 65 or e.keycode == 37:
        grid.left()
        refresh_image()
        return

    if e.keycode == 81:
        grid.turn_left()
        refresh_image()
        return

    if e.keycode == 69:
        grid.turn_right()
        refresh_image()
        return

    if e.keycode == 40 or e.keycode == 83 or e.keycode == 32:
        grid.update()
        refresh_image()
        return
    print(e)


root.bind('<KeyPress>', on_key_press)

root.after(speed, update)
root.mainloop()
