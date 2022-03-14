from PIL import Image

class Cell:
    def __init__(self, falling_=False, mode=0, ghost=False):
        colors = [
            (0, 0, 0),
            (47, 150, 175),
            (47, 68, 175),
            (175, 109, 47),
            (175, 175, 47),
            (60, 175, 47),
            (150, 47, 175),
            (175, 47, 47),
            (190, 71, 214),
            (71, 214, 191)
        ]
        self.falling = falling_
        if mode:
            mode -= 1
            self.mode = mode%(len(colors)-1)
            self.mode += 1
        else:
            self.mode = mode
        self.color = colors[self.mode]
        self.ghost = ghost

    def draw(self, width: int, height: int):
        """
        stick
        blue bend
        orange bend
        square
        left up
        crossing
        right up
        """
        
        if self.ghost:
            _color = (int(self.color[0]/2), int(self.color[1]/2), int(self.color[2]/2))
        else:
            _color = tuple(self.color)

        return Image.new("RGB", (width, height), color='#%02x%02x%02x' % _color)
