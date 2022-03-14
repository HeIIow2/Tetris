import cell as cl
import figure as fg
import copy
import random
from PIL import Image

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
                row.append(cl.Cell())
            self.grid.append(row)

    def reset_grid(self):
        self.grid = []
        self.lowest_frees = [self.grid_height-1]*self.grid_width

        for i in range(self.grid_height):
            row = []
            for j in range(self.grid_width):
                row.append(cl.Cell())
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

    def occupies(self, fig: fg.Figure):
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

    def is_placeable(self, fig: fg.Figure):
        for i, row in enumerate(fig.grid):
            for j, cell in enumerate(row):
                if cell is None:
                    continue

                if self.is_occupied(fig.x + j, fig.y + i):
                    return False

        return True

    def get_min_ghost(self, figure: fg.Figure):
        min_ghost = self.grid_height
        for x, y, cell in figure.get_lower_bounds():
            if self.lowest_frees[x]-y < min_ghost:
                min_ghost = self.lowest_frees[x]-y

        return min_ghost

    def hard_drop(self, index: int):
        min_ghost = self.get_min_ghost(self.figures[index])
        self.figures[index].y += min_ghost
        return min_ghost

    def place(self, figure: fg.Figure):
        for piece in figure.get_pieces():
                x, y, cell = piece
                self.grid[y][x] = cell
                    
                # the -1 is because not the full cell is needet, but the empty one above
                if self.lowest_frees[x] > y-1:
                    self.lowest_frees[x] = y-1

        return figure.soft_drop

    def update(self, soft_drop=False, hard_drop=False):
        continuous_soft_drop = 0
        hard_drop_ = 0
        to_pop = []
        for i, figure in enumerate(self.figures):
            if hard_drop:
                hard_drop_ += self.hard_drop(i)
                self.place(figure)
                to_pop.append(i)
                continue
            if soft_drop:
                figure.soft_drop += 1
            else:
                figure.soft_drop = 0
            figure.y += 1
            if not self.is_placeable(figure):
                # append figure to grid and delete
                figure.y -= 1
                continuous_soft_drop += self.place(figure)

                to_pop.append(i)

        for i in to_pop:
            self.figures.pop(i)

        # Wenn eine Zeile voll ist, lösche diese
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
            # wenn reihen zerstört wurden müssen auch die upper bounds geupdated werden
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

        return number_of_full_row, continuous_soft_drop, game_over_, hard_drop_

    def spawn_figure(self, figure: fg.Figure):
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
                
            min_ghost = self.get_min_ghost(figure)
            
            for x, y, cell in figure.get_pieces():
                temp_grid[y][x] = cell
                # if the block is drawn under another one it wont work
                # so in that case we ignore it and dont draw it because the likelyhood is small.
                if min_ghost > 0:
                    temp_grid[y+min_ghost][x] = cl.Cell(mode=cell.mode, ghost=True)

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
