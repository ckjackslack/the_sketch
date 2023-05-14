import random

from sketch_gif import Sketch, run_sketch


class WindowsScreensaverSketch(Sketch):
    def setup(self):
        self.balls = []
        self.num_balls = 10
        self.ball_radius = 20
        self.max_speed = 5
        self.colors = [
            (255, 0, 0),   # Red
            (0, 255, 0),   # Green
            (0, 0, 255),   # Blue
            (255, 255, 0), # Yellow
            (255, 0, 255), # Magenta
            (0, 255, 255)  # Cyan
        ]

        for _ in range(self.num_balls):
            x = random.randint(self.ball_radius, self.canvas.width - self.ball_radius)
            y = random.randint(self.ball_radius, self.canvas.height - self.ball_radius)
            dx = random.uniform(-self.max_speed, self.max_speed)
            dy = random.uniform(-self.max_speed, self.max_speed)
            color = random.choice(self.colors)
            self.balls.append((x, y, dx, dy, color))

    def update(self):
        for i, (x, y, dx, dy, color) in enumerate(self.balls):
            x += dx
            y += dy

            if x - self.ball_radius < 0 or x + self.ball_radius > self.canvas.width:
                dx = -dx
            if y - self.ball_radius < 0 or y + self.ball_radius > self.canvas.height:
                dy = -dy

            self.balls[i] = (x, y, dx, dy, color)

    def draw(self):
        self.canvas.draw.rectangle(
            (0, 0, self.canvas.width, self.canvas.height),
            fill=(0, 0, 0)  # Black background
        )

        for x, y, _, _, color in self.balls:
            self.canvas.draw.ellipse(
                (x - self.ball_radius, y - self.ball_radius, x + self.ball_radius, y + self.ball_radius),
                fill=color
            )


if __name__ == "__main__":
    run_sketch(WindowsScreensaverSketch, 800, 600, frame_limit=100)
