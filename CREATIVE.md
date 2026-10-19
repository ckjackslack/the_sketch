# Creative primitives

The creative toolkit adds reusable functions rather than requiring a subclass for every visual idea.

## Domains

| Domain | API |
| --- | --- |
| Math & easing | `lerp`, `remap`, `clamp`, `smoothstep`, `ease_in_out`, `pingpong` |
| Color | `hsv`, `mix_color`, `gradient` |
| Geometry | `point_on_circle`, `rotate`, `polygon`, `star`, `spiral`, `rose`, `lissajous`, `hypotrochoid`, `bezier`, `chaikin` |
| Layout & randomness | `polar_grid`, `rectangular_grid`, `random_walk`, `poisson_disc` |
| Procedural fields | `noise2`, `fbm`, `curl`, `flow_lines` |
| Drawing | `Painter.line/shape/circle/ellipse/rect/regular_polygon/star/path/arc/text` |
| Compositing | `layer`, `composite`, `glow` |
| Motion & simulation | `Vec2`, `Particle`, `ParticleSystem`, `oscillator` |

## Procedural composition

```python
from PIL import Image
from src.creative import Painter, hsv, star, spiral, layer, composite
from src.dynamics import poisson_disc

base=Image.new("RGB",(800,800),(6,8,25))
p=Painter(base)
for x,y in poisson_disc(800,800,35,seed=12):
    p.circle(x,y,2,fill=(120,150,210))
for i in range(18):
    p.path(spiral(400,400,turns=3,radius=18+i*17,phase=i*.25),
           hsv(i/18,.8,1),width=2)
overlay=layer((800,800),lambda draw:draw.star(400,400,150,65,9,
                                            fill=(255,225,150,255)),opacity=.5)
composite(base,overlay).convert("RGB").save("composition.png")
```

## Animated presets

```python
from src.sketch_gif import run_sketch
from src.compositions import CelestialSketch, FlowFieldSketch
run_sketch(CelestialSketch,600,600,frame_limit=120,fps=30,
           output="celestial.gif",seed=5)
run_sketch(FlowFieldSketch,900,600,frame_limit=90,
           output="flow.gif")
```

All blue-noise, particle, and walk generators accept explicit seeds. `noise2` and `fbm` are deterministic without mutable global RNG. Layers are RGBA and can be composited onto RGB canvases. Algorithms are pure Python and intended for moderate resolutions; choose samples and steps with care.
