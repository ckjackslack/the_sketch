import random

from PIL import ImageFont

from sketch_gif import Sketch, run_sketch
from helpers import random_color


class MatrixSketch(Sketch):
    def setup(self):
        self.columns = self.canvas.width // 40
        self.font_size = 40
        self.drops = [0] * self.columns
        self.characters = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
        self.font = ImageFont.truetype(
            # "/usr/share/fonts/truetype/ubuntu/Ubuntu-M.ttf",
            "./clacon2.ttf",
            self.font_size,
        )

    def update(self):
        for i in range(self.columns):
            if random.random() < 0.1:
                self.drops[i] = 0
            self.drops[i] += 1

    def draw(self):
        self.canvas.draw.rectangle(
            (0, 0, self.canvas.width, self.canvas.height),
            fill=(0, 0, 0)  # Black background
        )

        for i in range(len(self.drops)):
            char_index = random.randint(0, len(self.characters) - 1)
            char = self.characters[char_index]
            x = i * self.font_size
            y = (self.drops[i] * self.font_size) % self.canvas.height
            color = random_color()
            color = color[0] | (color[1] << 8) | (color[2] << 16)  # Convert RGB tuple to integer color value
            self.canvas.draw.text((x, y), char, fill=color, font=self.font)


if __name__ == "__main__":
    run_sketch(MatrixSketch, 800, 600, frame_limit=300, fps=15)
