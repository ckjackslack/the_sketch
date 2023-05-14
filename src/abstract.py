import random

from helpers import random_color
from sketch_gif import Sketch, run_sketch


class AbstractLineSketch(Sketch):
    def setup(self):
        self.num_lines = 100
        self.lines = []

        for _ in range(self.num_lines):
            x1 = random.randint(0, self.canvas.width)
            y1 = random.randint(0, self.canvas.height)
            x2 = random.randint(0, self.canvas.width)
            y2 = random.randint(0, self.canvas.height)
            color = random_color()
            self.lines.append(((x1, y1), (x2, y2), color))

    def update(self):
        for i in range(self.num_lines):
            x1, y1 = self.lines[i][0]
            x2, y2 = self.lines[i][1]
            x1 += random.randint(-5, 5)
            y1 += random.randint(-5, 5)
            x2 += random.randint(-5, 5)
            y2 += random.randint(-5, 5)
            self.lines[i] = ((x1, y1), (x2, y2), self.lines[i][2])

    def draw(self):
        self.canvas.draw.rectangle(
            (0, 0, self.canvas.width, self.canvas.height),
            fill=(255, 255, 255)  # White background
        )

        for line in self.lines:
            x1, y1 = line[0]
            x2, y2 = line[1]
            color = line[2]
            self.canvas.draw.line((x1, y1, x2, y2), fill=color, width=2)


if __name__ == "__main__":
    run_sketch(AbstractLineSketch, 800, 600, frame_limit=200)
