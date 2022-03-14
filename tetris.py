import tkinter as tk
import json
import game as gm

with open("config.json", "r") as config_file:
    config_data = json.loads(config_file.read())
    grid_width = config_data['grid_width']
    grid_height = config_data['grid_height']
    queue_len = config_data['queue_len']
    start_level = config_data['start_level']
    level_cap = config_data['level_cap']
    raw_figures = config_data['figures']
    figures = []
    
    max_width = 0
    for raw_figure in raw_figures:
        anything = [0] * len(raw_figure[0])
        figure = [len(raw_figure)]
        for row in raw_figure:
            for i, cell in enumerate(row):
                figure.append(cell)
                anything[i] = anything[i] or cell
                
        real_width = len(anything)
        
        for cell in anything:
            if cell:
                break
            real_width -= 1
            
        for cell in list(reversed(anything)):
            if cell:
                break
            real_width -= 1
            
        if real_width > max_width:
            max_width = real_width
                
        figures.append(figure)

root = tk.Tk()
root.title("Tetris")

game = gm.Game(root, figures, width=grid_width, height=grid_height, queue_width=max_width, queue_len=queue_len, level=start_level, level_cap=level_cap)

def update():
    game.update()
    root.after(game.speed, update)


root.after(game.speed, update)
root.mainloop()