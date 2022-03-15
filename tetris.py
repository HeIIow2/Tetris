import game as gm
import folders as fd

import tkinter as tk

root = tk.Tk()
root.title("Tetris")

folders = fd.Folders()

game = folders.get_game(root=root)
last_run = True

def on_pause():
    print("paused")

def on_resume():
    print("resumed")

def update():
    global last_run

    current_run = game.update()
    #save_binary.save_grid(game.grid)
    if last_run and not current_run:
        on_pause()
    elif not last_run and current_run:
        on_resume()

    last_run = current_run
    root.after(game.speed, update)


root.after(game.speed, update)
root.mainloop()