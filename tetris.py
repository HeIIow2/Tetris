import tkinter as tk
import json
import mechanics

with open("config.json", "r") as config_file:
    config_data = json.loads(config_file.read())
    grid_width = config_data['grid_width']
    grid_height = config_data['grid_height']
    queue_len = config_data['queue_len']
    start_level = config_data['start_level']
    level_cap = config_data['level_cap']
    raw_figures = config_data['figures']
    figures = []
    
    for raw_figure in raw_figures:
        figure = [len(raw_figure)]
        for row in raw_figure:
            for cell in row:
                figure.append(cell)
                
        figures.append(figure)

root = tk.Tk()
root.title("Tetris")

game = mechanics.Game(root, figures, width=grid_width, height=grid_height, queue_len=queue_len, level=start_level, level_cap=level_cap)

def update():
    game.update()
    root.after(game.speed, update)


root.after(game.speed, update)
root.mainloop()