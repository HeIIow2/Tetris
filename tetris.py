import copy
import tkinter as tk
from PIL import Image, ImageDraw, ImageTk

class Cell:
    def __init__(self, falling_=False, mode=0):
        self.falling = falling_
        self.mode = mode
        
    def draw(self, width:int, height:int):
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
    def __init__(self, size:int, matrix:list, mode:int, x=0, y=0):
        self.x = x
        self.y = y
        self.real_y = y
        self.width = size
        self.height = size
        self.mode = mode
        
        self.grid = []
        
        for i, elem in enumerate(matrix):
            if i%self.width == 0:
                self.grid.append([])
                
            if bool(elem):
                self.grid[-1].append(Cell(falling_=True, mode=self.mode))
            else:
                self.grid[-1].append(None)
        self.update_y()
        #self.output()
        
    def update_y(self):
        for i, row in enumerate(self.grid):
            break_ = False
            for cell in row:
                if cell is not None:
                    break_ = True
                    break
            if break_:
                print("wee")
                break

                
        self.y = -len(self.grid) + i
        print(self.y)
            
    def rotate_left(self):
        temp_grid = copy.deepcopy(self.grid)
    
        for i in range(self.height):
            for j in range(self.width):
                temp_grid[self.width-j-1][i] = self.grid[i][j]
        
        self.grid = temp_grid
        self.update_y()
        #self.output()
        
    def rotate_right(self):
        temp_grid = copy.deepcopy(self.grid)
    
        for i in range(self.height):
            for j in range(self.width):
                temp_grid[j][self.height-i-1] = self.grid[i][j]
        
        self.grid = temp_grid
        self.update_y()
        self.output()
        
                
    def output(self):
        for row in self.grid:
            print(row)  
        print()
            

class Grid:
    def __init__(self, width: int, height: int):
        self.figures = []
        self.grid_width = width
        self.grid_height = height
        
        self.grid = []

        for i in range(height):
            row=[]
            for j in range(width):
                row.append(Cell())        
            self.grid.append(row)
            
    def is_falling(self):
        for i in range(self.grid_height):
            for j in range(self.grid_width):
                if self.grid[i][j].falling:
                    return True
                    
        return False
        
    def is_occupied(self, x:int, y:int):
        """
        if y < 0 or x < 0:
            return True"""
            
        if y >= self.grid_height-1:
            return True
            
        if x >= self.grid_width-1:
            return True
            
        return False
        
    def is_placeabel(self, fig:Figure):
        f_x = fig.x
        f_y = fig.y
        
        for i, row in enumerate(fig.grid):
            for j, cell in enumerate(row):
                if cell is None:
                    continue
                    
                if self.is_occupied(f_x+j, f_y+i):
                    return False
                    
        return True
    
    def update(self):
        for i, figure in enumerate(self.figures):
            figure.y += 1
            if not self.is_placeabel(figure):
                exit(666)
            
        
            
    
    def spawn_figure(self, figure:Figure, x:int):
        figure = copy.deepcopy(figure)
        figure.x = x
        
        self.figures.append(figure)
                    
    
    def draw(self, width:int, height:int, spacing:int):
        temp_grid = copy.deepcopy(self.grid)
        for i, fig in enumerate(self.figures):
            x = fig.x
            y = fig.y
            
            f_x = fig.x
            f_y = fig.y
            
            for i, row in enumerate(fig.grid):
                for j, cell in enumerate(row):
                    if cell is None:
                        continue
                    if f_y+i < 0:
                        continue
                    temp_grid[f_y+i][f_x+j] = cell
    
        img_width = width*self.grid_width + spacing * (self.grid_width+1)
        img_height = height*self.grid_height + spacing * (self.grid_height+1)
        
        img = Image.new("RGB", (img_width, img_height), color="#fff")
        
        y = spacing
        for i in range(self.grid_height):
            x = spacing
            for j in range(self.grid_width):
                Image.Image.paste(img, temp_grid[i][j].draw(width, height), (x, y))
                x += spacing + width
            y += spacing + height
                
        return img
        
        
speed = 500

FIGURES = [
        Figure(4, [0,0,0,0,1,1,1,1,0,0,0,0,0,0,0,0], 1),
        Figure(3, [1,0,0,1,1,1,0,0,0], 2),
        Figure(3, [0,0,1,1,1,1,0,0,0], 3),
        Figure(2, [1,1,1,1], 4),
        Figure(3, [0,1,1,1,1,0,0,0,0], 5),
        Figure(3, [0,1,0,1,1,1,0,0,0], 6),
        Figure(3, [1,1,0,0,1,1,0,0,0], 7),
    ]

root = tk.Tk()
root.title("Tetris")
label = tk.Label(root)
img = None 

grid = Grid(7,10)
grid.spawn_figure(FIGURES[0], 2)

def refresh_image():
    global img
    img = ImageTk.PhotoImage(grid.draw(20, 20, 1))
    label.config(image=img)
      
refresh_image()
label.pack()

def update():
    global speed
    
    print("update")
    refresh_image()
    grid.update()
    root.after(speed, update)

root.after(speed, update)
root.mainloop()
