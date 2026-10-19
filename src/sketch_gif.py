"""Pillow sketch lifecycle and deterministic GIF/PNG rendering."""
from __future__ import annotations
import random
from pathlib import Path
from tempfile import TemporaryDirectory
from PIL import Image, ImageDraw

class Canvas:
    def __init__(self, width, height, background_color=(255, 255, 255)):
        if width <= 0 or height <= 0:
            raise ValueError("Canvas dimensions must be positive")
        self.width, self.height = width, height
        self.background_color = background_color
        self.image = Image.new("RGB", (width, height), background_color)
        self.draw = ImageDraw.Draw(self.image)

    def clear(self, color=None):
        self.draw.rectangle((0, 0, self.width, self.height), fill=self.background_color if color is None else color)

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

def render_frames(sketch, width, height, *, background_color=(255, 255, 255),
                  frame_limit=100, seed=None, clear_each_frame=False):
    """Yield independent frames; random state is restored when exhausted or closed."""
    if frame_limit < 1:
        raise ValueError("frame_limit must be positive")
    state = random.getstate()
    try:
        if seed is not None:
            random.seed(seed)
        canvas = Canvas(width, height, background_color)
        instance = sketch(canvas)
        instance.setup()
        for _ in range(frame_limit):
            if clear_each_frame:
                canvas.clear()
            instance.update()
            instance.draw()
            yield canvas.get_image()
    finally:
        random.setstate(state)

def run_sketch(sketch, width, height, background_color=(255, 255, 255),
               frame_limit=100, fps=60, output="output.gif", seed=None,
               save_frames=None, clear_each_frame=False):
    """Render a looping GIF or the final frame as PNG, returning the output path."""
    if not 1 <= fps <= 1000:
        raise ValueError("fps must be in the range 1..1000")
    if frame_limit < 1:
        raise ValueError("frame_limit must be positive")
    path = Path(output)
    if path.suffix.lower() not in (".gif", ".png"):
        raise ValueError("output must have .gif or .png extension")
    path.parent.mkdir(parents=True, exist_ok=True)
    if save_frames is not None:
        Path(save_frames).mkdir(parents=True, exist_ok=True)
    frames = render_frames(sketch, width, height, background_color=background_color,
                           frame_limit=frame_limit, seed=seed,
                           clear_each_frame=clear_each_frame)
    if path.suffix.lower() == ".png":
        try:
            for frame in frames:
                pass
            frame.save(path)
        finally:
            frames.close()
        return path
    with TemporaryDirectory(prefix="the-sketch-") as temp:
        files = []
        for i, frame in enumerate(frames):
            name = Path(temp) / f"{i:06d}.png"
            frame.quantize(colors=256).save(name)
            files.append(name)
            if save_frames is not None:
                frame.save(Path(save_frames) / f"frame_{i:06d}.png")
        opened = [Image.open(name) for name in files]
        try:
            opened[0].save(path, save_all=True, append_images=opened[1:],
                           duration=max(1, round(1000 / fps)), loop=0,
                           optimize=False, disposal=2)
        finally:
            for image in opened:
                image.close()
    return path
