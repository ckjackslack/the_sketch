# The Sketch

**A Python creative-coding playground that grows with your imagination:** generative graphics, procedural geometry, animation, event-driven scenes, signal processing, agent swarms, and 2D physics. Use it as a library to design original work, or run built-in sketches from a simple CLI.

The reusable engine lives under `src/`. All runnable sketches live together under `src/examples/`. The project favors small composable mechanisms over monolithic artistic presets.

## Installation

Requires **Python 3.10+**. Pillow is the only runtime dependency.

```bash
git clone https://github.com/ckjackslack/the_sketch.git
cd the_sketch
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m src list
python -m src render celestial --width 700 --height 700 --frames 120 --fps 30 --seed 42 -o art/celestial.gif
```

A PNG output renders the **last frame**; a GIF output renders the full animation. Use `--save-frames art/frames` to retain full-resolution frame PNGs alongside a GIF. Use `--clear` only when you want the renderer to clear between frames (many presets already paint their own backgrounds).

## Gallery: ready-to-run presets

| Name | What it demonstrates |
|---|---|
| `abstract` | Animated random lines |
| `arkanoid` | Rotating triangular arrangements |
| `circles` | Rejection-based non-overlapping circles |
| `example` | Minimal Sketch subclass |
| `fancy` | Rotating concentric color forms |
| `matrix` | Falling typographic columns, bundled font |
| `rectangles` | Drifting randomized rectangles |
| `screensaver` | Classic bouncing balls |
| `celestial` | Radial spirals and polar geometry |
| `flow-field` | Noise-field streamlines |
| `choreography` | Time triggers, events, automated transitions |
| `signal-garden` | Time signals bound to object properties |
| `graph-mandala` | Evaluation graph driving rose-curve geometry |
| `flow-constellation` | Noise flow paths and blue-noise stars |
| `swarm` | Autonomous flocking agents and a predator |
| `elastic` | Constraint-based spring lattice in a vortex |

Try several at once:

```bash
python -m src render flow-field --frames 120 --seed 7 -o art/flow.gif
python -m src render graph-mandala --frames 150 --fps 30 -o art/mandala.gif
python -m src render choreography --frames 180 -o art/choreography.gif
python -m src render swarm --frames 180 -o art/swarm.gif
python -m src render elastic --frames 180 -o art/elastic.gif
python -m src render abstract --frames 1 -o art/still.png
```

## Architecture

```text
src/
  __main__.py          CLI
  sketch_gif.py         Canvas, Sketch lifecycle, frame and GIF/PNG renderer
  sketch.py             Earlier interactive Sketch prototype (legacy)
  creative.py           Geometry, curves, palettes, procedural fields, Painter, layers
  dynamics.py           Vec2, particles, spatial sampling, flow lines, oscillators
  events.py             Event, priority subscriptions, queue and EventBus
  scene.py              Node hierarchy, transforms, components and Scene
  automation.py         Scheduler, Tween, Condition and Director
  graph.py              Typed operator graph, references, parameters, JSON recipes
  signals.py            Continuous signals, envelopes, binding, looping
  world.py              Deterministic agent simulation, collisions and spatial indexing
  behaviors.py          Seek, flee, wander, separation, alignment, cohesion
  machines.py           Guarded finite-state machines
  physics.py            Spring systems, distance constraints and force fields
  examples/             All 16 runnable sketch presets and registry
  clacon2.ttf           Bundled typeface for the Matrix sketch
docs/                  Domain guides with focused examples
tests/                 Regression tests and CLI/preset smoke tests
```

Core primitives and simulations do not require a visible graphics window. `World` and `PhysicsWorld` are headless; Pillow is used for drawing and file output.

## Recipe 1 — Draw something original

```python
from PIL import Image
from src.creative import Painter, hsv, spiral, star

image = Image.new("RGB", (600, 600), (7, 9, 25))
p = Painter(image)
for i in range(20):
    p.path(spiral(300, 300, radius=15 + i*12, turns=3, phase=i*.25),
           hsv(i/20, .8, 1), width=2)
p.star(300, 300, 60, 24, tips=8, fill=(255, 230, 160))
image.save("spiral.png")
```

Primitives also include `polygon`, `rose`, `lissajous`, `hypotrochoid`, cubic `bezier`, `chaikin` smoothing, `rectangular_grid`, `polar_grid`, seeded `noise2`/`fbm`/`curl`, palettes, alpha layers, and `glow`.

## Recipe 2 — Compose layers

```python
from PIL import Image
from src.creative import layer, composite

background = Image.new("RGB", (400, 300), (5, 10, 30))
halo = layer((400, 300),
             lambda p: p.circle(200, 150, 80, fill=(255, 80, 160, 180)),
             opacity=.7)
composite(background, halo).save("layers.png")
```

## Recipe 3 — Animate a custom sketch

```python
from src.sketch_gif import Sketch, run_sketch

class Orbit(Sketch):
    def setup(self):
        self.x = 0

    def update(self):
        self.x = (self.x + 3) % self.canvas.width

    def draw(self):
        self.canvas.clear((8, 15, 32))
        self.canvas.draw.ellipse((self.x, 70, self.x+24, 94),
                              fill=(255, 180, 75))

run_sketch(Orbit, 420, 170, frame_limit=120, fps=30,
           seed=42, output="orbit.gif")
```

The lifecycle runs `setup()` once, then `update()` and `draw()` each frame. For custom pipelines use `render_frames()` instead of saving a GIF.

## Recipe 4 — Schedule effects and react to conditions

```python
from src.scene import Scene, Node
from src.automation import Director

scene = Scene()
director = Director()
scene.systems.append(director)
orb = scene.add(Node("orb", tags={"interactive"}, properties={"radius": 10}))

director.animate(orb, "transform.x", 300, duration=5)
director.scheduler.after(2, lambda: orb.set("properties.radius", 30))
director.when(lambda s: orb.transform.x >= 200,
              lambda s: s.emit("threshold_reached"), once=True)
scene.on("threshold_reached", lambda e: print("Crossed at", e.time))
scene.run(300, dt=1/60)
```

`Scene` contains a hierarchical `Node` tree and a priority-aware `EventBus`. The `Director` unifies timed tasks, interpolated property tweens, and edge-triggered conditions. Time is simulation time, not your computer's clock.

## Recipe 5 — Make a signal control an object

```python
from src.scene import Scene, Node
from src.signals import oscillate, envelope, bind

scene = Scene()
orb = scene.add(Node("orb"))
bind(scene, orb, "transform.x", oscillate(.2, amplitude=100, offset=200))
bind(scene, orb, "properties.radius", envelope([(0, 4), (2, 20), (4, 4)]))
scene.run(120, dt=1/60)
print(orb.transform.x, orb.properties["radius"])
```

Signals compose mathematically: `(oscillate(.5) * 20 + 100).at(t)`. Also available: `repeat` and `hold`.

## Recipe 6 — Build a data-flow effect graph

```python
import json
from src.graph import Graph, Ref, Param

graph = Graph()
wave = graph.add("wave", "sine", x=Param("angle"))
graph.add("level", "multiply", a=wave, b=0.5)
print(graph.evaluate("level", parameters={"angle": 1.57}))

recipe = json.dumps(graph.to_dict())
restored = Graph.from_dict(json.loads(recipe))
```

Graphs validate operators, input types, and dependencies. Recipes serialize **data**, not executable Python functions. Graph evaluation is a numeric data-flow mechanism, not yet a GPU/shader pipeline.

## Recipe 7 — Spawn an autonomous flock

```python
from src.world import World
from src.behaviors import separate, align, cohere, wander

world = World(800, 600, seed=42)
for _ in range(200):
    world.spawn(behaviors=[
        separate(16, 1.5),
        align(42, .65),
        cohere(60, .55),
        wander(.1),
    ])
world.run(300, dt=1/60)
print(world.agents[0].position)
```

The simulation uses deterministic seeded randomness and spatial hashing. Collisions emit events; they do not automatically resolve agent overlaps. For collision response, use the separate `PhysicsWorld`.

## Recipe 8 — Build a pendulum or elastic sculpture

```python
from src.physics import PhysicsWorld, Body, Vector, radial_force

world = PhysicsWorld(800, 600, gravity=Vector(0, 100))
anchor = world.add(Body(Vector(400, 50), pinned=True))
bob = world.add(Body(Vector(400, 180), radius=12))
world.connect(anchor, bob, length=130)
world.fields.append(radial_force(Vector(450, 300), strength=1000))
for _ in range(120):
    world.step(1/60)
```

You can connect bodies using `world.spring(...)` or `world.connect(...)`, configure restitution, and apply vortex fields. This is an exploratory constraint solver, not a production-precision rigid-body physics engine.

## Recipe 9 — Control particle emission

```python
from PIL import Image
from src.creative import Painter
from src.dynamics import ParticleSystem

particles = ParticleSystem(seed=42, gravity=(0, .15), drag=.98)
particles.emit(200, 150, count=70, speed=3, lifetime=40,
               radius=2, color=(255, 130, 70))
for _ in range(10):
    particles.update()
image = Image.new("RGB", (400, 300), (5, 7, 18))
particles.draw(Painter(image))
image.save("particles.png")
```

## Tests and development

```bash
python -m pip install pytest
python -m pytest -q
python -m src list
```

GitHub Actions tests supported Python versions from 3.10 through 3.13. New examples should be registered in `src/examples/__init__.py` and tested with a single-frame smoke render. Put new reusable functionality into an engine module—not an example.

### Detailed guides

- [Creative primitives](docs/CREATIVE.md)
- [Scene and event orchestration](docs/ORCHESTRATION.md)
- [Effect graphs and signals](docs/COMPOSITION.md)
- [Emergent simulations](docs/EMERGENT.md)
- [Physics constraints](docs/PHYSICS.md)

## Limitations and roadmap

GIF rendering currently collects frame data before encoding, so large projects may use substantial memory. Agent collision detection and physics constraints favor clarity over performance; full fluid/soft-body solvers and real-time editor functionality are future work. Planned enhancements include interactive parameter controls, effect graph visualization, scene persistence, fast spatial collision broadphases, audio-reactive artwork, and export beyond Pillow.

## License

See [LICENSE](LICENSE).
