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
        if mode:
            mode -= 1
            self.mode = mode%(len(colors)-1)
            self.mode += 1
        else:
            self.mode = mode
        self.primary_color = colors[self.mode]
        self.secondary_color = (int(self.primary_color[0]/2), int(self.primary_color[1]/2), int(self.primary_color[2]/2))
        self.ghost = ghost

    def draw(self, width: int, height: int, ghost=False):
        """
        stick
        blue bend
        orange bend
        square
        left up
        crossing
        right up
        """
        
        if not self.ghost:
            return Image.new("RGB", (width, height), color='#%02x%02x%02x' % self.primary_color)

        return Image.new("RGB", (width, height), color='#%02x%02x%02x' % self.secondary_color)
