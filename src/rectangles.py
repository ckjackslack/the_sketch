import random

from PIL import ImageDraw

from sketch_gif import Sketch, run_sketch
from helpers import random_color, clamp


class RectanglesSketch(Sketch):
    def setup(self):
        self.rectangles = []
        self.num_rectangles = 50

        for _ in range(self.num_rectangles):
            x = random.randint(0, self.canvas.width)
            y = random.randint(0, self.canvas.height)
            width = random.randint(10, 100)
            height = random.randint(10, 100)
            color = random_color()
            self.rectangles.append((x, y, width, height, color))

    def update(self):
        for i, (x, y, width, height, color) in enumerate(self.rectangles):
            # Update rectangle position
            x += random.randint(-5, 5)
            y += random.randint(-5, 5)

            # Clamp rectangle position within canvas bounds
            x = clamp(x, 0, self.canvas.width - width)
            y = clamp(y, 0, self.canvas.height - height)

            # Update rectangle size
            width += random.randint(-5, 5)
            height += random.randint(-5, 5)

            # Clamp rectangle size within certain bounds
            width = clamp(width, 10, 100)
            height = clamp(height, 10, 100)

            self.rectangles[i] = (x, y, width, height, color)

    def draw(self):
        self.canvas.draw.rectangle(
            (0, 0, self.canvas.width, self.canvas.height),
            fill=(0, 0, 0)  # Black background
        )

        for x, y, width, height, color in self.rectangles:
            self.canvas.draw.rectangle(
                (x, y, x + width, y + height),
                fill=color
            )


if __name__ == "__main__":
    run_sketch(RectanglesSketch, 800, 600, frame_limit=200)
