"""Command-line interface: python -m src list | render PRESET."""
import argparse
from pathlib import Path
from .sketch_gif import run_sketch
from .examples import PRESETS, load_preset

def main(argv=None):
    parser = argparse.ArgumentParser(description="The Sketch — generative art toolkit")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("list", help="Display available examples")
    render = commands.add_parser("render", help="Render an example as GIF or PNG")
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
    result = run_sketch(load_preset(args.sketch), args.width, args.height,
                        frame_limit=args.frames, fps=args.fps, output=args.output,
                        seed=args.seed, save_frames=args.save_frames,
                        clear_each_frame=args.clear)
    print(f"Rendered {args.sketch} to {result}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
