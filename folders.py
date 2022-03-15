import grid as gd
import game as gm

import os
import time
import requests
import json


class Folders:
    def __init__(self, directory=None):
        if directory is None:
            BASE_DIR = os.getenv('APPDATA')
        else:
            BASE_DIR = directory
            if not os.path.exists(BASE_DIR):
                os.makedirs(BASE_DIR)
        FOLDER = "Tetris"
        self.PATH = os.path.join(BASE_DIR, FOLDER)

        if not os.path.exists(self.PATH):
            os.makedirs(self.PATH)

        REPLAY_FOLDER = "saves"
        CONFIG_FILE = "config.json"
        self.REPLAY_PATH = os.path.join(self.PATH, REPLAY_FOLDER)
        self.CONFIG_PATH = os.path.join(self.PATH, CONFIG_FILE)

        self.config = None
        self.is_connected = True
        self.download_config()

        if not os.path.exists(self.REPLAY_PATH):
            os.makedirs(self.REPLAY_PATH)

        self.grid_width = 10
        self.grid_height = 20
        self.queue_len = 5
        self.start_level = 1
        self.level_cap = 20
        self.raw_figures = [[[0, 0, 0, 0], [1, 1, 1, 1], [0, 0, 0, 0], [0, 0, 0, 0]], [[1, 0, 0], [1, 1, 1], [0, 0, 0]], [[0, 0, 1], [1, 1, 1], [0, 0, 0]], [[1, 1], [1, 1]], [[0, 1, 1], [1, 1, 0], [0, 0, 0]], [[0, 1, 0], [1, 1, 1], [0, 0, 0]], [[1, 1, 0], [0, 1, 1]]]

        if self.config is not None:
            self.grid_width = self.config["grid_width"]
            self.grid_height = self.config["grid_height"]
            self.queue_len = self.config["queue_len"]
            self.start_level = self.config["start_level"]
            self.level_cap = self.config["level_cap"]
            self.raw_figures = self.config["figures"]

        self.figures = []
        
        self.max_width = 0
        for raw_figure in self.raw_figures:
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
                
            if real_width > self.max_width:
                self.max_width = real_width
                    
            self.figures.append(figure)

            self.data = []
            self.creation_time = time.time()

    def read_config_file(self):
        with open(self.CONFIG_PATH, "r") as config_file:
            self.config = json.load(config_file)

    def download_config(self):
        config_url = "https://ln.topdf.de/tetris/config.json"
        timeout = 5

        if os.path.exists(self.CONFIG_PATH):
            self.read_config_file()
            return

        try:
            r = requests.get(config_url, timeout=timeout)
            self.config = r.json()
        except requests.exceptions.Timeout:
            self.is_connected = False
            return

        with open(self.CONFIG_PATH, "wb") as config_file:
            config_file.write(r.content)

    def get_game(self, root):
        return gm.Game(root, self.figures, width=self.grid_width, height=self.grid_height, queue_width=self.max_width, queue_len=self.queue_len, level=self.start_level, level_cap=self.level_cap)

    def save_grid(self, grid: gd.Grid):
        current_time = time.time() - self.creation_time


if __name__ == "__main__":
    folder = Folders()