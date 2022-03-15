import grid as gd
import queue_ as qe
import description as dp
import cycle

import tkinter
from PIL import ImageTk

class Game:
    def __init__(self, ui_frame, figures: list, queue_len=5, queue_width=4, width=10, height=20, level=1, start_speed=800, start_score=0, level_cap=20):
        self.queue_len = queue_len
        self.cycle = 0

        self.grid = gd.Grid(width=width, height=height)
        self.queue = qe.Queue(length=queue_len, figures=figures, width=queue_width, height=height)

        self.ui_frame = ui_frame
        self.ui_frame.bind('<KeyPress>', self.on_key_press)

        self.status_label = tkinter.Label(self.ui_frame, text="Level 1", font=('font-family font-size style', 25))
        self.status_label.grid(row=0, column=0, columnspan=3)

        self.queue_label = tkinter.Label(self.ui_frame)
        self.queue_image = None
        self.render_queue()
        self.queue_label.grid(row=1, column=0)

        self.img_label = tkinter.Label(self.ui_frame)
        self.img = None
        self.render()
        self.img_label.grid(row=1, column=1)

        self.description_frame = tkinter.Frame(self.ui_frame)
        self.description = dp.Description(self.description_frame, [("level", level), ("score", start_score), ("speed", start_speed), ("rows", "0/10")])
        self.description_frame.grid(row=1, column=2)

        self.game_over = False
        self.pause = False

        self.score = start_score
        self.level = level
        self.level_cap = level_cap
        self.speed = start_speed
        
        self.set_speed()

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

        if e.keycode == 40 or e.keycode == 83:
            self.update(soft_drop=True)
            return

        if e.keycode == 32:
            self.update(hard_drop=True)
            return

    def render(self):
        self.img = ImageTk.PhotoImage(self.grid.draw(20, 20, 1))
        self.img_label.config(image=self.img)

    def render_queue(self):
        self.queue_image = ImageTk.PhotoImage(self.queue.draw(20, 20, 1))
        self.queue_label.config(image=self.queue_image)

    def update(self, resume=False, soft_drop=False, hard_drop=False):
        doesnt_run = False

        if self.pause:
            return doesnt_run
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
                return doesnt_run

        full_rows, continuous_soft_drop, self.game_over, hard_drop = self.grid.update(soft_drop=soft_drop, hard_drop=hard_drop)
        self.render()

        if full_rows:
            self.broken_lines += full_rows
            self.update_level()

        self.score += self.get_score(full_rows) + continuous_soft_drop + hard_drop
        self.description.set_element("score", self.score)

        if self.grid.allow_spawn():
            self.grid.spawn_figure(self.queue.next_piece())
            self.render_queue()

        print(f"cycle: {self.cycle}; score: {self.score}; level: {self.level}; speed: {self.speed}")

        if self.game_over:
            self.status_label.config(text="Game Over")
            return doesnt_run

        self.cycle += 1

        return True

    def get_cycle(self):
        return cycle.Cycle(self.level, self.score, self.grid)
