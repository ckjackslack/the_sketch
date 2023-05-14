import random

from sketch_gif import Sketch, run_sketch


class CirclesSketch(Sketch):
    def setup(self):
        self.circles = []

    def update(self):
        # Generate a new circle if there are less than 10 circles
        if len(self.circles) < 10:
            circle = self.generate_circle()
            if self.is_valid_circle(circle):
                self.circles.append(circle)

    def draw(self):
        self.canvas.draw.rectangle(
            (0, 0, self.canvas.width, self.canvas.height),
            fill=(0, 0, 0)  # Black background
        )

        for circle in self.circles:
            self.canvas.draw.ellipse(
                circle,
                fill=(255, 255, 255)  # White circle
            )

    def generate_circle(self):
        radius = random.randint(10, 50)
        x = random.randint(radius, self.canvas.width - radius)
        y = random.randint(radius, self.canvas.height - radius)
        return (x - radius, y - radius, x + radius, y + radius)

    def is_valid_circle(self, circle):
        for existing_circle in self.circles:
            if self.is_overlap(existing_circle, circle):
                return False
        return True

    def is_overlap(self, circle1, circle2):
        x1, y1, x2, y2 = circle1
        x3, y3, x4, y4 = circle2
        if x2 < x3 or x4 < x1 or y2 < y3 or y4 < y1:
            return False
        return True


if __name__ == "__main__":
    run_sketch(CirclesSketch, 800, 600)
