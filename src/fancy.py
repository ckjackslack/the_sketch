import math

from sketch_gif import Sketch, run_sketch


class FancySketch(Sketch):
    def setup(self):
        self.angle = 0
        self.radius = min(self.canvas.width, self.canvas.height) // 2

    def update(self):
        self.angle += 0.02

    def draw(self):
        self.canvas.draw.rectangle(
            (0, 0, self.canvas.width, self.canvas.height),
            fill=(0, 0, 0)  # Black background
        )

        num_circles = 10
        for i in range(num_circles):
            circle_radius = self.radius - i * (self.radius // num_circles)
            x = self.canvas.width // 2 + int(circle_radius * math.cos(self.angle * (i + 1)))
            y = self.canvas.height // 2 + int(circle_radius * math.sin(self.angle * (i + 1)))
            color = self.get_color(i, num_circles)
            self.canvas.draw.ellipse(
                (x - circle_radius, y - circle_radius, x + circle_radius, y + circle_radius),
                fill=color
            )

    def get_color(self, index, total):
        hue = int((index / total) * 255)
        saturation = 255
        value = 255
        return tuple(map(int, self.hsv_to_rgb(hue, saturation, value)))

    def hsv_to_rgb(self, h, s, v):
        if s == 0:
            return v, v, v
        region = h // 43
        remainder = (h - (region * 43)) * 6
        p = (v * (255 - s)) >> 8
        q = (v * (255 - ((s * remainder) >> 8))) >> 8
        t = (v * (255 - ((s * (255 - remainder)) >> 8))) >> 8
        if region == 0:
            return v, t, p
        elif region == 1:
            return q, v, p
        elif region == 2:
            return p, v, t
        elif region == 3:
            return p, q, v
        elif region == 4:
            return t, p, v
        else:
            return v, p, q


if __name__ == "__main__":
    run_sketch(FancySketch, 800, 800, frame_limit=200)
