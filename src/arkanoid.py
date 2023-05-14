import math

from sketch_gif import Sketch, run_sketch


class ArkanoidSketch(Sketch):
    def setup(self):
        self.center_x = self.canvas.width // 2
        self.center_y = self.canvas.height // 2
        self.radius = min(self.center_x, self.center_y) // 2
        self.angle = 0
        self.triangle_size = 20
        self.triangle_speed = 0.03

    def update(self):
        self.angle += self.triangle_speed

    def draw(self):
        self.canvas.draw.rectangle(
            (0, 0, self.canvas.width, self.canvas.height),
            fill=(0, 0, 0)  # Black background
        )

        num_triangles = 6
        for i in range(num_triangles):
            angle = self.angle + (2 * math.pi * i / num_triangles)
            x = self.center_x + int(self.radius * math.cos(angle))
            y = self.center_y + int(self.radius * math.sin(angle))
            color = self.get_color(i, num_triangles)
            self.draw_triangle(x, y, self.triangle_size, color)

    def draw_triangle(self, x, y, size, color):
        points = [
            (x - size, y),
            (x + size, y),
            (x, y - size)
        ]
        self.canvas.draw.polygon(points, fill=color)

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
    run_sketch(ArkanoidSketch, 800, 600, frame_limit=200)
