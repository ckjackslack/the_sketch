# Emergent Worlds

A headless, stdlib-only agent simulation that works independently of Pillow.

```python
from src.world import World
from src.behaviors import separate, align, cohere, wander
world=World(800,600,seed=42)
for _ in range(200):
    world.spawn(behaviors=[separate(16),align(42),cohere(60),wander(.1)])
world.run(300,dt=1/60)
```

Includes `Vector`, `Agent`, `World`, `SpatialHash`, six composable steering behaviors and `StateMachine` with guarded prioritized transitions and enter/exit hooks.

Run the demo:

```bash
python -m src render swarm --frames 180 --fps 30 -o swarm.gif
python -m pytest -q
```

Simulation steps are deterministic for fixed seed, agent insertion order and timestep. Avoid shared random number generators between worlds. For now, collisions emit events but do not resolve overlapping geometry. Spatial neighbor forces are based on the same-frame snapshot. Boundaries support wrap, bounce or none.

Next extensions: collision resolution, spring constraints, continuous collision detection, spatial index instrumentation, render-time decoupling, reaction-diffusion and agent behavior trees.
