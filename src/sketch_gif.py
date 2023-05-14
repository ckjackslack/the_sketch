import os
import random

from PIL import Image, ImageDraw


class Canvas:
    def __init__(self, width, height, background_color=(255, 255, 255)):
        self.width = width
        self.height = height
        self.image = Image.new("RGB", (width, height), background_color)
        self.draw = ImageDraw.Draw(self.image)

    def save(self, filename):
        self.image.save(filename)

    def get_image(self):
        return self.image.copy()


class Sketch:
    def __init__(self, canvas):
        self.canvas = canvas

    def setup(self):
        pass

    def update(self):
        pass

    def draw(self):
        pass


def run_sketch(
    sketch,
    width,
    height,
    background_color=(255, 255, 255),
    frame_limit=100,
    fps=60,
):
    temp_folder = "temp"
    os.makedirs(temp_folder, exist_ok=True)

    canvas = Canvas(width, height, background_color)
    sketch_instance = sketch(canvas)
    sketch_instance.setup()

    frame_count = 0
    images = []

    while frame_count < frame_limit:
        sketch_instance.update()
        sketch_instance.draw()
        frame_count += 1
        image_copy = canvas.get_image()
        images.append(image_copy)

    # Save individual frames
    for i, image in enumerate(images):
        filename = os.path.join(temp_folder, f"frame_{i}.png")
        image.save(filename)

    # Create GIF from frames
    gif_filename = "output.gif"
    images[0].save(
        gif_filename,
        save_all=True,
        append_images=images[1:],
        duration=1000/fps,  # milliseconds between frames
        loop=0  # loop forever
    )

    print(f"GIF created: {gif_filename}")

    # Clean up intermediate frames
    for filename in os.listdir(temp_folder):
        file_path = os.path.join(temp_folder, filename)
        os.remove(file_path)

    os.rmdir(temp_folder)