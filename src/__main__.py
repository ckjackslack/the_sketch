"""Run with python -m src list or python -m src render NAME."""
import argparse
import importlib
import sys
from pathlib import Path
from .sketch_gif import run_sketch

# Legacy effects use absolute sibling imports; preserve their entry points.
sys.path.insert(0, str(Path(__file__).resolve().parent))
PRESETS = {
    "abstract": ("abstract", "AbstractLineSketch"),
    "arkanoid": ("arkanoid", "ArkanoidSketch"),
    "circles": ("circles", "CirclesSketch"),
    "example": ("example", "MySketch"),
    "fancy": ("fancy", "FancySketch"),
    "matrix": ("matrix", "MatrixSketch"),
    "rectangles": ("rectangles", "RectanglesSketch"),
    "screensaver": ("old_screensaver", "WindowsScreensaverSketch"),
    "celestial": ("src.compositions", "CelestialSketch"),
    "flow-field": ("src.compositions", "FlowFieldSketch"),
    "choreography": ("src.choreography", "ChoreographySketch"),
    "signal-garden": ("src.showcases", "SignalGardenSketch"),
    "graph-mandala": ("src.showcases", "GraphMandalaSketch"),
    "flow-constellation": ("src.showcases", "FlowConstellationSketch"),
    "swarm": ("src.swarm", "SwarmSketch"),
}

def main(argv=None):
    parser = argparse.ArgumentParser(description="Procedural art renderer")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("list", help="List built-in sketch presets")
    render = sub.add_parser("render", help="Render a preset")
    render.add_argument("sketch", choices=sorted(PRESETS))
    render.add_argument("-o", "--output", default="output.gif")
    render.add_argument("--width", type=int, default=800)
    render.add_argument("--height", type=int, default=600)
    render.add_argument("--frames", type=int, default=100)
    render.add_argument("--fps", type=int, default=30)
    render.add_argument("--seed", type=int)
    render.add_argument("--save-frames", type=Path)
    render.add_argument("--clear", action="store_true")
    args = parser.parse_args(argv)
    if args.command == "list":
        print("\n".join(sorted(PRESETS)))
        return 0
    module_name, class_name = PRESETS[args.sketch]
    sketch = getattr(importlib.import_module(module_name), class_name)
    path = run_sketch(sketch, args.width, args.height, frame_limit=args.frames,
                      fps=args.fps, output=args.output, seed=args.seed,
                      save_frames=args.save_frames, clear_each_frame=args.clear)
    print(f"Rendered {args.sketch} to {path}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
