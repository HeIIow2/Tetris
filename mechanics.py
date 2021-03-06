import copy
import tkinter
import tkinter as tk
from PIL import Image, ImageTk
import random


class Cell:
    def __init__(self, falling_=False, mode=0, ghost=False):
        self.falling = falling_
        self.mode = mode
        self.ghost = ghost

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
        if self.ghost:
            color = str(colors[self.mode])[1:]
            
            color_list = []
            color_str="#"
            for i in range(3):
                new_thing = int(color[i*2:i*2+2],16)
                new_thing = int(new_thing / 2)
                color_str+=hex(new_thing).rstrip("L").lstrip("0x").zfill(2)
            return Image.new("RGB", (width, height), color=color_str)

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
        self.lower_bounds = []
        
        for i, elem in enumerate(matrix):
            if i % self.width == 0:
                self.grid.append([])

            if bool(elem):
                self.grid[-1].append(Cell(falling_=True, mode=self.mode))
            else:
                self.grid[-1].append(None)

        self.update_y()
        self.update_lower_bounds()

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
        
        self.update_lower_bounds()

    def rotate_right(self):
        temp_grid = copy.deepcopy(self.grid)

        for i in range(self.height):
            for j in range(self.width):
                temp_grid[j][self.height - i - 1] = self.grid[i][j]

        self.grid = temp_grid
        
        self.update_lower_bounds()

    def update_lower_bounds(self):
        self.lower_bounds = []
        for x in range(self.width):
            for y, row in reversed(list(enumerate(self.grid))):
                if row[x] is None:
                    continue
                cell = copy.deepcopy(row[x])
                cell.ghost = True
                self.lower_bounds.append((x, y, cell))
                break

    def get_lower_bounds(self):
        lower_bounds = []
        
        for x, y, cell in self.lower_bounds:
            lower_bounds.append((self.x + x, self.y + y, cell))
    
        return lower_bounds

    def draw(self, grid_width: int, width: int, height: int, spacing: int):
        img_width = width * grid_width + spacing * (grid_width + 1)
        img_height = height * self.height + spacing * (self.height + 1)

        margin_left = int((grid_width-self.width)/2)
        margin_right = margin_left + (grid_width-self.width)%2

        img = Image.new("RGB", (img_width, img_height), color="#666")

        y = spacing
        for i in range(self.height):
            x = spacing
            for n in range(margin_left):
                Image.Image.paste(img, Cell().draw(width, height), (x, y))
                x += spacing + width

            for j in range(self.width):
                if self.grid[i][j] is None:
                    Image.Image.paste(img, Cell().draw(width, height), (x, y))
                else:
                    Image.Image.paste(img, self.grid[i][j].draw(width, height), (x, y))
                x += spacing + width

            for n in range(margin_right):
                Image.Image.paste(img, Cell().draw(width, height), (x, y))
                x += spacing + width

            y += spacing + height

        return img


class Grid:
    def __init__(self, width: int, height: int):
        self.figures = []
        self.to_pop = []
        self.grid_width = width
        self.grid_height = height

        self.grid = []
        # saving the cell of the first piece you encounter going from the top for each collumn
        self.lowest_frees = [self.grid_height-1]*self.grid_width

        for i in range(height):
            row = []
            for j in range(width):
                row.append(Cell())
            self.grid.append(row)

    def reset_grid(self):
        self.grid = []
        self.lowest_frees = [self.grid_height-1]*self.grid_width

        for i in range(self.grid_height):
            row = []
            for j in range(self.grid_width):
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

    def occupies(self, fig: Figure):
        f_x = fig.x
        f_y = fig.y
        
        occupied_fields = 0

        for i, row in enumerate(fig.grid):
            for j, cell in enumerate(row):
                if cell is None:
                    continue

                if self.is_occupied(f_x + j, f_y + i):
                    occupied_fields += 1

        return occupied_fields

    def is_placeable(self, fig: Figure):
        for i, row in enumerate(fig.grid):
            for j, cell in enumerate(row):
                if cell is None:
                    continue

                if self.is_occupied(fig.x + j, fig.y + i):
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
                # append figure to grid and delete
                figure.y -= 1
                continuous_soft_drop += figure.soft_drop

                for piece in figure.get_pieces():
                    x, y, cell = piece
                    self.grid[y][x] = cell
                    
                    # the -1 is because not the full cell is needet, but the empty one above
                    if self.lowest_frees[x] > y-1:
                        self.lowest_frees[x] = y-1

                to_pop.append(i)

        for i in to_pop:
            self.figures.pop(i)

        # Wenn eine Zeile voll ist, l??sche diese
        number_of_full_row = 0
        deleted_some_rows = False
        for i, row in enumerate(self.grid):
            is_full = True
            for cell in row:
                if cell.mode == 0:
                    is_full = False

            if is_full:
                deleted_some_rows = True
                number_of_full_row += 1
                self.remove_row(i)
                
        if deleted_some_rows:
            # wenn reihen zerst??rt wurden m??ssen auch die upper bounds geupdated werden
            for x in range(self.grid_width):
                for y in range(self.grid_height):
                    if self.grid[y][x].mode != 0:
                        self.lowest_frees[x] = y-1
                        break
                else:
                    self.lowest_frees[x] = y

        # wenn in der obersten Zeile ein block ist, game over
        first_row = self.grid[0]
        game_over_ = False
        for cell in first_row:
            if cell.mode != 0:
                game_over_ = True

        return number_of_full_row, continuous_soft_drop, game_over_

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
                
            min_ghost = self.grid_height
            for x, y, cell in figure.get_lower_bounds():
                if self.lowest_frees[x]-y < min_ghost:
                    min_ghost = self.lowest_frees[x]-y
            
            for x, y, cell in figure.get_pieces():
                temp_grid[y][x] = cell
                # if the block is drawn under another one it wont work
                # so in that case we ignore it and dont draw it because the likelyhood is small.
                if min_ghost > 0:
                    temp_grid[y+min_ghost][x] = Cell(mode=cell.mode, ghost=True)

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
        # self.is_placeable(self.figures[index])
        original_occupation = self.occupies(self.figures[index])
        if not original_occupation:
            return True
            
        moving_x = 0
        moving_y = 0
        
        self.figures[index].x += 1
        current_occupies = self.occupies(self.figures[index])
        if not current_occupies:
            return True
        if current_occupies < original_occupation:
            moving_x = 1
        else:
            self.figures[index].x -= 2
            current_occupies = self.occupies(self.figures[index])
            if not current_occupies:
                return True
            if current_occupies < original_occupation:
                moving_x = -1
            else:
                self.figures[index].x += 1
                self.figures[index].y -= 1
                moving_x = 0
                moving_y = -1
                current_occupies = self.occupies(self.figures[index])
                if not current_occupies:
                    return True
                if not current_occupies < original_occupation:
                    self.figures[index].y += 1
                    return False
                   
        m = 0
        threshold = 3
        while not self.is_placeable(self.figures[index]):
            self.figures[index].x += moving_x
            self.figures[index].y += moving_y
            if m > threshold:
                self.figures[index].x -= moving_x * threshold
                self.figures[index].y -= moving_y * threshold
                return False
            m += 1
                   
        return True        

    def turn_right(self):
        for i in range(len(self.figures)):
            self.figures[i].rotate_right()
            if not self.move_in_bounds(i):
                self.figures[i].rotate_left()

    def turn_left(self):
        for i in range(len(self.figures)):
            self.figures[i].rotate_left()
            if not self.move_in_bounds(i):
                self.figures[i].rotate_right()

    def allow_spawn(self):
        return len(self.figures) == 0


class Description:
    def __init__(self, root, elements: list):
        self.elements = {}
        for i, element_ in enumerate(elements):
            element, value = element_
            self.elements[element] = tkinter.Label(root, text=f"{element}: {value}")
            self.elements[element].grid(row=i, column=0)

    def set_element(self, element, value):
        if element not in self.elements:
            return

        self.elements[element].config(text=f"{element}: {value}")


class Queue:
    def __init__(self, length: int, height: int, width: int):
        self.grid = []

        self.grid_height = height
        self.grid_width = width

        for i in range(height):
            row = []
            for j in range(width):
                row.append(Cell())
            self.grid.append(row)

        self.prev_piece_ind = -1

        self.queue = []
        for i in range(length):
            self.queue.append(self.get_random_piece())

    def get_random_piece(self):
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

    def next_piece(self):
        next_piece_ = self.queue[0]
        self.queue.pop(0)

        self.queue.append(self.get_random_piece())
        return next_piece_

    def draw(self, width: int, height: int, spacing: int):
        img_height = 0
        figure_images = []
        for figure in self.queue:
            figure_images.append(figure.draw(grid_width=4, width=width, height=height, spacing=spacing))
            img_height += figure_images[-1].height

        img_width = width * 4 + spacing * (4 + 1)

        img = Image.new("RGB", (img_width, img_height), color="#666")
        current_height = 0
        for image in figure_images:
            img.paste(image, (0, current_height))

            current_height += image.height

        return img


class Game:
    def __init__(self, ui_frame, queue_len=5, width=10, height=20, level=1, start_speed=800, start_score=0, level_cap=20):
        self.queue_len = queue_len
        self.cycle = 0

        self.grid = Grid(width=width, height=height)
        self.queue = Queue(queue_len, width=4, height=height)

        self.ui_frame = ui_frame
        self.ui_frame.bind('<KeyPress>', self.on_key_press)

        self.status_label = tk.Label(self.ui_frame, text="Level 1", font=('font-family font-size style', 25))
        self.status_label.grid(row=0, column=0, columnspan=3)

        self.queue_label = tkinter.Label(self.ui_frame)
        self.queue_image = None
        self.render_queue()
        self.queue_label.grid(row=1, column=0)

        self.img_label = tkinter.Label(self.ui_frame)
        self.img = None
        self.render()
        self.img_label.grid(row=1, column=1)

        self.description_frame = tk.Frame(self.ui_frame)
        self.description = Description(self.description_frame, [("level", level), ("score", start_score), ("speed", start_speed), ("rows", "0/10")])
        self.description_frame.grid(row=1, column=2)

        self.game_over = False
        self.pause = False

        self.score = start_score
        self.level = level
        self.level_cap = level_cap
        self.speed = start_speed

        self.broken_lines = 0

    def reset_level(self):
        self.score = 0
        self.level = 1
        self.broken_lines = 0

        self.status_label.config(text="Level: 1")

        self.description.set_element("score", self.score)
        self.description.set_element("level", self.level)
        self.update_level()

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

        self.description.set_element("speed", self.speed)

    def get_score(self, broken_rows: int):
        # https://tetris.fandom.com/wiki/Scoring

        POINTS = [0, 40, 100, 300, 1200]

        return POINTS[broken_rows]*self.level

    def update_level(self):
        # https://gaming.stackexchange.com/questions/379636/how-does-the-leveling-system-on-tetris-work

        level = self.level
        if level > self.level_cap:
            level = self.level_cap
            self.description.set_element("rows", f"{self.broken_lines}/inf")
        required_lines = level * 10

        self.description.set_element("rows", f"{self.broken_lines}/{required_lines}")

        if self.broken_lines >= required_lines:
            self.broken_lines -= required_lines
            self.level += 1
            self.description.set_element("level", self.level)
            self.status_label.config(text=f"Level: {self.level}")
            self.set_speed()
            
        required_lines = self.level * 10
        self.description.set_element("rows", f"{self.broken_lines}/{required_lines}")

    def on_key_press(self, e):
        if self.pause:
            self.pause = False
            self.status_label.config(text=f"Level: {self.level}")
            self.update()
        elif e.keycode == 27:
            self.pause = True
            self.status_label.config(text=f"Pause")
            return
    
        if self.game_over:
            self.update(resume=True)

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
            return

    def render(self):
        self.img = ImageTk.PhotoImage(self.grid.draw(20, 20, 1))
        self.img_label.config(image=self.img)

    def render_queue(self):
        self.queue_image = ImageTk.PhotoImage(self.queue.draw(20, 20, 1))
        self.queue_label.config(image=self.queue_image)

    def update(self, resume=False, soft_drop=False):
        if self.pause:
            return
        if not self.ui_frame.focus_get():
            self.status_label.config(text=f"Pause")
            
            while not self.ui_frame.focus_get():
                self.ui_frame.update()
            
            self.status_label.config(text=f"Level: {self.level}")
            
        if self.game_over:
            if resume:
                self.grid.reset_grid()
                self.reset_level()
                self.game_over = True
            else:
                return

        full_rows, continuous_soft_drop, self.game_over = self.grid.update(soft_drop=soft_drop)
        self.render()

        if full_rows:
            self.broken_lines += full_rows
            self.update_level()

        self.score += self.get_score(full_rows) + continuous_soft_drop
        self.description.set_element("score", self.score)

        if self.grid.allow_spawn():
            self.grid.spawn_figure(self.queue.next_piece())
            self.render_queue()

        print(f"cycle: {self.cycle}; score: {self.score}; level: {self.level}; speed: {self.speed}")

        if self.game_over:
            self.status_label.config(text="Game Over")
            return

        self.cycle += 1


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Tetris")

    game = Game(root)


    def update():
        game.update()
        root.after(game.speed, update)


    root.after(game.speed, update)
    root.mainloop()
