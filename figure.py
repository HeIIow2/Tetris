import cell
import random
import copy
from PIL import Image

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
                self.grid[-1].append(cell.Cell(falling_=True, mode=self.mode))
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
                Image.Image.paste(img, cell.Cell().draw(width, height), (x, y))
                x += spacing + width

            for j in range(self.width):
                if self.grid[i][j] is None:
                    Image.Image.paste(img, cell.Cell().draw(width, height), (x, y))
                else:
                    Image.Image.paste(img, self.grid[i][j].draw(width, height), (x, y))
                x += spacing + width

            for n in range(margin_right):
                Image.Image.paste(img, cell.Cell().draw(width, height), (x, y))
                x += spacing + width

            y += spacing + height

        return img