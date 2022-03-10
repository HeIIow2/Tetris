import tkinter as tk
import mechanics

root = tk.Tk()
root.title("Tetris")

game = mechanics.Game(root)

def update():
    game.update()
    root.after(game.speed, update)


root.after(game.speed, update)
root.mainloop()
