import random
import pytest
from PIL import Image
from src.sketch_gif import Canvas, Sketch, render_frames, run_sketch

class Noise(Sketch):
    def draw(self):
        self.canvas.draw.point((0, 0), fill=(random.randrange(256), 0, 0))

def test_canvas_dimensions():
    with pytest.raises(ValueError):
        Canvas(0, 10)

def test_canvas_copy():
    canvas = Canvas(4, 4)
    image = canvas.get_image()
    image.putpixel((0, 0), (0, 0, 0))
    assert canvas.get_image().getpixel((0, 0)) == (255, 255, 255)

def test_seed_and_random_state():
    state = random.getstate()
    a = [im.tobytes() for im in render_frames(Noise, 5, 5, frame_limit=4, seed=7)]
    b = [im.tobytes() for im in render_frames(Noise, 5, 5, frame_limit=4, seed=7)]
    assert a == b
    assert random.getstate() == state

def test_gif_and_frame_export(tmp_path):
    output = tmp_path / "nested" / "animation.gif"
    directory = tmp_path / "frames"
    assert run_sketch(Noise, 16, 12, frame_limit=4, output=output,
                      seed=42, save_frames=directory) == output
    with Image.open(output) as image:
        assert image.size == (16, 12)
        assert image.n_frames >= 1
    assert len(list(directory.glob("frame_*.png"))) == 4

def test_png(tmp_path):
    path = tmp_path / "still.png"
    run_sketch(Noise, 8, 8, frame_limit=3, output=path, seed=1)
    with Image.open(path) as image:
        assert image.size == (8, 8)

@pytest.mark.parametrize("kwargs", [{"frame_limit": 0}, {"fps": 0}, {"fps": 1001}])
def test_bad_options(tmp_path, kwargs):
    with pytest.raises(ValueError):
        run_sketch(Noise, 10, 10, output=tmp_path / "out.gif", **kwargs)

def test_unsupported_output(tmp_path):
    with pytest.raises(ValueError):
        run_sketch(Noise, 5, 5, output=tmp_path / "out.mov")
