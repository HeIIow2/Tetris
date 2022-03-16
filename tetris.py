import game as gm
import folders as fd

import tkinter as tk

root = tk.Tk()
root.title("Tetris")

folders = fd.Folders()

game = folders.get_game(root=root)
last_run = True

paused = False

def on_pause():
    global paused
    paused = True
    folders.dump_replay()
    print("paused")

def on_resume():
    global paused
    paused = False
    print("resumed")

def update():
    global last_run

    current_run = game.update()
    if not paused:
        folders.save_grid()
    if last_run and not current_run:
        on_pause()
    elif not last_run and current_run:
        on_resume()

    last_run = current_run
    root.after(game.speed, update)


root.after(game.speed, update)
root.mainloop()