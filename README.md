# The Sketch

A small Python **generative art and animation engine** built on Pillow. Includes a sketch lifecycle, deterministic seeds, GIF/PNG renderer, frame export, built-in effects, and a command-line interface.

## Quickstart

```bash
python -m pip install -r requirements.txt
python -m src list
python -m src render fancy --frames 120 --fps 30 --seed 42 -o art/fancy.gif
python -m src render circles --frames 80 -o art/circles.gif
python -m src render abstract --frames 1 -o art/still.png
python -m src render rectangles --frames 30 --save-frames art/frames -o art/rectangles.gif
python -m pip install pytest
python -m pytest -q
```

Built-in presets: `abstract`, `arkanoid`, `circles`, `example`, `fancy`, `matrix`, `rectangles`, `screensaver`.

## Programmatic API

```python
from src.sketch_gif import Sketch, run_sketch

class Orbit(Sketch):
    def setup(self):
        self.x = 0

    def update(self):
        self.x += 3

    def draw(self):
        self.canvas.clear((9, 12, 30))
        self.canvas.draw.ellipse((self.x, 40, self.x + 30, 70), fill=(255, 180, 40))

run_sketch(Orbit, 400, 200, frame_limit=100, fps=30,
           output="art/orbit.gif", seed=123)
```

The lifecycle is `setup()` once, then `update()` followed by `draw()` for each frame. The `Canvas` provides `width`, `height`, `image`, `draw`, `clear()`, `get_image()`, and `save()`. Use `render_frames()` to consume frames directly in custom pipelines. PNG output saves the final frame. `--clear` clears before each frame; by default frames may accumulate drawing. Seeding controls Python's `random` module, not third-party RNGs.

## Architecture

- `src/sketch_gif.py` — rendering engine, legacy-compatible API
- `src/__main__.py` — CLI and preset registry
- `src/*.py` — procedural art examples
- `tests/` — regression tests
- `.github/workflows/` — CI

## Next directions

Composite layers, transitions, keyframe timelines, particle systems, palettes, advanced noise fields, SVG export, parameter sweeps, and interactive galleries.

## License

See [LICENSE](LICENSE).
