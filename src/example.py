from sketch_gif import Sketch, run_sketch


# Example usage:
class MySketch(Sketch):
    def draw(self):
        # Draw on the canvas
        self.canvas.draw.rectangle((10, 10, 100, 100), fill=(255, 0, 0))


if __name__ == "__main__":
    run_sketch(MySketch, 800, 600, frame_limit=50)
